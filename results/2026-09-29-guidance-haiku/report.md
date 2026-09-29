# Gloss eval report

## Run

- Experiment: guidance
- Model: `claude-haiku-4-5-20251001`
- Cases: `cases/haber.json` (sha256 `a3b6f68f04ac`)
- Trials per case and arm: 5
- Started: 2026-09-29T20:00:28+00:00; finished: 2026-09-29T20:03:18+00:00 (UTC)
- Cost: $1.3188 (ceiling $1.90, $0.0000 already spent against it before this run)
- Command: `python -m gloss_eval guidance --cases cases/haber.json --model haiku --trials 5 --max-usd 1.9 --workers 4`
- Package version: 0.1.0

All 400 planned trials were bought.

Failed requests (counted as failed trials): 0.
Answers that carried « or » (scored with the marks removed): 0.

## Totals

| Arm | Passes | Trials | Rate |
|---|---:|---:|---:|
| no-guidance | 18 | 80 | 23% |
| rule | 12 | 80 | 15% |
| rule+example | 36 | 80 | 45% |
| second-example | 50 | 80 | 63% |
| turn-clause | 76 | 80 | 95% |

## Per case

| Case | no-guidance | rule | rule+example | second-example | turn-clause |
|---|---:|---:|---:|---:|---:|
| haberle-cogido | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| haberle-desobedecido | 0/5 | 0/5 | 1/5 | 3/5 | 5/5 |
| haberle-librado | 1/5 | 0/5 | 2/5 | 4/5 | 5/5 |
| haberlo-sabido | 0/5 | 0/5 | 2/5 | 5/5 | 5/5 |
| haberlos-dejado | 0/5 | 3/5 | 5/5 | 5/5 | 5/5 |
| haberme-quejado | 0/5 | 0/5 | 0/5 | 0/5 | 4/5 |
| haberme-robado | 2/5 | 0/5 | 1/5 | 3/5 | 5/5 |
| haberse-formado | 2/5 | 0/5 | 1/5 | 0/5 | 3/5 |
| haberse-lavado | 5/5 | 2/5 | 2/5 | 1/5 | 5/5 |
| haberse-repuesto | 0/5 | 0/5 | 0/5 | 0/5 | 4/5 |
| haberte-ocultado | 0/5 | 0/5 | 3/5 | 5/5 | 5/5 |
| haberte-oido | 0/5 | 0/5 | 2/5 | 5/5 | 5/5 |
| habiendole-herido | 3/5 | 1/5 | 4/5 | 5/5 | 5/5 |
| habiendoles-dado | 0/5 | 0/5 | 3/5 | 4/5 | 5/5 |
| habiendolo-tocado | 0/5 | 1/5 | 5/5 | 5/5 | 5/5 |
| habiendose-puesto | 0/5 | 0/5 | 0/5 | 0/5 | 5/5 |

## Answers

### haberle-cogido

Selection: "haberle"

no-guidance:

- 2 x "having stolen from her": pass
- 1 x "having": pass
- 1 x "having stolen from him": pass
- 1 x "having taken": pass

rule:

- 1 x "having… taken": pass
- 1 x "having taken from her": pass
- 1 x "having … taken": pass
- 1 x "having... taken": pass
- 1 x "having stolen from her": pass

rule+example:

- 4 x "having … it": pass
- 1 x "having … taken it": pass

second-example:

- 5 x "having … him": pass

turn-clause:

- 5 x "having … him": pass

### haberle-desobedecido

Selection: "haberle"

no-guidance:

- 2 x "having disobeyed": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "to have disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "having disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "disobeying him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection

rule:

- 4 x "having disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "to have disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection

rule+example:

- 2 x "having … disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "having … it": pass
- 1 x "having disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "having … him disobeyed": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection

second-example:

- 3 x "having … him": pass
- 1 x "having … him disobeyed": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection
- 1 x "having … disobeyed him": fail: absorbed "disobey" from outside the selection; absorbed "obey" from outside the selection

turn-clause:

- 5 x "having … him": pass

### haberle-librado

Selection: "haberle"

no-guidance:

- 2 x "having … freed": fail: absorbed "free" from outside the selection
- 1 x "having… freed": fail: absorbed "free" from outside the selection
- 1 x "having freed him": fail: absorbed "free" from outside the selection
- 1 x "having": pass

rule:

- 3 x "having … freed": fail: absorbed "free" from outside the selection
- 1 x "having… freed": fail: absorbed "free" from outside the selection
- 1 x "having … freed him": fail: absorbed "free" from outside the selection

rule+example:

- 2 x "having … it": pass
- 1 x "having … freed him": fail: absorbed "free" from outside the selection
- 1 x "having … it freed": fail: absorbed "free" from outside the selection
- 1 x "having … freed": fail: absorbed "free" from outside the selection

second-example:

- 3 x "having … him": pass
- 1 x "having … freed him": fail: absorbed "free" from outside the selection
- 1 x "having … it": pass

turn-clause:

- 5 x "having … him": pass

### haberlo-sabido

Selection: "haberlo"

no-guidance:

- 5 x "have known it": fail: absorbed "know" from outside the selection

