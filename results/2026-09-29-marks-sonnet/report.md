# Gloss eval report

## Run

- Experiment: marks
- Model: `claude-sonnet-5`
- Cases: `cases/marks.json` (sha256 `b9d1737298ec`)
- Trials per case and arm: 5
- Started: 2026-09-29T19:58:27+00:00; finished: 2026-09-29T20:00:09+00:00 (UTC)
- Cost: $1.4488 (ceiling $1.90, $0.0000 already spent against it before this run)
- Command: `python -m gloss_eval marks --cases cases/marks.json --model sonnet --trials 5 --max-usd 1.9 --workers 4`
- Package version: 0.1.0

All 190 planned trials were bought.

Failed requests (counted as failed trials): 0.
Answers that carried « or » (scored with the marks removed): 0.

## Totals

| Arm | Passes | Trials | Rate |
|---|---:|---:|---:|
| unmarked | 95 | 95 | 100% |
| marked | 95 | 95 | 100% |

## Per case

| Case | unmarked | marked |
|---|---:|---:|
| a-punto-de-absorb-verb | 5/5 | 5/5 |
| acababa-de-absorb-verb | 5/5 | 5/5 |
| baronet-tono-resuelto-tag | 5/5 | 5/5 |
| caperucita-dijo-el-lobo | 5/5 | 5/5 |
| como-el-mejor-holmes-vocative | 5/5 | 5/5 |
| delantal-absorb-plata | 5/5 | 5/5 |
| fria-sangre-fria-absorb | 5/5 | 5/5 |
| generoso-dijo-muchacho-whole-sentence | 5/5 | 5/5 |
| le-dio-absorb-beso | 5/5 | 5/5 |
| lobo-echo-a-correr-subject | 5/5 | 5/5 |
| marido-se-vistio-subject | 5/5 | 5/5 |
| ojos-muy-grandes-noun | 5/5 | 5/5 |
| por-lo-tanto-disponte-connective | 5/5 | 5/5 |
| rey-tan-grande-speech-tag | 5/5 | 5/5 |
| rogerio-arrodillo-absorb-both | 5/5 | 5/5 |
| sin-embargo-miradas-connective | 5/5 | 5/5 |
| temor-caballos-clause-tail | 5/5 | 5/5 |
| tiro-contra-la-pared-absorb-both | 5/5 | 5/5 |
| tras-uno-tras-otro-particle | 5/5 | 5/5 |

## Answers

### a-punto-de-absorb-verb

Selection: "a punto de"

unmarked:

- 5 x "about to": pass

marked:

- 5 x "about to": pass

### acababa-de-absorb-verb

Selection: "acababa de"

unmarked:

- 5 x "had just": pass

marked:

- 5 x "had just": pass

### baronet-tono-resuelto-tag

Selection: "—dijo el baronet en tono resuelto"

unmarked:

- 3 x "said the baronet resolutely": pass
- 2 x "said the baronet in a resolute tone": pass

marked:

- 3 x "said the baronet resolutely": pass
- 2 x "said the baronet in a resolute tone": pass

### caperucita-dijo-el-lobo

Selection: "Caperucita roja, dijo el lobo"

unmarked:

- 5 x "Little Red Riding Hood, said the wolf": pass

marked:

- 5 x ""Little Red Riding Hood," said the wolf": pass

### como-el-mejor-holmes-vocative

Selection: "como el mejor, señor Holmes"

unmarked:

- 3 x "as well as the next man, Mr. Holmes": pass
- 2 x "as well as anyone, Mr. Holmes": pass

marked:

- 3 x "as well as the next man, Mr. Holmes": pass
- 2 x "as well as anyone, Mr. Holmes": pass

### delantal-absorb-plata

Selection: "se puso un delantal"

unmarked:

- 5 x "put on an apron": pass

marked:

- 5 x "put on an apron": pass

### fria-sangre-fria-absorb

Selection: "fría"

unmarked:

- 5 x "cold": pass

marked:

- 5 x "cold": pass

### generoso-dijo-muchacho-whole-sentence

Selection: "generoso —dijo el muchacho—, voy a dejar"

