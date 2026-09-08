# Quality framework

Apply these controls as separate, auditable passes. A criterion failure must lead to revision, rejection, manual review, or escalation; never conceal it by editing the audit label. Use one or two short sentences of observable evidence per criterion. Do not ask for or store chain-of-thought.

This file is the canonical MCQ quality gate. Source keys `[S1]` through `[S5]` refer to the full citations and evidence boundaries in [research-basis.md](research-basis.md#mcq-item-writing-evidence). They support general item-writing guidance; they do not extend the empirical claims of Isley et al. (2025).

## Subagent execution contract

For each candidate, use four distinct fresh subagents for MCQs (classification, answer solver 1, answer solver 2, final judge) or two for essays (classification and final judge). Start every review with no inherited conversation history; with Codex collaboration tools use `spawn_agent` with `fork_turns: "none"`. Here history means earlier task dialogue, not baseline system/developer instructions or profile/environment context supplied by the host. If that baseline itself exposes prohibited assessment information, isolation is unverified. Never reuse a reviewer for another role, candidate, or revision. Discard earlier reviews after an item changes and review the revised item with new subagents.

The coordinator constructs minimal review packets rather than passing the complete candidate, audit, skill, or conversation. Reviewers must use only their supplied packet, must not inspect workspace files or contact other agents, and must return a result plus a concise observable justification. A shared workspace is not a security sandbox: if prohibited information is accessed or history inheritance cannot be ruled out, mark isolation unverified. Do not claim technical access isolation merely because a separate agent was started.

- Classification: item prompt/stem, options when present, and permitted resources only. No answer outline, rubric, keys, rationales, exemplar memory, target labels, or prior results. Return Bloom, estimated difficulty, confidence and a concise basis before the coordinator compares them with targets. Approved historical or calibration items may inform difficulty after Bloom is fixed; redact keys and target labels for the current candidate and do not reveal run-exemplar verdicts. Cite comparator source locators in the difficulty basis; comparators never expand scope.
- Answer solvers: stem, stable option IDs and text, and permitted resources only. Solver 2 receives an order different from both the displayed original and solver 1. Return the chosen option ID and a short answer justification.
- Final judge: item, permitted resources, relevant authorized grounding evidence, and the approved position's scope, outcome, points and constraints. Remove target Bloom/difficulty labels and all keys, answer outlines, rubrics, rationales, exemplar memory, and earlier results. For essays, independently establish scoring expectations; the coordinator then checks the generated outline and rubric against those expectations.

Run the final judge after the preceding reviews, without revealing their results. Reviews may run sequentially to respect agent limits; dispose of completed reviewer sessions when the runtime supports it. Never weaken isolation to work around capacity limits. Preserve the generate–judge–refresh sequence between candidates.

Record the actual returned agent ID, `history_inherited: false`, `isolation_method: fresh_subagent`, and the visibility declarations for each call. Agent IDs must be unique across the audit's independent review calls. Keep concise evidence of the supplied packet and returned result in the run record, without storing chain-of-thought. The coordinator verifies declarations against real calls; the JSON validator cannot establish their truth. Audit `reviewer_id` labels are not substitutes for runtime agent IDs.

If a call cannot run or completes with unverified isolation, retain an unresolved escalation and a non-passing candidate. Do not fabricate an agent ID or result. Resume using new subagents when available. Instructor approval never waives mandatory review; manual review remains available for substantive issues such as flagged lexical similarity.

## 1. Grounding and alignment

For every candidate verify:

- every assessed concept is supported by `scope_evidence` from authorized materials;
- `answer_evidence` supports the keyed answer or essay scoring expectations;
- a constructed scenario is self-contained and does not introduce unsupported assessed principles;
- the item assesses the intended learning outcome and its actual cognitive operation fits that outcome;
- item type, points, resources, Bloom target, and difficulty target correspond to the approved position;
- resource and calculation demands are feasible in the intended assessment format.

Difficulty must come from construct-relevant subject knowledge or reasoning, not confusing wording, irrelevant reading load, or test-taking tricks. `[S1, S3, S4]`

Precedence resolves compatible instructions only; it never overrides grounding requirements. A blueprint element unsupported by authorized evidence must be returned to the instructor for resolution.

Evidence entries should contain stable source locators such as document title plus page, section, slide, timestamp, or paragraph. `scope_evidence` may establish that a principle belongs to the course without asserting that the question text is copied from a source. `scenario_origin: constructed` is valid when invented details are self-contained and the assessed principle remains grounded.

## 2. Hard rejection and revision criteria

Reject or revise candidates that contain any of the following:

- course-meta, administration, scheduling, grading, or logistics questions;
- questions that test explicit syllabus wording rather than learning;
- answer options that refer to other options, such as "both A and B";
- unintended dependencies on external tables, websites, software, readings, or data not authorized in the blueprint;
- trivial retrieval or formula substitution when higher cognitive demand is intended;
- calculations that cannot reasonably be performed with the approved resources, time, or response format;
- assessed concepts unsupported by authorized materials;
- more than one defensible MCQ answer or no defensible answer;
- distractors that are implausible, redundant, overlapping, outside the correct answer's conceptual category, or not linked to a realistic misconception;
- grammatical, lexical, logical, option-position, specificity, or answer-length clues;
- `all of the above`, `none of the above`, or complex answer combinations;
- ambiguity caused by missing assumptions, undefined terms, or uncontrolled context;
- offensive, stereotyped, or construct-irrelevant cultural and language load.

Permitted resources in the approved blueprint govern resource demand. A generally useful external resource is still an unintended dependency when it was not approved.

## 3. Canonical MCQ quality gate

Default to three strong options with stable IDs such as `opt-1` through `opt-3`. Stable IDs do not change when presentation order changes. Use more than three options only when every distractor meets the criteria below or the approved blueprint requires the additional options. Never add an implausible distractor merely to reach an option count. `[S2]`

### Alignment

- The item assesses the intended learning outcome.
- The cognitive operation required by the item matches that outcome.
- Difficulty comes from subject knowledge or reasoning, not confusing wording or test-taking tricks. `[S1, S3, S4]`

### Stem

- Present one clear, self-contained problem.
- Make the task understandable before the options are read.
- Use concise, precise, and unambiguous wording.
- Include only information relevant to solving the problem.
- Avoid negative wording such as **NOT** or **EXCEPT** unless it is necessary; when used, make it visually conspicuous and justify it in the audit. `[S1, S3, S5]`

### One best answer

- Exactly one option is clearly the best answer.
- The answer is defensible from the information and permitted resources provided.
- No unstated assumption is needed.
- The answer should remain the same under competent subject-matter review. `[S1, S5]`

Reject the item if multiple options are equally defensible or no option is correct.

### Distractors

Every distractor must:

- be incorrect but plausible;
- represent a realistic misconception, error, or incomplete understanding where possible;
- belong to the same conceptual category as the correct answer;
- require relevant subject knowledge to eliminate. `[S1, S3, S4]`

Record a concise misconception rationale for every distractor. Prefer three strong options in total over four or five options containing weak distractors. `[S2]`

### Option quality

- Options are mutually exclusive and do not overlap.
- Options use parallel grammar and similar levels of detail.
- The correct answer is not noticeably longer, more precise, or more qualified.
- No grammatical, lexical, logical, or positional clue reveals the answer.
- Do not use `all of the above`, `none of the above`, option-to-option references, or complex answer combinations. `[S1, S3, S4]`

### Fairness

- The item measures the intended construct rather than unnecessary reading complexity, cultural knowledge, or test-wiseness.
- Context and examples do not introduce irrelevant difficulty. `[S1, S4]`

Do not label a fixed-response MCQ as revised Bloom `Create`. Require a concise answer rationale and no hidden resource or calculation dependency.

### Review priority

Fix problems in this order:

1. learning-outcome alignment;
2. cognitive level;
3. clarity of the problem;
4. one-best-answer requirement;
5. distractor quality;
6. unintended cues;
7. wording and style.

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

Use a fresh classification subagent under the execution contract above. The reviewer sees the item and permitted resources but not target labels, generator metadata, rationales, previous verdicts, revision history, or exemplar memory. It first records:

- `reviewed_bloom` and a concise observable justification;
- `estimated_difficulty`, `difficulty_confidence`, `difficulty_basis` and a concise observable justification. Confidence is an uncalibrated design judgment, not an empirical probability.

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

Use three independent rolling FIFO windows, each capped at five, ordered from oldest to newest:

- **accepted (`pass`)**: patterns worth emulating;
- **revisable (`revise`)**: preserve the useful core (`retain`) and avoid or repair the identified defect (`correct`). A distractor or wording defect does not make an authorized concept undesirable;
- **rejected (`reject`)**: patterns or approaches to avoid, supported by a concise reason.

Unresolved `manual_review` candidates enter none of these windows. The coordinator still records that their judgment occurred; this is process state, not a negative training example. A human can later resolve the verdict to pass, revise or reject with recorded provenance, provided the full item content is unchanged. A changed distractor, answer rationale or rubric requires a new revision and fresh independent reviews. Such a resolution cannot waive grounding, mandatory independent review or other pass requirements.

Append judgments to `exemplar_registries.judgment_history`. New candidates, revised versions and human resolutions are separate immutable events. When a candidate receives a new verdict, remove its superseded entry from any retained window and append its current version to the appropriate window (or none for manual_review). Evict the oldest entry only when that category exceeds five. Never retroactively alter earlier generation packets or recategorize their historical examples.

Each generation call receives the exact windows as they stood immediately before generation. For a new candidate, record that history boundary in `exemplar_context.after_event_index`. For revisions, reconstruct the input windows from the prefix immediately before the new revision's judgment event. Preserve each event's complete item snapshot, summary, feedback and verdict so later mutation of the candidate cannot rewrite the earlier evidence. Generate and judge sequentially; no intervening judgment may occur between a generation call and its verdict.

`calibration_exemplars` are fixed, optional, instructor-approved and limited to five. They can inform form, quality and difficulty but cannot authorize an out-of-scope concept. Supply this registry alongside all three run-memory windows. FIFO and the revisable category are extensions of the paper's first-five good/bad examples. See `output-contract.md` for the canonical audit fields.

## 8. Blind MCQ answer checks

Run two solution passes with separate fresh subagents under the execution contract above. Each receives only:

- stem;
- options;
- permitted resources.

Neither receives the generated key, answer rationale, target or review metadata, earlier verdicts, revision history, or exemplar memory. Pass 2 receives options in a different order while stable `option_id` values remain unchanged. Compare conclusions by `option_id`, never by A/B/C/D.

Each answer reviewer records only the selected `option_id`, a short answer justification suitable for audit, and this declaration:

```yaml
review_context:
  isolation_method: fresh_subagent
  agent_id: actual-runtime-agent-id
  history_inherited: false
  isolation_verified: true
  key_visible: false
  prior_verdicts_visible: false
  rationale_visible: false
  revision_history_visible: false
  target_metadata_visible: false
```

The two answer checks and generated key must agree on the stable `option_id`. Disagreement fails automated verification and triggers revision, rejection, or instructor review.

If fresh subagents are unavailable, set `isolation_verified: false`, retain an unresolved escalation, and block approval and delivery until the required reviews are completed. Instructor verification cannot replace them. Asking the same context to "forget" is not isolation.

## 9. Separate final judge

Use a fresh, key-blind and history-blind final-judge subagent after the earlier passes. It may receive a redacted approved blueprint (without Bloom/difficulty target labels) and grounding evidence to assess scope and alignment. It must not receive the generated key, rationales, prior verdicts, revision history, or exemplar memory. It may receive independently reordered MCQ options.

The final judge determines whether the item is valid and identifies its answer or scoring expectations independently. Record the same reviewer-context declaration. A mismatch with the key or a substantive quality failure prohibits automated pass.

## 10. Candidate disposition and budgets

Candidate verdicts are `pass`, `revise`, `reject`, or `manual_review`.

- `pass` (**GOOD**): all critical criteria and Bloom fit are satisfied, isolation is verified, and no unresolved manual check remains. Difficulty may be `aligned` or `adjacent_uncertain`; the latter must be disclosed during final instructor review.
- `revise` (**REVISE**): the learning objective and core question are valid, but a correctable stem or option defect exists and revision budget remains.
- `reject` (**REJECT**): alignment or cognitive level is wrong; the item is ambiguous; multiple answers are defensible; no answer is correct; distractors are predominantly implausible; strong unintended cues remain; or an exhausted candidate path makes revision inappropriate.
- `manual_review`: an instructor must decide, for substantive issues such as lexical similarity of at least 0.85 without an approved resolution, or a difficulty disposition requiring review. Missing subagent isolation remains blocked until fresh independent reviews complete; a manual decision cannot waive it.

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
