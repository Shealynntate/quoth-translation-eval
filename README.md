# Quoth translation eval

Measures whether a language model translates exactly the words a reader selected, and nothing
else.

[Quoth](https://lectura-323fd.web.app) is an iOS app for reading books in Spanish. Tap a word or
drag across a phrase and it shows the English for that selection, written by Claude. That short
English is called a gloss. This repository is the evaluation harness behind the feature. It
holds:

- the app's real system prompt, tool schema and request format, in `prompt/`
- 35 test sentences from public-domain books, in `cases/`
- the recorded results of two experiments, every trial included, in `results/`
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

Each table gives two counts. **Scored** is what the substring checks said. **After review** is
the count once every passing answer had been read against its sentence (see
[What the checks miss](#what-the-checks-miss)).

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
  answered "cold" and "after" every time.
- **In the app**, a selection of more than one word goes to Sonnet and a single word goes to
  Haiku. So the two single-word failures above are the ones a reader can still meet.

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

- **A rule alone did worse than saying nothing.** 15% against 23%.
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

### What the checks miss

Scoring is by substring, so an answer can fail in a way its check did not name and still pass.
Every passing answer was read against its sentence in a second pass. That pass found 20 of them
breaking the rule, listed one by one in [results/REVIEW.md](results/REVIEW.md).

- **One-sided checks.** A check that only asks for "however" passes an answer that is only
  "however", with the rest of the selection dropped.
- **Unlisted synonyms.** A check that excludes "caught" passes "having taken".
- **The review moved every gap in the same direction.** The weaker arms lost more passes than
  the stronger ones, so the scored tables understate the differences.

The checks were not edited after the answers were seen. The scored counts are what the
published checks give.

## How it works

**The request is the app's.** `prompt/` holds the system prompt, the tool schema and the three
clauses the app adds to a user turn. The request builder's output is pinned in the tests to the text the
app sends, byte for byte, and nothing is added to the call: no temperature, no caching, no extra instruction.

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
its case had been seen.

**No model scores anything.** A model judge would bring its own error rate into every number.
Substring checks are crude and their misses are easy to see, which is why the review above can
list them.

**The spend ceiling refuses a call before it is sent.** Each call reserves its worst-case cost
first. If that would cross the ceiling, the call never leaves. A live run does not start
without a ceiling.

**Every trial is kept.** `trials.jsonl` holds one row per request: the user turn as sent, the
answer as returned, the checks it failed, tokens and cost. `replay` re-scores a recorded run
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

## Limits

- **It is small.** 35 sentences and 5 trials per cell. A difference of a few trials between two
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
- **The prompt is a snapshot** of what the app sent on 2026-09-29.

## Sources and license

The case sentences are quoted from five Spanish translations in the public domain. Titles,
translators, editions and the basis for each are in [cases/SOURCES.md](cases/SOURCES.md).

The system prompt's own examples include two short phrases from a novel that is still in
copyright.

The code is released under the MIT license. See [LICENSE](LICENSE).
