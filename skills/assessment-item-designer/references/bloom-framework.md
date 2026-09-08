# Revised Bloom framework

Use revised Bloom taxonomy to describe the highest cognitive operation that the student must actually perform, not the verb printed in the stem and not the generator's metadata.

## Levels

### Remember

Retrieve a fact, term, definition, rule, or previously learned procedure with no meaningful transformation.

Observable signals: name, recognize, recall, identify a directly taught fact.

### Understand

Explain meaning, classify, summarize, interpret, exemplify, or infer a direct implication.

Observable signals: paraphrase an idea, categorize an example, explain a relationship in familiar terms.

### Apply

Use a known procedure or principle in a concrete situation. The student must select or execute the relevant method, not merely substitute values into an explicitly supplied formula.

Observable signals: choose and apply a method, implement a rule in a case, calculate after determining the needed procedure.

### Analyze

Differentiate, organize, attribute, compare structures, or determine how evidence, assumptions, and parts relate.

Observable signals: distinguish competing explanations using criteria, diagnose a case, infer which relationship accounts for an outcome, decompose a complex argument.

### Evaluate

Judge a claim, option, design, or course of action against explicit or defensible criteria, normally requiring justification.

Observable signals: critique evidence, prioritize alternatives using criteria, assess trade-offs, defend a judgment.

### Create

Generate, plan, or produce a coherent new product or solution by integrating elements. Do not classify a fixed-response MCQ as `Create`, even if it asks which created product would be best. The student is selecting, not creating.

Observable signals: design an intervention, construct an argument, formulate a plan, produce an original synthesis.

## Independent review procedure

Use a fresh classification subagent, distinct from answer solvers and the final judge, without inherited history, following the subagent execution contract in `quality-framework.md`. The reviewer receives only the student-facing item content and permitted resources, but not:

- `target_bloom`;
- `target_difficulty`;
- generator labels, rationale, answer key, answer outline, or rubric;

- earlier verdicts or revision history;
- exemplar memory.

The reviewer records `reviewed_bloom` first, with one or two short sentences citing observable task demands. Only then compare it with `target_bloom` and set `bloom_fit: pass | fail`.

Do not infer level from a single command verb. Consider what information the item supplies, whether answer options reveal the needed reasoning, and the minimum cognitive process sufficient for a well-prepared student to answer correctly.

## Difficulty estimate and confidence

Difficulty is related to, but not determined by, Bloom. Record `estimated_difficulty: Easy | Medium | Hard`, `difficulty_confidence: low | medium | high`, and `difficulty_basis` (one or two sentences, maximum 500 characters) before revealing the current item's target. The basis should name observable features and assumptions, for example reasoning depth, inferential steps, context familiarity, scaffolding or calculation burden. Confidence itself is not empirically calibrated.

Use these approximate anchors independently of Bloom:

- **Easy:** familiar context, few dependent steps, substantial scaffolding.
- **Medium:** several linked steps, some integration, limited scaffolding.
- **Hard:** extended dependencies, unfamiliar applications or integration across concepts.

A poorly worded item can be hard for irrelevant reasons; that is a quality defect. Neither a Bloom label nor a command verb determines difficulty.

After independently fixing Bloom, the same classification reviewer may use instructor-approved calibration examples, historical instructor questions or comparable administered items to strengthen the difficulty basis. Describe the comparison and cite supplied source locators. Separate empirical observations about those historical items from estimates about the new candidate. These examples must not reveal the current target or expand assessment scope. Sparse or indirect evidence generally warrants lower confidence; no confidence level guarantees correctness.

## Canonical target-fit policy

The coordinator compares the fixed review results with the approved targets. Bloom fit remains `pass | fail` and follows the blueprint's explicit acceptable range, or exact category fit when none is specified. A higher reviewed Bloom level is not automatically better.

Difficulty fit is a design disposition, never a psychometric pass/fail measurement:

| Declared target versus estimate | Confidence | `difficulty_fit` | Consequence |
| --- | --- | --- | --- |
| Same category | Any | `aligned` | Eligible if all other controls pass |
| Adjacent categories | low or medium | `adjacent_uncertain` | May be selected; explicitly flag the uncertainty for final instructor review |
| Adjacent categories | high | `review_required` | No pass yet; seek instructor clarification or revise and independently reassess |
| Easy versus Hard | Any | `mismatch` | No pass; revise or resolve the target with the instructor |

For `review_required` or `mismatch`, record `manual_review` when seeking instructor target clarification, `revise` when changing the item, or `reject` when abandoning the candidate. The unchanged-item target-resolution route starts from `manual_review`; revise/reject are not silently relabeled as passes. A human discussion alone does not relabel the estimate or turn a failed disposition into a pass: revise and reassess, or explicitly reapprove the blueprint target and recompute fit while retaining the independent estimate and the change record. All cases remain subject to substantive quality controls and final instructor approval.

List selected `adjacent_uncertain` candidates in the final audit's `difficulty_caveat_candidate_ids` and explain the uncertainty in the instructor-facing material. Verify intended target coverage separately from the distribution of estimates.

Model-estimated difficulty is a pre-administration judgment. Release 2026.6 does not implement student-response analysis or IRT estimation; all claims that its estimates or confidence are empirical/calibrated remain false. Actual post-administration item difficulty or IRT parameters require student-response data and a separate documented analysis. Deterministic validation checks these declarations and comparison consistency, not semantic truth.