unmarked:

- 5 x "generous," said the boy, "I'm going to stop": pass

marked:

- 3 x "generous," said the young man, "I'm going to stop": pass
- 1 x ""generous," said the boy, "I'll stop": pass
- 1 x ""generous," said the young man, "I will stop": pass

### le-dio-absorb-beso

Selection: "le dio"

unmarked:

- 3 x "gave him": pass
- 1 x "gave him/her": pass
- 1 x "gave... to him": pass

marked:

- 5 x "gave him": pass

### lobo-echo-a-correr-subject

Selection: "El lobo echó a correr tanto como pudo"

unmarked:

- 2 x "The wolf ran off as fast as he could": pass
- 1 x "The wolf started running as fast as it could": pass
- 1 x "The wolf took off running as fast as he could": pass
- 1 x "The wolf set off running as fast as he could": pass

marked:

- 2 x "The wolf took off running as fast as he could": pass
- 2 x "The wolf set off running as fast as he could": pass
- 1 x "The wolf broke into a run as fast as he could": pass

### marido-se-vistio-subject

Selection: "El marido se vistió rápidamente y echó a correr"

unmarked:

- 2 x "The husband got dressed quickly and took off running": pass
- 2 x "The husband got dressed quickly and ran off": pass
- 1 x "The husband dressed quickly and took off running": pass

marked:

- 3 x "The husband got dressed quickly and ran off": pass
- 1 x "The husband got dressed quickly and took off running": pass
- 1 x "The husband dressed quickly and ran off": pass

### ojos-muy-grandes-noun

Selection: "ojos muy grandes"

unmarked:

- 4 x "very big eyes": pass
- 1 x "such big eyes": pass

marked:

- 5 x "very big eyes": pass

### por-lo-tanto-disponte-connective

Selection: "Por lo tanto disponte a separarte de tu hija"

unmarked:

- 3 x "So get ready to part with your daughter": pass
- 1 x "Therefore get ready to part with your daughter": pass
- 1 x "Therefore, get ready to part with your daughter": pass

marked:

- 4 x "Therefore prepare yourself to part with your daughter": pass
- 1 x "So get ready to part with your daughter": pass

### rey-tan-grande-speech-tag

Selection: "tan grande —dijo el rey"

unmarked:

- 3 x "so great —said the king": pass
- 2 x "so great, said the king": pass

marked:

- 4 x "so great —said the king": pass
- 1 x "so great,” said the king, “": pass

### rogerio-arrodillo-absorb-both

Selection: "Rogerio se arrodilló a su lado con aspecto"

unmarked:

- 5 x "Rogerio knelt at his side looking": pass

marked:

- 5 x "Rogerio knelt at his side looking": pass

### sin-embargo-miradas-connective

Selection: "sin embargo, las miradas se volvieron fijas"

unmarked:

- 3 x "however, the gazes became fixed": pass
- 1 x "however, the gazes grew fixed": pass
- 1 x "however, the glances became fixed": pass

marked:

- 2 x "however, the gazes grew fixed": pass
- 2 x "however, the gazes became fixed": pass
- 1 x "however, their gazes became fixed": pass

### temor-caballos-clause-tail

Selection: "temor de que no asustase a los caballos"

unmarked:

- 2 x "for fear that he might frighten the horses": pass
- 1 x "for fear that it might scare the horses": pass
- 1 x "for fear that it might frighten the horses": pass
- 1 x "for fear that it would frighten the horses": pass

marked:

- 2 x "fear that he might scare the horses": pass
- 2 x "for fear that he might frighten the horses": pass
- 1 x "fear that he might frighten the horses": pass

### tiro-contra-la-pared-absorb-both

Selection: "la cogió y la tiró contra la pared con todas"

unmarked:

- 5 x "grabbed it and threw it against the wall with all": pass

marked:

- 3 x "grabbed it and threw it against the wall with all": pass
- 2 x "she grabbed it and threw it against the wall with all": pass

### tras-uno-tras-otro-particle

Selection: "tras"

unmarked:

- 5 x "after": pass

marked:

- 5 x "after": pass

