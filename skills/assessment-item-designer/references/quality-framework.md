# Quality framework

Apply these controls as separate, auditable passes. A criterion failure must lead to revision, rejection, manual review, or escalation; never conceal it by editing the audit label. Use one or two short sentences of observable evidence per criterion. Do not ask for or store chain-of-thought.

## 1. Grounding and alignment

For every candidate verify:

- every assessed concept is supported by `scope_evidence` from authorized materials;
- `answer_evidence` supports the keyed answer or essay scoring expectations;
- a constructed scenario is self-contained and does not introduce unsupported assessed principles;
- learning outcome, item type, points, resources, Bloom target, and difficulty target correspond to the approved position;
- resource and calculation demands are feasible in the intended assessment format.

Precedence resolves compatible instructions only; it never overrides grounding requirements. A blueprint element unsupported by authorized evidence must be returned to the instructor for resolution.

Evidence entries should contain stable source locators such as document title plus page, section, slide, timestamp, or paragraph. `scope_evidence` may establish that a principle belongs to the course without asserting that the question text is copied from a source. `scenario_origin: constructed` is valid when invented details are self-contained and the assessed principle remains grounded.

## 2. Hard rejection and revision criteria

Reject or revise candidates that contain any of the following:

- course-meta, administration, scheduling, grading, or logistics questions;
- questions that test explicit syllabus wording rather than learning;
- answer options that refer to other options, such as "both A and B" or "all of the above";
- unintended dependencies on external tables, websites, software, readings, or data not authorized in the blueprint;
- trivial retrieval or formula substitution when higher cognitive demand is intended;
- calculations that cannot reasonably be performed with the approved resources, time, or response format;
- assessed concepts unsupported by authorized materials;
- more than one defensible MCQ answer or no defensible answer;
- distractors that are implausible, redundant, overlapping, or not linked to a misconception;
- grammatical agreement, option position, specificity, or answer-length clues;
- ambiguity caused by missing assumptions, undefined terms, or uncontrolled context;
- offensive, stereotyped, or construct-irrelevant cultural and language load.

Permitted resources in the approved blueprint govern resource demand. A generally useful external resource is still an unintended dependency when it was not approved.

## 3. MCQ form and answerability

An MCQ normally has four options with stable IDs such as `opt-1` through `opt-4`. Stable IDs do not change when presentation order changes. Require:

- one unambiguously best answer;
- a complete, focused stem;
- parallel, independent options;
- plausible distractors based on identifiable misconceptions;
- a concise answer rationale;
- a misconception rationale for every distractor;
- no option-to-option references;
- no hidden resource or calculation dependency.

Do not label a fixed-response MCQ as revised Bloom `Create`.

## 4. Essay form and rubric review

Require:

- a prompt that elicits observable evidence of the targeted operation;
- scope, expected length or time, permitted resources, and points;
- an answer outline that describes essential evidence without prescribing one exact wording;
- defensible alternative approaches where appropriate;
- an analytic rubric with observable criteria and distinct performance descriptors;
- criterion maxima that sum exactly to item points;
- a notice that the Isley et al. field study did not evaluate essay generation or rubrics.

Reject criteria that grade personality, effort, polish unrelated to the outcome, or unobservable mental states. Do not let language mechanics dominate unless language performance is an explicit outcome.

## 5. Target-independent Bloom and difficulty review

Use a fresh reviewer context. The reviewer sees the item and permitted resources but not target labels, generator metadata, rationales, previous verdicts, revision history, or exemplar memory. It first records:

- `reviewed_bloom` and a concise observable justification;
- `estimated_difficulty` and a concise observable justification.

Only after those fields are fixed may another comparison set `bloom_fit` and `difficulty_fit`. Follow `bloom-framework.md`. A declared target cannot serve as evidence that the target was met.

## 6. Position-aware duplication

### Same-position alternatives

Alternative candidates for the same `blueprint_position_id` are expected to assess the same construct. They do not fail solely because assessed concepts overlap substantively.

Record:

- `same_position_overlap: expected | excessive`;
- `solution_route_overlap: distinct | partial | equivalent`;
- maximum lexical similarity and compared candidate IDs;
- a short structural comparison.

Mark `same_position_overlap: excessive` when alternatives are effectively interchangeable in wording, scenario, option structure, evidence elicited, or solution process. Exact duplicates fail. Equivalent solution routes plus merely cosmetic changes normally fail. Partial solution-route overlap may pass only when the observable evidence elicited is materially different.

### Cross-position alternatives

Across different blueprint positions record:

- `cross_position_overlap: none | partial | substantive`;
- the compared position and candidate IDs;
- concept and cognitive-operation observations.