rule:

- 5 x "have known it": fail: absorbed "know" from outside the selection

rule+example:

- 2 x "to have ... known it": fail: absorbed "know" from outside the selection
- 1 x "have ... it": pass
- 1 x "have … it": pass
- 1 x "to have … it known": fail: absorbed "know" from outside the selection

second-example:

- 4 x "having … it": pass
- 1 x "to have … it": pass

turn-clause:

- 5 x "having … it": pass

### haberlos-dejado

Selection: "haberlos"

no-guidance:

- 5 x "having left them": fail: absorbed "left" from outside the selection

rule:

- 2 x "having… them": pass
- 2 x "having left them": fail: absorbed "left" from outside the selection
- 1 x "having … them": pass

rule+example:

- 5 x "having … them": pass

second-example:

- 5 x "having … them": pass

turn-clause:

- 5 x "having … them": pass

### haberme-quejado

Selection: "haberme"

no-guidance:

- 4 x "having complained": fail: absorbed "complain" from outside the selection
- 1 x "to have complained": fail: absorbed "complain" from outside the selection

rule:

- 4 x "having complained": fail: absorbed "complain" from outside the selection
- 1 x "to have complained": fail: absorbed "complain" from outside the selection

rule+example:

- 5 x "having … complained": fail: absorbed "complain" from outside the selection

second-example:

- 4 x "having … complained": fail: absorbed "complain" from outside the selection
- 1 x "having complained": fail: absorbed "complain" from outside the selection

turn-clause:

- 3 x "having …": pass
- 1 x "having … it": pass
- 1 x "having … complained": fail: absorbed "complain" from outside the selection

### haberme-robado

Selection: "haberme"

no-guidance:

- 2 x "having": pass
- 2 x "having robbed me of": fail: absorbed "rob" from outside the selection
- 1 x "having stolen from me": fail: absorbed "stole" from outside the selection; absorbed "stol" from outside the selection

rule:

- 2 x "having … robbed": fail: absorbed "rob" from outside the selection
- 1 x "having robbed me of": fail: absorbed "rob" from outside the selection
- 1 x "having… robbed": fail: absorbed "rob" from outside the selection
- 1 x "to have … robbed": fail: absorbed "rob" from outside the selection

rule+example:

- 1 x "having … it": pass
- 1 x "having … robbed": fail: absorbed "rob" from outside the selection
- 1 x "having robbed me of": fail: absorbed "rob" from outside the selection
- 1 x "robbing me": fail: absorbed "rob" from outside the selection
- 1 x "having … stolen": fail: absorbed "stole" from outside the selection; absorbed "stol" from outside the selection

second-example:

- 3 x "having … me": pass
- 1 x "having … robbed": fail: absorbed "rob" from outside the selection
- 1 x "having … robbed me": fail: absorbed "rob" from outside the selection

turn-clause:

- 2 x "having …": pass
- 2 x "having … me": pass
- 1 x "having … it": pass

### haberse-formado

Selection: "haberse"

no-guidance:

- 3 x "to have formed": fail: absorbed "form" from outside the selection
- 2 x "to have been": pass

rule:

- 4 x "to have formed": fail: absorbed "form" from outside the selection
- 1 x "to have... formed": fail: absorbed "form" from outside the selection

rule+example:

- 2 x "to have formed": fail: absorbed "form" from outside the selection
- 2 x "to have … formed": fail: absorbed "form" from outside the selection
- 1 x "to have been": pass

second-example:

- 2 x "to have formed": fail: absorbed "form" from outside the selection
- 1 x "to have … formed": fail: absorbed "form" from outside the selection
- 1 x "having formed": fail: absorbed "form" from outside the selection
- 1 x "to have ... formed": fail: absorbed "form" from outside the selection

turn-clause:

- 2 x "having …": pass
- 2 x "having … formed": fail: absorbed "form" from outside the selection
- 1 x "having … been": pass

### haberse-lavado

Selection: "haberse"

no-guidance:

- 5 x "having": pass

rule:

- 2 x "having…washed": fail: absorbed "wash" from outside the selection
- 2 x "having": pass
- 1 x "to have … washed": fail: absorbed "wash" from outside the selection

rule+example:

- 3 x "having … washed": fail: absorbed "wash" from outside the selection
- 1 x "having …": pass
- 1 x "having… it": pass

second-example:

- 4 x "having … washed": fail: absorbed "wash" from outside the selection
- 1 x "having …": pass

turn-clause:

- 4 x "having …": pass
- 1 x "having": pass

### haberse-repuesto

Selection: "haberse"

no-guidance:

- 3 x "recovered": fail: absorbed "recover" from outside the selection
- 1 x "having recovered": fail: absorbed "recover" from outside the selection
- 1 x "recovered somewhat": fail: absorbed "recover" from outside the selection

rule:

- 2 x "having recovered": fail: absorbed "recover" from outside the selection
- 1 x "having recovered somewhat": fail: absorbed "recover" from outside the selection
- 1 x "having ... recovered": fail: absorbed "recover" from outside the selection
- 1 x "recovered somewhat": fail: absorbed "recover" from outside the selection

rule+example:

- 1 x "having … recovered somewhat": fail: absorbed "recover" from outside the selection
- 1 x "having … recovered": fail: absorbed "recover" from outside the selection
- 1 x "having… recovered": fail: absorbed "recover" from outside the selection
- 1 x "having ... recovered": fail: absorbed "recover" from outside the selection
- 1 x "having recovered": fail: absorbed "recover" from outside the selection

second-example:

- 2 x "having recovered": fail: absorbed "recover" from outside the selection
- 1 x "having ... recovered": fail: absorbed "recover" from outside the selection
- 1 x "having recovered somewhat": fail: absorbed "recover" from outside the selection
- 1 x "recovered": fail: absorbed "recover" from outside the selection

turn-clause:

- 4 x "having … oneself": pass
- 1 x "having … recovered": fail: absorbed "recover" from outside the selection

### haberte-ocultado

Selection: "haberte"

no-guidance:

- 5 x "having hidden you": fail: absorbed "hid" from outside the selection

rule:

- 3 x "having hidden you": fail: absorbed "hid" from outside the selection
- 1 x "having hidden you from": fail: absorbed "hid" from outside the selection
- 1 x "have hidden you": fail: absorbed "hid" from outside the selection

rule+example:

- 3 x "having … you": pass
- 2 x "having … you hidden": fail: absorbed "hid" from outside the selection

second-example:

- 3 x "having … you": pass
- 2 x "having ... you": pass

turn-clause:

- 5 x "having … you": pass

### haberte-oido

Selection: "haberte"

no-guidance:

- 4 x "to have heard you": fail: absorbed "hear" from outside the selection
- 1 x "having heard you": fail: absorbed "hear" from outside the selection

rule:

- 4 x "to have heard you": fail: absorbed "hear" from outside the selection
- 1 x "having heard you": fail: absorbed "hear" from outside the selection

rule+example:

- 3 x "having … heard you": fail: absorbed "hear" from outside the selection
- 2 x "having … you": pass

second-example:

- 4 x "having … you": pass
- 1 x "having ... you": pass

turn-clause:

- 5 x "having … you": pass

### habiendole-herido

Selection: "habiéndole"

no-guidance:

- 2 x "having": pass
- 1 x "having … wounded": fail: absorbed "wound" from outside the selection
- 1 x "having … it": pass
- 1 x "having wounded him": fail: absorbed "wound" from outside the selection

rule:

- 2 x "having wounded him": fail: absorbed "wound" from outside the selection
- 1 x "having wounded it": fail: absorbed "wound" from outside the selection
- 1 x "having … wounded": fail: absorbed "wound" from outside the selection
- 1 x "having": pass

rule+example:

- 4 x "having … it": pass
- 1 x "having wounded it": fail: absorbed "wound" from outside the selection

second-example:

- 3 x "having … it": pass
- 2 x "having … him": pass

turn-clause:

- 5 x "having … him": pass

### habiendoles-dado

Selection: "habiéndoles"

no-guidance:

- 5 x "having given them": fail: absorbed "given" from outside the selection; absorbed "giv" from outside the selection

rule:

- 4 x "having given them": fail: absorbed "given" from outside the selection; absorbed "giv" from outside the selection
- 1 x "having … given them": fail: absorbed "given" from outside the selection; absorbed "giv" from outside the selection

rule+example:

- 3 x "having … them": pass
- 2 x "having … given them": fail: absorbed "given" from outside the selection; absorbed "giv" from outside the selection

second-example:

- 4 x "having … them": pass
- 1 x "having … given them": fail: absorbed "given" from outside the selection; absorbed "giv" from outside the selection

turn-clause:

- 5 x "having … them": pass

### habiendolo-tocado

Selection: "habiéndolo"

no-guidance:

- 5 x "having touched it": fail: absorbed "touch" from outside the selection

rule:

- 2 x "having touched it": fail: absorbed "touch" from outside the selection
- 1 x "having … touched it": fail: absorbed "touch" from outside the selection
- 1 x "having … it": pass
- 1 x "having touched him": fail: absorbed "touch" from outside the selection

rule+example:

- 5 x "having … it": pass

second-example:

- 5 x "having … it": pass

turn-clause:

- 5 x "having … it": pass

### habiendose-puesto

Selection: "Habiéndose"

no-guidance:

- 2 x "Having set": fail: absorbed "set" from outside the selection
- 2 x "having set out": fail: absorbed "set" from outside the selection
- 1 x "Having set out": fail: absorbed "set" from outside the selection

rule:

- 5 x "Having set out": fail: absorbed "set" from outside the selection

rule+example:

- 2 x "Having set out": fail: absorbed "set" from outside the selection
- 2 x "having set out": fail: absorbed "set" from outside the selection
- 1 x "Having set": fail: absorbed "set" from outside the selection

second-example:

- 3 x "having set out": fail: absorbed "set" from outside the selection
- 1 x "Having set out": fail: absorbed "set" from outside the selection
- 1 x "Having set": fail: absorbed "set" from outside the selection

turn-clause:

- 3 x "having … themselves": pass
- 1 x "having … oneself": pass
- 1 x "having …": pass

