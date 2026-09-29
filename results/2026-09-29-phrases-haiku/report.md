# Gloss eval report

## Run

- Experiment: phrases
- Model: `claude-haiku-4-5-20251001`
- Cases: `cases/phrases.json` (sha256 `23874cea7817`)
- Trials per case and arm: 5
- Started: not recorded; finished: 2026-09-29T22:11:23+00:00 (UTC)
- Cost: $2.9042 (ceiling $3.50, $0.0000 already spent against it before this run)
- Measured by: the app's private harness on 2026-09-29, in two rounds: five arms (750 requests, finished 22:03:39 UTC), then one arm (150 requests, finished 22:11:23 UTC). Not sent by this package; the cost is the sum of the rows
- Requests: every recorded user turn is rebuilt byte for byte by this package from the case file, and the system prompt and tool schema the private harness sent are prompt/system.txt and prompt/tool_schema.json, pinned by sha256 (tests/test_phrases_record.py)
- Ceiling: one $3.50 ceiling covered both rounds and 150 further requests ($0.48) on the app's own regression sentences, which quote books still in copyright and are not published here

All 900 planned trials were bought.

Failed requests (counted as failed trials): 0.
Answers that carried « or » (scored with the marks removed): 0.

## Totals

| Arm | Passes | Trials | Rate |
|---|---:|---:|---:|
| no-clause | 105 | 150 | 70% |
| own-meaning+exception | 122 | 150 | 81% |
| own-meaning | 119 | 150 | 79% |
| words-outside | 130 | 150 | 87% |
| three-examples | 116 | 150 | 77% |
| adverb-examples | 115 | 150 | 77% |

## By group

| Arm | Phrase words | Exceptions | Plain words | Phrase words, as first scored | Phrase words reporting the phrase |
|---|---:|---:|---:|---:|---:|
| no-clause | 35/80 | 30/30 | 40/40 | 32/80 | 22/80 |
| own-meaning+exception | 52/80 | 30/30 | 40/40 | 47/80 | 20/80 |
| own-meaning | 50/80 | 29/30 | 40/40 | 46/80 | 18/80 |
| words-outside | 60/80 | 30/30 | 40/40 | 55/80 | 22/80 |
| three-examples | 46/80 | 30/30 | 40/40 | 42/80 | 21/80 |
| adverb-examples | 46/80 | 29/30 | 40/40 | 46/80 | 33/80 |

A check was amended after these answers were first scored. Every other count in this report uses the checks as published.

## Per case

| Case | no-clause | own-meaning+exception | own-meaning | words-outside | three-examples | adverb-examples |
|---|---:|---:|---:|---:|---:|---:|
| alta-en-voz-alta | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 |
| caso-en-todo-caso | 3/5 | 4/5 | 3/5 | 5/5 | 5/5 | 5/5 |
| completo-por-completo | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| echo-echo-a-correr | 3/5 | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 |
| fin-por-fin | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 1/5 |
| fria-a-sangre-fria | 1/5 | 5/5 | 2/5 | 5/5 | 2/5 | 0/5 |
| hizo-hizo-caso | 3/5 | 5/5 | 4/5 | 5/5 | 4/5 | 3/5 |
| lugar-en-lugar-de | 1/5 | 2/5 | 4/5 | 5/5 | 1/5 | 3/5 |
| mayor-hijo-mayor | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| modo-de-modo-que | 1/5 | 3/5 | 4/5 | 5/5 | 3/5 | 5/5 |
| nuevo-de-nuevo | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| p-arbol | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-cansada | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-cuchillo | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-llave | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-nieve | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-pasos | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-pequena | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| p-rompio | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| pie-de-pie | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| primera-por-primera-vez | 4/5 | 4/5 | 5/5 | 5/5 | 5/5 | 2/5 |
| sin-sin-embargo | 0/5 | 4/5 | 3/5 | 5/5 | 1/5 | 5/5 |
| tras-una-tras-otra | 4/5 | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 |
| vez-otra-vez | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| x-embargo-sin-embargo-1 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| x-embargo-sin-embargo-2 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| x-hurtadillas-a-hurtadillas | 5/5 | 5/5 | 4/5 | 5/5 | 5/5 | 4/5 |
| x-menudo-a-menudo | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| x-reojo-de-reojo | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| x-repente-de-repente | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |

