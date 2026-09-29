# Review of the passing answers

The scores in each `report.md` come from substring checks. A substring check can pass an
answer that breaks the rule, when the answer fails in a way the check did not name. So every
passing answer of experiments 1 and 2 was read against its sentence in a second pass, and the
ones below were judged to break the rule although they passed.

The second pass was done by a model, Claude Fable 5.1, which is a stronger model than the two
under test. It is a review, not the score: every judged row is listed here with its reason, so
each one can be checked by reading it.

Only clear cases are counted: a content word that comes from outside the selection, or
content inside the selection that is missing. Two kinds of answer were read as borderline
and left as passes: a subject pronoun English needs for a finite verb ("she put on an
apron"), and a lone function word ("for fear that").

The checks of experiments 1 and 2 were not edited after the answers were seen, so the recorded
scores stand as scored. The tables in the README give both counts.

Experiment 3, in `2026-09-29-phrases-haiku`, had no such pass. Its answers were read one by one
by a model, which led to one amended check, but its passes were not judged row by row as below.
The README gives its counts as first scored and under the amended check.

## 2026-09-29-marks-haiku

| Arm | Scored passes | Judged to break the rule | After review |
|---|---:|---:|---:|
| unmarked | 62/95 | 8 | 54/95 |
| marked | 86/95 | 2 | 84/95 |

| Arm | Case | Answer | Trials | Why it breaks the rule |
|---|---|---|---:|---|
| unmarked | sin-embargo-miradas-connective | "however" | 3 | drops everything after the connective; the check asks only for the connective |
| unmarked | generoso-dijo-muchacho-whole-sentence | "generous" | 3 | drops the speech tag and the verb; the check only excludes words from outside |
| unmarked | generoso-dijo-muchacho-whole-sentence | "Since you're so generous" | 2 | drops the speech tag and the verb, and absorbs the words before the selection |
| marked | generoso-dijo-muchacho-whole-sentence | "you're so generous," said the boy, "I'll stop" | 1 | absorbs the words before the selection |
| marked | tras-uno-tras-otro-particle | "one after the other" | 1 | the whole phrase again; the check names "another", not "the other" |

## 2026-09-29-marks-sonnet

| Arm | Scored passes | Judged to break the rule | After review |
|---|---:|---:|---:|
| unmarked | 95/95 | 0 | 95/95 |
| marked | 95/95 | 0 | 95/95 |

No passing answer was judged to break the rule.

## 2026-09-29-guidance-haiku

| Arm | Scored passes | Judged to break the rule | After review |
|---|---:|---:|---:|
| no-guidance | 18/80 | 4 | 14/80 |
| rule | 12/80 | 5 | 7/80 |
| rule+example | 36/80 | 1 | 35/80 |
| second-example | 50/80 | 0 | 50/80 |
| turn-clause | 76/80 | 0 | 76/80 |

| Arm | Case | Answer | Trials | Why it breaks the rule |
|---|---|---|---:|---|
| no-guidance | haberle-cogido | "having stolen from her" | 2 | absorbs the clause that follows the participle |
| no-guidance | haberle-cogido | "having stolen from him" | 1 | absorbs the clause that follows the participle |
| no-guidance | haberle-cogido | "having taken" | 1 | absorbs a verb; the check lists caught, catch, found |
| rule | haberle-cogido | "having… taken" | 1 | absorbs a verb; the check lists caught, catch, found |
| rule | haberle-cogido | "having taken from her" | 1 | absorbs the clause that follows the participle |
| rule | haberle-cogido | "having … taken" | 1 | absorbs a verb; the check lists caught, catch, found |
| rule | haberle-cogido | "having... taken" | 1 | absorbs a verb; the check lists caught, catch, found |
| rule | haberle-cogido | "having stolen from her" | 1 | absorbs the clause that follows the participle |
| rule+example | haberle-cogido | "having … taken it" | 1 | absorbs a verb; the check lists caught, catch, found |
