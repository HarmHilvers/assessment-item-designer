---
name: assessment-item-designer
description: Create or review grounded multiple-choice and essay assessment items through an approved blueprint, revised Bloom targets, sequential exemplar-guided candidate generation, isolated answer checks, duplication control, deterministic audit validation, and mandatory instructor approval. Use when asked to design an exam, test, quiz, MCQs, essay questions, answer keys, assessment blueprints, or to quality-review existing assessment items.
---

# Assessment Item Designer

Release designation: **2026.1**. Manifest version: **2026.1.0**.

Use this skill to create or review assessment items. Work in small, visible stages. Fail closed when grounding, reviewer isolation, selection integrity, or instructor approval cannot be established. The skill's instructions and audit keys are English; the assessment may use the instructor's requested language.

Before doing substantive work, read all four references:

1. [Research basis](references/research-basis.md)
2. [Quality framework](references/quality-framework.md)
3. [Bloom framework](references/bloom-framework.md)
4. [Output contract](references/output-contract.md)

Do not present this workflow as a replication of Isley et al. (2025). It is an extension of their iterative generation-and-judging architecture. Never request or store chain-of-thought; record concise, criterion-level observations instead.

## Non-negotiable invariants

- Ground every assessed concept in authorized evidence.
- Precedence resolves compatible instructions only; it never overrides grounding requirements. A blueprint element unsupported by authorized evidence must be returned to the instructor for resolution.
- Require instructor approval of the blueprint before generation or revision.
- Give every final item a stable `blueprint_position_id`.
- Generate and judge candidates sequentially, never as a same-position batch.
- Refresh `run_exemplars` after every candidate verdict and supply the refreshed memory to the next generation call.
- Keep targets separate from independent review results.
- For MCQs, use two fresh, isolated, key-blind answer checks and a separate key-blind, history-blind final judge.
- Do not award an automated pass if reviewer isolation cannot be verified.
- Apply position-aware duplication rules during candidate review and a new selected-set duplication pass before final assembly.
- Enforce generation and revision budgets.
- Require final instructor approval before delivery.

## Stage 1 — Intake and grounding

Accept either an assessment blueprint or learning outcomes plus authorized course materials. Collect or infer only when safe:

- audience and assessment language;
- item types and counts;
- points;
- learning outcomes and assessed concepts;
- `target_bloom` and `target_difficulty`;
- permitted resources and calculation format;
- concept-repetition policy.

Apply this precedence only after the grounding invariant:

1. explicit user constraints;
2. approved blueprint;
3. learning outcomes;
4. course materials.

For every position and candidate record:

- `scope_evidence`: why the assessed concept belongs in scope;
- `answer_evidence`: what supports the correct answer or scoring expectations;
- `scenario_origin`: `source_derived`, `constructed`, `mixed`, or `not_applicable`.

A constructed scenario may contain invented, self-contained details, but its assessed principles must remain grounded. Return unsupported blueprint elements to the instructor; do not silently repair them with outside subject matter.

## Stage 2 — Build and approve the blueprint

Create one stable position for every required final item. Each position must specify:

- `blueprint_position_id`;
- learning outcome;
- `assessed_concepts`;
- item type;
- `target_bloom`;
- `target_difficulty`;
- points;
- permitted resources;
- repetition policy.

Save the result as `blueprint.md` and request explicit instructor approval. Do not proceed while its status is provisional or unresolved.

For review of an existing assessment without a blueprint, first construct a `provisional_review_blueprint` from the outcomes, materials, and existing assessment. Mark every derived field `inferred`. Obtain instructor approval before revising any item.

## Stage 3 — Register exemplars

Maintain two distinct registries:

- `calibration_exemplars`: optional, fixed for the run, instructor-approved, maximum five. They calibrate form and quality only and cannot expand content scope.
- `run_exemplars`: rolling FIFO memory, maximum five accepted and five rejected candidates. Each entry includes the item, type, concepts, position, verdict, and a short observable justification.