## Answers

### alta-en-voz-alta

Selection: "alta"

no-clause:

- 5 x "loud": pass

own-meaning+exception:

- 5 x "loud": pass

own-meaning:

- 5 x "loud": pass

words-outside:

- 5 x "loud": pass

three-examples:

- 5 x "loud": pass

adverb-examples:

- 4 x "loud": pass
- 1 x "aloud": fail: absorbed "aloud" from outside the selection

### caso-en-todo-caso

Selection: "caso"

no-clause:

- 2 x "in any case": fail: absorbed "any case" from outside the selection
- 2 x "event": pass
- 1 x "instance": pass

own-meaning+exception:

- 4 x "case": pass
- 1 x "any case": fail: absorbed "any case" from outside the selection

own-meaning:

- 2 x "instance": pass
- 1 x "any case": fail: absorbed "any case" from outside the selection
- 1 x "case": pass
- 1 x "circumstance": fail: missing any of "case" / "event" / "instance" / "matter"

words-outside:

- 4 x "instance": pass
- 1 x "event": pass

three-examples:

- 4 x "case": pass
- 1 x "instance": pass

adverb-examples:

- 3 x "instance": pass
- 2 x "event": pass

### completo-por-completo

Selection: "completo"

no-clause:

- 5 x "completely": fail: absorbed "completely" from outside the selection

own-meaning+exception:

- 5 x "completely": fail: absorbed "completely" from outside the selection

own-meaning:

- 5 x "completely": fail: absorbed "completely" from outside the selection

words-outside:

- 5 x "completely": fail: absorbed "completely" from outside the selection

three-examples:

- 5 x "completely": fail: absorbed "completely" from outside the selection

adverb-examples:

- 5 x "completely": fail: absorbed "completely" from outside the selection

### echo-echo-a-correr

Selection: "echó"

no-clause:

- 2 x "began": pass
- 2 x "began to run": fail: absorbed "run" from outside the selection
- 1 x "began to": pass

own-meaning+exception:

- 2 x "began to": pass
- 2 x "started": pass
- 1 x "began": pass

own-meaning:

- 2 x "began to": pass
- 2 x "started": pass
- 1 x "began": pass

words-outside:

- 2 x "began to": pass
- 2 x "began": pass
- 1 x "started": pass

three-examples:

- 2 x "began": pass
- 2 x "started": pass
- 1 x "began to": pass

adverb-examples:

- 3 x "started": pass
- 1 x "threw... into": pass
- 1 x "began to run": fail: absorbed "run" from outside the selection

### fin-por-fin

Selection: "fin"

no-clause:

- 5 x "at last": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "last" from outside the selection

own-meaning+exception:

- 5 x "at last": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "last" from outside the selection

own-meaning:

- 5 x "at last": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "last" from outside the selection

words-outside:

- 4 x "at last": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "last" from outside the selection
- 1 x "finally": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "final" from outside the selection

three-examples:

- 4 x "at last": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "last" from outside the selection
- 1 x "finally": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "final" from outside the selection

adverb-examples:

- 4 x "finally": fail: missing any of "end" / "finish" / "aim" / "purpose" / "goal"; absorbed "final" from outside the selection
- 1 x "end": pass

### fria-a-sangre-fria

Selection: "fría"

no-clause:

- 3 x "cold blood": fail: absorbed "blood" from outside the selection
- 1 x "cold-blooded": fail: absorbed "blood" from outside the selection
- 1 x "cold": pass

own-meaning+exception:

- 5 x "cold": pass

own-meaning:

- 2 x "cold blood": fail: absorbed "blood" from outside the selection
- 2 x "cold": pass
- 1 x "cold-bloodedly": fail: absorbed "blood" from outside the selection

words-outside:

- 5 x "cold": pass

three-examples:

- 2 x "cold blood": fail: absorbed "blood" from outside the selection
- 2 x "cold": pass
- 1 x "cold-bloodedly": fail: absorbed "blood" from outside the selection

adverb-examples:

- 5 x "cold blood": fail: absorbed "blood" from outside the selection

### hizo-hizo-caso

