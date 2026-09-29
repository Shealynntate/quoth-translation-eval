# Gloss eval report

## Run

- Experiment: marks
- Model: `claude-haiku-4-5-20251001`
- Cases: `cases/marks.json` (sha256 `b9d1737298ec`)
- Trials per case and arm: 5
- Started: 2026-09-29T19:57:16+00:00; finished: 2026-09-29T19:58:14+00:00 (UTC)
- Cost: $0.5771 (ceiling $0.90, $0.0000 already spent against it before this run)
- Command: `python -m gloss_eval marks --cases cases/marks.json --model haiku --trials 5 --max-usd 0.9 --workers 4`
- Package version: 0.1.0

All 190 planned trials were bought.

Failed requests (counted as failed trials): 0.
Answers that carried « or » (scored with the marks removed): 0.

## Totals

| Arm | Passes | Trials | Rate |
|---|---:|---:|---:|
| unmarked | 62 | 95 | 65% |
| marked | 86 | 95 | 91% |

## Per case

| Case | unmarked | marked |
|---|---:|---:|
| a-punto-de-absorb-verb | 5/5 | 5/5 |
| acababa-de-absorb-verb | 4/5 | 5/5 |
| baronet-tono-resuelto-tag | 5/5 | 5/5 |
| caperucita-dijo-el-lobo | 0/5 | 5/5 |
| como-el-mejor-holmes-vocative | 1/5 | 5/5 |
| delantal-absorb-plata | 0/5 | 5/5 |
| fria-sangre-fria-absorb | 0/5 | 0/5 |
| generoso-dijo-muchacho-whole-sentence | 5/5 | 5/5 |
| le-dio-absorb-beso | 5/5 | 5/5 |
| lobo-echo-a-correr-subject | 4/5 | 5/5 |
| marido-se-vistio-subject | 5/5 | 5/5 |
| ojos-muy-grandes-noun | 5/5 | 5/5 |
| por-lo-tanto-disponte-connective | 5/5 | 5/5 |
| rey-tan-grande-speech-tag | 0/5 | 5/5 |
| rogerio-arrodillo-absorb-both | 4/5 | 5/5 |
| sin-embargo-miradas-connective | 5/5 | 5/5 |
| temor-caballos-clause-tail | 5/5 | 5/5 |
| tiro-contra-la-pared-absorb-both | 4/5 | 5/5 |
| tras-uno-tras-otro-particle | 0/5 | 1/5 |

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

- 4 x "had just": pass
- 1 x "had just arrived": fail: absorbed "arriv" from outside the selection

marked:

- 5 x "had just": pass

### baronet-tono-resuelto-tag

Selection: "—dijo el baronet en tono resuelto"

unmarked:

- 3 x "said the baronet in a resolute tone": pass
- 1 x "said the baronet in a determined tone": pass
- 1 x "the baronet said in a determined tone": pass

marked:

- 2 x "said the baronet in a resolute tone": pass
- 1 x "said the baronet in a determined tone": pass
- 1 x "said the baronet in a firm tone": pass
- 1 x "said the baronet resolutely": pass

### caperucita-dijo-el-lobo

Selection: "Caperucita roja, dijo el lobo"

unmarked:

- 5 x "Little Red Riding Hood": fail: missing "said"; missing "wolf"

marked:

- 4 x "Little Red Riding Hood, said the wolf": pass
- 1 x "Red Riding Hood, said the wolf": pass

### como-el-mejor-holmes-vocative

Selection: "como el mejor, señor Holmes"

unmarked:

- 4 x "as well as anyone": fail: missing "holmes"
- 1 x "as well as anyone, sir Holmes": pass

marked:

- 3 x "as well as anyone, Mr. Holmes": pass
- 1 x "as well as anyone, sir Holmes": pass
- 1 x "like anyone, Mr. Holmes": pass

### delantal-absorb-plata

Selection: "se puso un delantal"

unmarked:

- 5 x "put on a silver apron": fail: absorbed "silver" from outside the selection

marked:

- 3 x "put on an apron": pass
- 1 x "he put on an apron": pass
- 1 x "she put on an apron": pass

### fria-sangre-fria-absorb

Selection: "fría"

unmarked:

- 3 x "cold-blooded": fail: absorbed "blood" from outside the selection
- 2 x "cold blood": fail: absorbed "blood" from outside the selection

marked:

- 5 x "cold blood": fail: absorbed "blood" from outside the selection

### generoso-dijo-muchacho-whole-sentence

Selection: "generoso —dijo el muchacho—, voy a dejar"

unmarked:

- 3 x "generous": pass
- 2 x "Since you're so generous": pass

marked:

- 2 x "generous," said the boy, "I'll stop": pass
- 1 x "you're so generous," said the boy, "I'll stop": pass
- 1 x "generous," said the boy, "I'm going to stop": pass
- 1 x "generous, said the boy, I'm going to stop": pass