`substantive` is a failure unless the approved blueprint explicitly authorizes repeated assessment of that concept. When repetition is authorized, context-only variation is insufficient: the items must require a materially different cognitive operation or materially different evidence or solution process.

Conceptual-duplication failure therefore applies across different blueprint positions. Alternative candidates generated for the same blueprint position are expected to assess the same target construct and do not fail solely for substantive concept overlap with one another.

### Lexical layer

Deterministic lexical checks are a secondary layer:

- exact normalized duplicates fail;
- normalized lexical similarity of `0.85` or higher requires manual review;
- low lexical similarity never establishes conceptual distinctness.

The audit must state the normalization method. A recommended minimum is lowercase Unicode normalization, punctuation removal, and whitespace collapse followed by a declared similarity calculation. Lexical checks do not replace model-based comparison of concepts, evidence, and solution process.

## 7. Sequential exemplar-guided generation

For each position, generate candidate 1, judge it, update run memory, and only then generate candidate 2. Apply the same generate–judge–refresh cycle to each replacement. Never generate two same-position candidates in one model call.

After each candidate is judged, retain a bounded exemplar memory of accepted and rejected candidates. Subsequent generation calls must receive up to five accepted and five rejected examples with their verdicts, so that judge decisions influence later generation.

`calibration_exemplars` are fixed, optional, instructor-approved, and limited to five. They calibrate quality and form only; they cannot authorize a concept that is absent from the approved scope.

`run_exemplars` use rolling FIFO retention with a maximum of five accepted and five rejected entries. Store candidate ID, compact item representation, type, assessed concepts, position, verdict, and concise justification. FIFO retention is a deliberate departure from the paper's first-five approach.

## 8. Blind MCQ answer checks

Run two solution passes in genuinely fresh reviewer contexts. Each receives only:

- stem;
- options;
- permitted resources.

Neither receives the generated key, answer rationale, target or review metadata, earlier verdicts, revision history, or exemplar memory. Pass 2 receives options in a different order while stable `option_id` values remain unchanged. Compare conclusions by `option_id`, never by A/B/C/D.

Each answer reviewer records only the selected `option_id`, a short answer justification suitable for audit, and this declaration:

```yaml
review_context:
  isolation_method: fresh_reviewer_context
  isolation_verified: true
  key_visible: false
  prior_verdicts_visible: false
  rationale_visible: false
  revision_history_visible: false
  target_metadata_visible: false
```

The two answer checks and generated key must agree on the stable `option_id`. Disagreement fails automated verification and triggers revision, rejection, or instructor review.

If the environment cannot provide independent contexts, set `isolation_verified: false`, do not award an automated pass, and require instructor verification. Merely instructing the same context to "forget" is not verified isolation.

## 9. Separate final judge

Use a fresh, key-blind and history-blind final judge after the earlier passes. It may receive the approved blueprint and grounding evidence to assess scope and alignment. It must not receive the generated key, rationales, prior verdicts, revision history, or exemplar memory. It may receive independently reordered MCQ options.

The final judge determines whether the item is valid and identifies its answer or scoring expectations independently. Record the same reviewer-context declaration. A mismatch with the key or a substantive quality failure prohibits automated pass.

## 10. Candidate disposition and budgets

Candidate verdicts are `pass`, `revise`, `reject`, or `manual_review`.

- `pass`: all hard requirements meet their declared disposition; isolation is verified; no unresolved manual check remains.
- `revise`: a correctable defect exists and revision budget remains.
- `reject`: a hard defect or exhausted candidate path makes revision inappropriate.
- `manual_review`: an instructor must decide, including when isolation is not verified or lexical similarity is at least 0.85 without an approved resolution.

Allow two initial candidates plus at most two fresh replacements per position, and at most two revisions per candidate. Escalate after exhaustion. A replacement is a fresh candidate, not revision number three.

## 11. Assessment-level duplication and assembly

After selecting one passed item per position, ignore unselected alternatives and run a new pass across selected items only:

1. compare every cross-position pair conceptually;
2. recompute lexical similarity;
3. confirm authorized repetitions require materially different cognition or evidence/solution process;
4. replace a failing selected item using a passed alternative from the same position;
5. rerun the complete selected-set pass after every replacement;
6. escalate when no valid combination exists.

The audit must record comparison pairs, overlap classifications, lexical values, repetition authorization, material-distinction disposition, replacement history, run count, and final status.

Then verify one item per position, no extras, exact points, requested item-type distribution, target-fit policy, permitted resources, and all answer-key references. Final delivery still requires instructor approval.