Selection: "hizo"

no-clause:

- 3 x "paid": pass
- 1 x "paid … attention": fail: absorbed "attention" from outside the selection
- 1 x "paid … attention to": fail: absorbed "attention" from outside the selection

own-meaning+exception:

- 5 x "paid": pass

own-meaning:

- 4 x "paid": pass
- 1 x "paid … attention to": fail: absorbed "attention" from outside the selection

words-outside:

- 5 x "paid": pass

three-examples:

- 4 x "paid": pass
- 1 x "did... pay ... attention to": fail: absorbed "attention" from outside the selection

adverb-examples:

- 2 x "made": pass
- 1 x "heeded": fail: missing any of "made" / "did" / "make" / "paid" / "pay"; absorbed "heed" from outside the selection
- 1 x "paid": pass
- 1 x "paid ... attention to": fail: absorbed "attention" from outside the selection

### lugar-en-lugar-de

Selection: "lugar"

no-clause:

- 3 x "instead": fail: missing any of "place" / "spot" / "site" / "location"; absorbed "instead" from outside the selection
- 1 x "place": pass
- 1 x "instead of": fail: missing any of "place" / "spot" / "site" / "location"; absorbed "instead" from outside the selection

own-meaning+exception:

- 3 x "instead": fail: missing any of "place" / "spot" / "site" / "location"; absorbed "instead" from outside the selection
- 2 x "place": pass

own-meaning:

- 4 x "place": pass
- 1 x "of": fail: missing any of "place" / "spot" / "site" / "location"

words-outside:

- 5 x "place": pass

three-examples:

- 2 x "instead": fail: missing any of "place" / "spot" / "site" / "location"; absorbed "instead" from outside the selection
- 1 x "stead": fail: missing any of "place" / "spot" / "site" / "location"
- 1 x "place": pass
- 1 x "of": fail: missing any of "place" / "spot" / "site" / "location"

adverb-examples:

- 3 x "place": pass
- 2 x "instead": fail: missing any of "place" / "spot" / "site" / "location"; absorbed "instead" from outside the selection

### mayor-hijo-mayor

Selection: "mayor"

no-clause:

- 4 x "eldest": pass
- 1 x "oldest": pass

own-meaning+exception:

- 5 x "eldest": pass

own-meaning:

- 4 x "eldest": pass
- 1 x "oldest": pass

words-outside:

- 3 x "eldest": pass
- 2 x "oldest": pass

three-examples:

- 4 x "eldest": pass
- 1 x "oldest": pass

adverb-examples:

- 5 x "eldest": pass

### modo-de-modo-que

Selection: "modo"

no-clause:

- 3 x "so that": fail: missing any of "way" / "manner" / "mode" / "fashion" / "means"; absorbed "so that" from outside the selection
- 1 x "so": fail: missing any of "way" / "manner" / "mode" / "fashion" / "means"
- 1 x "in such a way that": pass

own-meaning+exception:

- 3 x "manner": pass
- 2 x "so that": fail: missing any of "way" / "manner" / "mode" / "fashion" / "means"; absorbed "so that" from outside the selection

own-meaning:

- 3 x "way": pass
- 1 x "so that": fail: missing any of "way" / "manner" / "mode" / "fashion" / "means"; absorbed "so that" from outside the selection
- 1 x "in such a way that": pass

words-outside:

- 5 x "manner": pass

three-examples:

- 2 x "so that": fail: missing any of "way" / "manner" / "mode" / "fashion" / "means"; absorbed "so that" from outside the selection
- 2 x "way": pass
- 1 x "in such a way": pass

adverb-examples:

- 4 x "way": pass
- 1 x "manner": pass

### nuevo-de-nuevo

Selection: "nuevo"

no-clause:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

own-meaning+exception:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

own-meaning:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

words-outside:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

three-examples:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

adverb-examples:

- 5 x "again": fail: missing any of "new" / "fresh" / "novel"; absorbed "again" from outside the selection

### p-arbol

Selection: "árbol"

no-clause:

- 5 x "tree": pass

own-meaning+exception:

- 5 x "tree": pass

own-meaning:

- 5 x "tree": pass

words-outside:

- 5 x "tree": pass

three-examples:

- 5 x "tree": pass

adverb-examples:

- 5 x "tree": pass

### p-cansada

Selection: "cansada"

no-clause:

- 5 x "tired": pass

own-meaning+exception:

- 5 x "tired": pass

own-meaning:

- 5 x "tired": pass

words-outside:

- 5 x "tired": pass

three-examples:

- 5 x "tired": pass

adverb-examples:

- 5 x "tired": pass

### p-cuchillo

Selection: "cuchillo"

no-clause:

- 5 x "knife": pass

own-meaning+exception:

- 5 x "knife": pass

own-meaning:

- 5 x "knife": pass

words-outside:

- 5 x "knife": pass

three-examples:

- 5 x "knife": pass

adverb-examples:

- 5 x "knife": pass

### p-llave

Selection: "llave"

no-clause:

- 5 x "key": pass

own-meaning+exception:

- 5 x "key": pass

own-meaning:

- 5 x "key": pass

words-outside:

- 5 x "key": pass

three-examples:

- 5 x "key": pass

adverb-examples:

- 5 x "key": pass

### p-nieve

Selection: "nieve"

no-clause:

- 5 x "snow": pass

own-meaning+exception:

- 5 x "snow": pass

own-meaning:

- 5 x "snow": pass

words-outside:

- 5 x "snow": pass

three-examples:

- 5 x "snow": pass

adverb-examples:

- 5 x "snow": pass

### p-pasos

Selection: "pasos"

no-clause:

- 5 x "footsteps": pass

own-meaning+exception:

- 5 x "footsteps": pass

own-meaning:

- 5 x "footsteps": pass

words-outside:

- 5 x "footsteps": pass

three-examples:

- 4 x "footsteps": pass
- 1 x "steps": pass

adverb-examples:

- 5 x "footsteps": pass

### p-pequena

Selection: "pequeña"

no-clause:

- 5 x "small": pass

own-meaning+exception:

- 5 x "small": pass

own-meaning:

- 5 x "small": pass

words-outside:

- 5 x "small": pass

three-examples:

- 5 x "small": pass

adverb-examples:

- 5 x "small": pass

### p-rompio

Selection: "rompió"

no-clause:

- 3 x "broke": pass
- 2 x "snapped": pass

own-meaning+exception:

- 5 x "broke": pass

own-meaning:

- 5 x "broke": pass

words-outside:

- 5 x "broke": pass

three-examples:

- 5 x "broke": pass

adverb-examples:

- 5 x "broke": pass

### pie-de-pie

Selection: "pie"

no-clause:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

own-meaning+exception:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

own-meaning:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

words-outside:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

three-examples:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

adverb-examples:

- 5 x "standing": fail: missing any of "foot" / "feet"; absorbed "stand" from outside the selection

### primera-por-primera-vez

Selection: "primera"

no-clause:

- 4 x "first": pass
- 1 x "first time": fail: absorbed "time" from outside the selection

own-meaning+exception:

- 4 x "first": pass
- 1 x "first time": fail: absorbed "time" from outside the selection

own-meaning:

- 5 x "first": pass

words-outside:

- 5 x "first": pass

three-examples:

- 5 x "first": pass

adverb-examples:

- 3 x "first time": fail: absorbed "time" from outside the selection
- 2 x "first": pass

### sin-sin-embargo

Selection: "Sin"

no-clause:

- 4 x "however": fail: missing any of "without"; absorbed "however" from outside the selection
- 1 x "However": fail: missing any of "without"; absorbed "however" from outside the selection

own-meaning+exception:

- 3 x "without": pass
- 1 x "however": fail: missing any of "without"; absorbed "however" from outside the selection
- 1 x "Without": pass

own-meaning:

- 3 x "without": pass
- 1 x "however": fail: missing any of "without"; absorbed "however" from outside the selection
- 1 x "However": fail: missing any of "without"; absorbed "however" from outside the selection

words-outside:

- 5 x "without": pass

three-examples:

- 3 x "however": fail: missing any of "without"; absorbed "however" from outside the selection
- 1 x "without": pass
- 1 x "However": fail: missing any of "without"; absorbed "however" from outside the selection

adverb-examples:

- 5 x "without": pass

### tras-una-tras-otra

