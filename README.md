# Quoth translation eval

Measures whether a language model translates exactly the words a reader selected, and nothing
else.

[Quoth](https://lectura-323fd.web.app) is an iOS app for reading books in Spanish. Tap a word or
drag across a phrase and it shows the English for that selection, written by Claude. That short
English is called a gloss. This repository is the evaluation harness behind the feature. It
holds:

- the app's real system prompt, tool schema and request format, in `prompt/`
- 65 test sentences from public-domain books, in `cases/`
- the recorded results of three experiments, every trial included, in `results/`
- a small Python package that builds the requests, scores the answers and caps the spend

## The rule under test

The English must stand in for exactly the selected words. There are two ways to break it.

| Failure | Selection | In the sentence | Answer |
|---|---|---|---|
| **Drop**: something inside the selection is left out | como el mejor, señor Holmes | Sé aguantar las bromas como el mejor, señor Holmes, pero esta vez... | "as well as anyone" |
| **Absorb**: meaning from outside the selection is pulled in | se puso un delantal | ...se puso un delantal de plata y dio comienzo a su tarea. | "put on a silver apron" |

Both answers are fluent, and both are wrong for a reader who wants to know what the selected
words mean.

The same request can pass on one try and fail on the next. So every result here is a pass
rate over repeated trials, never a single observation.

## Findings

The tables of experiments 1 and 2 give two counts. **Scored** is what the substring checks said.
**After review** is the count once every passing answer had been read against its sentence (see
[What the checks miss](#what-the-checks-miss)). The table of experiment 3 gives its counts under
one check as first written and as amended, for the reason given in the same section.

### 1. Marking the selection in place

The app sends the selection and the sentence it sits in. The two arms differ in one thing:
whether the sentence shows where the selection is.

```
Translate this Spanish text into English: “se puso un delantal”
It appears in this sentence: “Limpióse el rostro, las manos y los brazos; «se puso un delantal» de plata y dio comienzo a su tarea.”
```

That is the marked arm. The unmarked arm sends the same two lines without the « ».

19 sentences, 5 trials per sentence and arm.

| Model | Arm | Scored | After review |
|---|---|---:|---:|
| Haiku 4.5 | unmarked | 62/95 (65%) | 54/95 (57%) |
| Haiku 4.5 | marked | 86/95 (91%) | 84/95 (88%) |
| Sonnet 5 | unmarked | 95/95 (100%) | 95/95 (100%) |
| Sonnet 5 | marked | 95/95 (100%) | 95/95 (100%) |

- **On Haiku the marks are worth 26 points as scored and 31 after review.** Four sentences
  went from 0 or 1 passes in 5 to 5 in 5, among them both rows of the table above.
- **Sonnet passed every trial with or without them.** On this set the marks buy nothing on the
  stronger model.
- **One kind of failure the marks do not touch.** A single word inside a fixed phrase takes the
  phrase's meaning. "fría" in "a sangre fría" came back "cold blood" or "cold-blooded" in all 10
  Haiku trials. "tras" in "uno tras otro" came back as the whole phrase in all 10. Sonnet
  answered "cold" and "after" every time. [Experiment 3](#3-a-single-word-inside-a-fixed-phrase)
  takes this failure up.
- **In the app**, a selection of more than one word goes to Sonnet and a single word goes to
  Haiku. So the two single-word failures above are the ones a reader can still meet. Experiment 3
  measures five clauses against them on Haiku, over sixteen such words.

### 2. Where guidance should live

The failure: in "Nadie podía haberlo sabido", the selection "haberlo" is the auxiliary with a
pronoun attached, and the participle "sabido" is outside it. The model answers "have known
it".

Five arms, each adding one thing to the one before. 16 sentences, 5 trials per sentence and
arm, all on Haiku 4.5, which is the model that serves a single-word tap.

| Arm | What the model is given | Scored | After review |
|---|---|---:|---:|
| no-guidance | the system prompt with its two sentences on attached pronouns removed | 18/80 (23%) | 14/80 (18%) |
| rule | the rule sentence alone | 12/80 (15%) | 7/80 (9%) |
| rule+example | the rule and one worked example | 36/80 (45%) | 35/80 (44%) |
| second-example | the above and a second worked example | 50/80 (63%) | 50/80 (63%) |
| turn-clause | the rule and one example, and a clause in the request itself | 76/80 (95%) | 76/80 (95%) |

- **A rule alone did no better than saying nothing, and may have done worse.** 15% against
  23%, a gap of six trials in eighty.
- **A worked example taught its own string and its near neighbours.** The example in the prompt
  is "haberla". With it, "haberlos" and "habiéndolo" passed 5 in 5, while three reflexive
  sentences ("haberse repuesto", "habiéndose puesto", "haberme quejado") stayed at 0 in 5.
- **The form of the example carried further than its point.** On "haberle desobedecido" the
  model copied the example's ellipsis and kept the participle: "having … disobeyed him".
- **A second example repeated the pattern.** It names "haberle". The forms close to it
  improved, and five reflexive sentences stayed at 0 or 1 in 5.
- **The clause in the request reached every form.** It is sent only when the selected word is
  haber with a pronoun attached, so no other lookup changes by a single byte. This is what the
  app's code now sends.
- **Its 4 failures are all reflexive** ("having … complained", "having … recovered"), where
  English has no pronoun to put after the ellipsis.
- **Some of its passes are thin.** "having …" with the pronoun missing, and "having … oneself",
  pass the checks and absorb nothing. They are not glosses to be proud of.

### 3. A single word inside a fixed phrase

The failure: a tap on one word inside a fixed phrase comes back with the phrase's meaning. In
"A sangre fría ha violado la santidad de un corazón humano", the selection "fría" came back "cold
blood" 3 times in 5 and "cold-blooded" once, on the request as it stood. The word alone means
"cold".

Six arms. Each clause is sent as the second line of the user turn, and only when the selection is
one plain word: one word by the app's word rule, and neither haber with a pronoun attached nor a
pronoun-plus-verb span, which carry their own clauses.

| Arm | The clause |
|---|---|
| no-clause | none: the request as experiments 1 and 2 sent it |
| own-meaning+exception | translate the word alone and report its phrase separately, with one worked example ("larga" in "a la larga" is "long"), and the exception: a word with no meaning outside its phrase ("balde" in "en balde") takes the phrase's meaning |
| own-meaning | the same without the exception |
| words-outside | the words around the selection are outside it and stay out of the translation, even when they form a fixed phrase with it, with the same worked example |
| three-examples | own-meaning with two more worked examples, a noun ("pelo" in "le tomó el pelo") and a verb ("metió" in "metió la pata") |
| adverb-examples | words-outside with two examples of a preposition and one word that make an adverb ("de prisa", "por último"), the exception, and a demand that the phrase be reported |

No case repeats a clause's own worked example, and the harness refuses to run one that does. The
first five arms ran as one round. The sixth was written after that round's answers had been read,
and ran as a second round the same day.

30 sentences, 5 trials per sentence and arm, all on Haiku 4.5, in three groups:

- **Phrase words**, 16: a word with a sense of its own inside a fixed phrase, such as "fría" in
  "a sangre fría" or "nuevo" in "de nuevo". The phrase's meaning is the failure.
- **Exceptions**, 6: a word with no sense outside its phrase, such as "embargo" in "sin
  embargo". The phrase's meaning is the right answer, as the system prompt says.
- **Plain words**, 8: words in no fixed phrase.

**The bar was set before any answer was seen.** An arm would ship if it passed at least 68 of the
80 phrase-word trials and left no phrase word under 2 passes in 5, while harming nothing else: the
exceptions and the plain words within two trials of the control, the phrase still reported about
as often, and none of the app's own regression sentences two trials worse.

| Arm | Phrase words, as first scored | Phrase words, amended check | Exceptions | Plain words | Phrase words reporting the phrase |
|---|---:|---:|---:|---:|---:|
| no-clause | 32/80 | 35/80 (44%) | 30/30 | 40/40 | 22/80 |
| own-meaning+exception | 47/80 | 52/80 (65%) | 30/30 | 40/40 | 20/80 |
| own-meaning | 46/80 | 50/80 (63%) | 29/30 | 40/40 | 18/80 |
| words-outside | 55/80 | 60/80 (75%) | 30/30 | 40/40 | 22/80 |
| three-examples | 42/80 | 46/80 (58%) | 30/30 | 40/40 | 21/80 |
| adverb-examples | 46/80 | 46/80 (58%) | 29/30 | 40/40 | 33/80 |

The two phrase-word columns differ by one check, amended after the first round and before the
second, which was scored under the amended check from the start (see
[What the checks miss](#what-the-checks-miss)).

- **No arm cleared the bar.** The best, words-outside, reached 60 of 80 under the amended check
  and left four phrase words at 0 in 5.
- **words-outside lifts the phrase words from 35 to 60 of 80 and harms nothing.** The exceptions
  stay at 30 of 30 and the plain words at 40 of 40. Twelve phrase words reach 5 in 5 under it,
  eleven as first scored.
- **A preposition and one word that make an adverb does not move.** "de nuevo", "por completo",
  "de pie" and "por fin" passed 1 trial in 120 across the six arms. "nuevo" came back "again",
  "completo" "completely" and "pie" "standing" in all 30 of their trials.
- **More examples did worse than one.** three-examples scored 46 against own-meaning's 50. The
  longer adverb-examples, which also required the phrase to be reported, scored 46 against
  words-outside's 60, and lost "fría" outright: "cold" in 5 of 5 under words-outside, "cold
  blood" in 5 of 5 under adverb-examples.
- **Asking for the phrase seems to pull the translation toward it.** Every adverb-examples failure
  on "fría" and "fin" reports the phrase, and gives the phrase's meaning as the translation.
- **The phrase is reported in about a quarter of phrase-word answers, clause or no clause.** 18
  to 22 of 80 in the first round. The clause that demanded it raised that to 33. Once the
  translation is the word's own meaning, the reported phrase is the only way the phrase's sense
  reaches the reader.
- **The exceptions and the plain words were never at risk.** The two exception failures are a
  sense miss ("on tiptoe" for "a hurtadillas") and one empty answer.
- **What happened next.** The app sends the words-outside clause from version 1.0.1, as a partial
  fix, knowing it missed the bar.
- **On the app's own regression sentences**, which are not published here, the clause took one
  case from 0 to 4 passes in 5 and cost another case two of its five.

### What the checks miss

Scoring is by substring, so an answer can fail in a way its check did not name and still pass.
Every passing answer of experiments 1 and 2 was read against its sentence in a second pass. That
pass found 20 of them breaking the rule, listed one by one in [results/REVIEW.md](results/REVIEW.md).

- **One-sided checks.** A check that only asks for "however" passes an answer that is only
  "however", with the rest of the selection dropped.
- **Unlisted synonyms.** A check that excludes "caught" passes "having taken".
- **The review moved every gap in the same direction.** The weaker arms lost more passes than
  the stronger ones, so the scored tables understate the differences.

The checks of experiments 1 and 2 were not edited after the answers were seen. Their scored
counts are what the published checks give.

**One check in experiment 3 was amended**, after the first round had been scored and before the
second round was run. The case `hizo-hizo-caso` selects "hizo" in "no la hizo caso" (paid her no
attention), and its check excluded "paid" as the phrase leaking in. But in "paid her no
attention", "paid" is the word standing where "hizo" stands, which is what a substitutable gloss
is. So "paid" and "pay" moved from the exclusions to the accepted answers, and "attention" and
"heed" still fail. The case file keeps the check as first written, under `amended`, and every row
of the run keeps the verdict it first got, so both counts rebuild from the published files. On
the phrase words, as first scored: no-clause 32, own-meaning+exception 47, own-meaning 46,
words-outside 55, three-examples 42. Amended: 35, 52, 50, 60, 46. adverb-examples, run after
the amendment, scored 46. No arm clears the bar either way.

The answers of experiment 3 were also read one by one by a model, and that reading is where the
amendment came from. It was not a pass-by-pass review like the one in REVIEW.md, so experiment
3's table gives scored counts only.

## How it works

**The request is the app's.** `prompt/` holds the system prompt, the tool schema and the four
lines the app can add to a user turn:

| File | Sent when | In which experiments |
|---|---|---|
| `clitic_turn.txt` | the selection is a pronoun and a verb, as in "le dio" | all three |
| `haber_turn.txt` | the selection is haber with a pronoun attached, as in "haberlo" | all three, except the guidance arms that measure without it |
| `single_word_turn.txt` | the selection is any other single word | experiment 3, as the words-outside arm; the app sends it from version 1.0.1 |
| `earlier_turn.txt` | the selection is a single word; it carries the passage before the sentence | all three |

`prompt/phrase_clauses/` holds the five clauses experiment 3 compared, one file per arm. The
request builder's output is pinned in the tests to the text the app sends, byte for byte, and
nothing is added to the call: no temperature, no caching, no extra instruction.

**Experiment 3 was sent by the app's own harness**, not by this package. Its 900 recorded user
turns are rebuilt by this package from `cases/phrases.json` in `tests/test_phrases_record.py`,
and each one matches byte for byte, as do the system prompt and the tool schema that were sent.

**A case** is a sentence, a selection and its checks.

```json
{
  "id": "delantal-absorb-plata",
  "selection": "se puso un delantal",
  "sentence": "Limpióse el rostro, las manos y los brazos; se puso un delantal de plata y dio comienzo a su tarea.",
  "mustExclude": ["silver"],
  "note": "Cuentos de hadas (Charles Perrault). Absorb: the completing phrase just past the span."
}
```

| Check | Passes when |
|---|---|
| `mustInclude` | every entry appears in the answer |
| `mustIncludeAny` | at least one entry appears |
| `mustExclude` | no entry appears |
| `mustNotBe` | the whole answer is not this string |

Matching is case-insensitive and by substring. Every check was written before any answer to
its case had been seen. One was amended later, as described above, and keeps its first form.

**No model scores anything.** A model judge would bring its own error rate into every number.
Substring checks are crude and their misses are easy to see, which is why the review above can
list them.

**The spend ceiling refuses a call before it is sent.** Each call reserves its worst-case cost
first. If that would cross the ceiling, the call never leaves. A live run does not start
without a ceiling.

**Every trial is kept.** `trials.jsonl` holds one row per request: the user turn as sent, the
answer as returned, the checks it failed, tokens and cost. A row of experiment 3 also keeps the
phrase the model reported and the verdict the row first got. `replay` re-scores a recorded run
offline and lists every row whose verdict would change, so an edited check cannot quietly move
a published number.

## Run it

Python 3.11 or later.

```bash
pip install -e ".[dev]"
python -m pytest
python -m gloss_eval validate
```

See exactly what a run would send and what it could cost, without sending anything:

```bash
python -m gloss_eval guidance --cases cases/haber.json --model haiku --trials 5 --dry-run
python -m gloss_eval phrases --cases cases/phrases.json --model haiku --trials 5 --dry-run
```

Run an experiment. Put `ANTHROPIC_API_KEY` in the environment or in a `.env` file first.

```bash
python -m gloss_eval marks --cases cases/marks.json --model haiku --trials 5 --max-usd 0.90 --out results/my-run
```

Re-score a recorded run without spending anything:

```bash
python -m gloss_eval replay results/2026-09-29-marks-haiku
```

What the published runs cost, on 2026-09-29:

| Run | Requests | Cost | Ceiling |
|---|---:|---:|---:|
| marks, Haiku 4.5 | 190 | $0.58 | $0.90 |
| marks, Sonnet 5 | 190 | $1.45 | $1.90 |
| guidance, Haiku 4.5 | 400 | $1.32 | $1.90 |
| phrases, Haiku 4.5 | 900 | $2.90 | $3.50 |

The phrases run went in two rounds, 750 requests then 150, under one ceiling that also covered
150 requests ($0.48) on the app's own regression sentences, which are not published here.

## Limits

- **It is small.** 65 sentences and 5 trials per cell. A difference of a few trials between two
  arms is noise.
- **One language pair and one register.** Spanish to English, in literary prose from
  translations made between 1879 and 1929.
- **The marks cases were chosen by shape.** Each was picked because its selection cuts a
  sentence in a way that invites a drop or an absorb, not because it had failed. Cases promoted
  from observed failures would score lower.
- **Whom the pronoun names is untested.** Every "le" in `cases/haber.json` refers to a man, and
  the shipped clause's example says "him". Whether it says "him" of a woman is not measured
  here.
- **Two models.** The request forces a tool call. Haiku 4.5 and Sonnet 5 accept that. Sonnet 5.5
  and Opus 5.5 reject it, so they cannot be measured with this request as it stands.
- **The request has moved on.** Experiments 1 and 2 were run against the request as the app sent
  it before the single-word clause. Experiment 3 measured that clause, and the app sends it from
  version 1.0.1.
- **Two marks cases carry a longer sentence than the app would send.** The app ends a sentence at
  every period, including the one in an abbreviation ("Vd.") or an ellipsis ("Watson..."). So
  `a-punto-de-absorb-verb` and `fria-sangre-fria-absorb` show the model more context than a
  reader's tap would.

## Sources and license

The case sentences are quoted from five Spanish translations in the public domain. Titles,
translators, editions and the basis for each are in [cases/SOURCES.md](cases/SOURCES.md).

The system prompt's own examples include two short phrases from a novel that is still in
copyright.

The code is released under the MIT license. See [LICENSE](LICENSE).

Built with [Claude Code](https://claude.com/claude-code).