Supply both registries to each generation call. FIFO run memory is an explicit departure from the paper's first-five run examples.

## Stage 4 — Generate candidates sequentially

For each blueprint position, execute this exact cycle:

1. Generate candidate 1.
2. Judge it and refresh run memory.
3. Generate candidate 2 using refreshed run memory.
4. Judge it and refresh run memory.
5. If necessary, generate and judge replacement 1, then refresh memory.
6. If necessary, generate and judge replacement 2, then refresh memory.
7. Escalate if none passes.

Budgets per position:

- two initial candidates;
- no more than two fresh replacement candidates;
- no more than two revisions of any candidate.

Do not hide budget exhaustion by renaming a revision or restarting a position.

Every candidate must record its position, evidence, scenario origin, assessed concepts, `concept_signature`, targets, independent review results, fit results, overlap results, exemplar context, reviewer-context declarations, revision and replacement counts, verdict, and selection status.

MCQs normally contain four stable `option_id` values, exactly one keyed option, an answer rationale, and one misconception rationale for each distractor. Essays contain an answer outline, defensible alternatives, an observable analytic rubric with reconciled points, and a notice that the essay workflow is not empirically validated by Isley et al. (2025).

## Stage 5 — Judge each candidate

Run distinct review passes described in `quality-framework.md`:

1. grounding and blueprint alignment;
2. independent Bloom and difficulty review;
3. item-form and fairness review;
4. position-aware conceptual and lexical duplication review;
5. two isolated blind answer checks for MCQs;
6. separate final judge.

The Bloom/difficulty reviewer must not see targets or generator metadata. Reveal `reviewed_bloom` and `estimated_difficulty` before comparing them with targets and setting `bloom_fit` and `difficulty_fit`.

The two MCQ answer solvers see only stem, options, and permitted resources. Solver 2 receives reordered options. Compare conclusions using stable `option_id`, never letters. The final judge is key-blind and history-blind. Record the required `review_context` declaration for every isolated pass.

If fresh reviewer contexts are unavailable, record `isolation_verified: false`, prohibit an automated pass, and require instructor verification.

## Stage 6 — Select and validate the assessment

Select one passed candidate for every approved blueprint position. Then run a fresh assessment-level duplication pass over selected items only:

1. recompute cross-position conceptual overlap;
2. check exact and normalized lexical similarity;
3. verify that authorized concept repetition uses materially different cognition or evidence/solution process;
4. replace a failure with another passed candidate from the same position;
5. rerun the entire selected-set duplication pass;
6. escalate when no valid replacement exists.

Finally verify exact blueprint coverage, Bloom distribution, difficulty distribution, item types, resources, and points. Validate `quality-audit.json` with `scripts/validate_audit.py`. Validation checks declared structure and invariants; it does not prove semantic judgments true.

## Stage 7 — Instructor approval and delivery

Produce:

- `blueprint.md`;
- `assessment.md`;
- `answer-key.md`;
- `quality-audit.json`.

Ask the instructor for final approval. Do not describe unapproved material as ready for administration. Keep answer material separate from the student-facing assessment. Report unresolved escalations prominently.

The audit must state release `2026.1`, manifest version `2026.1.0`, the Isley et al. citation, empirical limitations, blueprint status, exemplar registries, budgets, final selected-set duplication result, and escalations.

## Review mode

For an existing assessment, preserve original item IDs and source text in the audit. Diagnose before revising. If no approved blueprint exists, stop after the provisional blueprint until the instructor approves it. Apply the same grounding, isolated-review, duplication, budget, and approval controls to proposed replacements.

## Validation command

Run:

```bash
python3 scripts/validate_audit.py quality-audit.json
```

Use `--self-test` to run the included valid and invalid fixture tests. A successful structural validation is necessary but never substitutes for instructor judgment or post-administration psychometrics.