### le-dio-absorb-beso

Selection: "le dio"

unmarked:

- 3 x "gave him": pass
- 2 x "gave him/her": pass

marked:

- 5 x "gave him": pass

### lobo-echo-a-correr-subject

Selection: "El lobo echó a correr tanto como pudo"

unmarked:

- 2 x "The wolf ran as fast as it could": pass
- 1 x "ran as fast as he could": fail: missing "wolf"
- 1 x "The wolf set off running as fast as he could": pass
- 1 x "The wolf began to run as fast as it could": pass

marked:

- 2 x "The wolf started running as fast as it could": pass
- 1 x "The wolf began to run as fast as it could": pass
- 1 x "The wolf broke into a run as fast as it could": pass
- 1 x "The wolf set off running as fast as it could": pass

### marido-se-vistio-subject

Selection: "El marido se vistió rápidamente y echó a correr"

unmarked:

- 2 x "The husband dressed quickly and ran off": pass
- 1 x "The husband dressed quickly and began to run": pass
- 1 x "The husband got dressed quickly and started running": pass
- 1 x "The husband dressed quickly and rushed off running": pass

marked:

- 1 x "The husband dressed quickly and broke into a run": pass
- 1 x "The husband dressed quickly and began to run": pass
- 1 x "The husband dressed quickly and took off running": pass
- 1 x "The husband got dressed quickly and rushed off": pass
- 1 x "The husband dressed quickly and ran off": pass

### ojos-muy-grandes-noun

Selection: "ojos muy grandes"

unmarked:

- 5 x "very large eyes": pass

marked:

- 4 x "very large eyes": pass
- 1 x "very big eyes": pass

### por-lo-tanto-disponte-connective

Selection: "Por lo tanto disponte a separarte de tu hija"

unmarked:

- 2 x "Therefore, prepare yourself to part with your daughter": pass
- 1 x "Therefore prepare yourself to part with your daughter": pass
- 1 x "Therefore prepare yourself to separate from your daughter": pass
- 1 x "therefore, prepare yourself to part with your daughter": pass

marked:

- 4 x "Therefore, prepare yourself to part with your daughter": pass
- 1 x "Therefore prepare yourself to separate from your daughter": pass

### rey-tan-grande-speech-tag

Selection: "tan grande —dijo el rey"

unmarked:

- 5 x "so great": fail: missing "said"; missing "king"

marked:

- 2 x "so great, said the king": pass
- 1 x "so great—said the king": pass
- 1 x "so great —said the king": pass
- 1 x "so great—the king said": pass

### rogerio-arrodillo-absorb-both

Selection: "Rogerio se arrodilló a su lado con aspecto"

unmarked:

- 3 x "Rogerio knelt at his side with a": pass
- 1 x "Rogerio knelt beside him with a": pass
- 1 x "old Rogerio knelt at his side looking": fail: absorbed "old " from outside the selection

marked:

- 2 x "Rogerio knelt at his side with an air": pass
- 1 x "Rogerio knelt at his side with a": pass
- 1 x "Rogerio knelt down beside him looking": pass
- 1 x "Rogerio knelt at his side with a look": pass

### sin-embargo-miradas-connective

Selection: "sin embargo, las miradas se volvieron fijas"

unmarked:

- 3 x "however": pass
- 1 x "however, the glances became fixed": pass
- 1 x "however, gazes became fixed": pass

marked:

- 2 x "however, the gazes became fixed": pass
- 1 x "yet the gazes became fixed": pass
- 1 x "however, gazes became fixed": pass
- 1 x "however, the gazes turned fixed": pass

### temor-caballos-clause-tail

Selection: "temor de que no asustase a los caballos"

unmarked:

- 4 x "fear that he would frighten the horses": pass
- 1 x "fear that he might frighten the horses": pass

marked:

- 2 x "fear that he might frighten the horses": pass
- 2 x "fear that he would frighten the horses": pass
- 1 x "fear that it might frighten the horses": pass

### tiro-contra-la-pared-absorb-both

Selection: "la cogió y la tiró contra la pared con todas"

unmarked:

- 2 x "grabbed her and hurled her against the wall with all": pass
- 1 x "she grabbed it and threw it against the wall with all her strength": fail: absorbed "strength" from outside the selection
- 1 x "seized her and hurled her against the wall with all": pass
- 1 x "seized her and threw her against the wall with all": pass

marked:

- 3 x "seized her and hurled her against the wall with all": pass
- 1 x "grabbed her and threw her against the wall with all": pass
- 1 x "seized it and threw it against the wall with all": pass

### tras-uno-tras-otro-particle

Selection: "tras"

unmarked:

- 5 x "one after another": fail: absorbed "another" from outside the selection; is exactly the rejected gloss "one after another"

marked:

- 4 x "one after another": fail: absorbed "another" from outside the selection; is exactly the rejected gloss "one after another"
- 1 x "one after the other": pass