Selection: "tras"

no-clause:

- 3 x "after": pass
- 1 x "one after another": fail: absorbed "another" from outside the selection
- 1 x "one after": pass

own-meaning+exception:

- 5 x "after": pass

own-meaning:

- 5 x "after": pass

words-outside:

- 5 x "after": pass

three-examples:

- 5 x "after": pass

adverb-examples:

- 4 x "after": pass
- 1 x "one after another": fail: absorbed "another" from outside the selection

### vez-otra-vez

Selection: "vez"

no-clause:

- 5 x "time": pass

own-meaning+exception:

- 5 x "time": pass

own-meaning:

- 5 x "time": pass

words-outside:

- 5 x "time": pass

three-examples:

- 5 x "time": pass

adverb-examples:

- 5 x "time": pass

### x-embargo-sin-embargo-1

Selection: "embargo"

no-clause:

- 5 x "however": pass

own-meaning+exception:

- 5 x "however": pass

own-meaning:

- 5 x "however": pass

words-outside:

- 5 x "however": pass

three-examples:

- 5 x "however": pass

adverb-examples:

- 5 x "however": pass

### x-embargo-sin-embargo-2

Selection: "embargo"

no-clause:

- 4 x "however": pass
- 1 x "yet": pass

own-meaning+exception:

- 3 x "yet": pass
- 1 x "nevertheless": pass
- 1 x "however": pass

own-meaning:

- 5 x "however": pass

words-outside:

- 5 x "however": pass

three-examples:

- 5 x "however": pass

adverb-examples:

- 5 x "however": pass

### x-hurtadillas-a-hurtadillas

Selection: "hurtadillas"

no-clause:

- 3 x "on the sly": pass
- 1 x "stealthily": pass
- 1 x "by stealth": pass

own-meaning+exception:

- 3 x "stealthily": pass
- 2 x "on tiptoe; stealthily": pass

own-meaning:

- 4 x "stealthily": pass
- 1 x "on tiptoe": fail: missing any of "stealth" / "furtive" / "secret" / "sly" / "sneak" / "covert" / "surreptitious"

words-outside:

- 2 x "stealthily": pass
- 2 x "on the sly": pass
- 1 x "stealth": pass

three-examples:

- 4 x "stealthily": pass
- 1 x "on the sly": pass

adverb-examples:

- 2 x "on the sly": pass
- 1 x "stealthily": pass
- 1 x "by stealth": pass
- 1 x "": fail: missing any of "stealth" / "furtive" / "secret" / "sly" / "sneak" / "covert" / "surreptitious"

### x-menudo-a-menudo

Selection: "menudo"

no-clause:

- 4 x "often": pass
- 1 x "frequently": pass

own-meaning+exception:

- 5 x "often": pass

own-meaning:

- 5 x "often": pass

words-outside:

- 4 x "often": pass
- 1 x "frequently": pass

three-examples:

- 5 x "often": pass

adverb-examples:

- 5 x "often": pass

### x-reojo-de-reojo

Selection: "reojo"

no-clause:

- 5 x "out of the corner of my eye": pass

own-meaning+exception:

- 4 x "out of the corner of my eye": pass
- 1 x "the corner of one's eye": pass

own-meaning:

- 5 x "out of the corner of my eye": pass

words-outside:

- 1 x "the corner of my eye": pass
- 1 x "out of the corner of my eye": pass
- 1 x "out of the corner of one's eye": pass
- 1 x "corner of the eye": pass
- 1 x "from the corner of my eye": pass

three-examples:

- 4 x "out of the corner of my eye": pass
- 1 x "out of the corner of one's eye": pass

adverb-examples:

- 2 x "out of the corner of one's eye": pass
- 1 x "sidelong glance": pass
- 1 x "the corner of one's eye": pass
- 1 x "out of the corner of my eye": pass

### x-repente-de-repente

Selection: "repente"

no-clause:

- 5 x "suddenly": pass

own-meaning+exception:

- 5 x "suddenly": pass

own-meaning:

- 5 x "suddenly": pass

words-outside:

- 5 x "suddenly": pass

three-examples:

- 5 x "suddenly": pass

adverb-examples:

- 5 x "suddenly": pass

