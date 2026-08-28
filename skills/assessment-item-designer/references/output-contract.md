# Output and audit contract

Produce four files in the instructor's chosen output directory. Keep all audit field names in English even when the assessment language is not English.

## `blueprint.md`

Include:

- assessment purpose, audience, language, timing, and permitted resources;
- authorized materials with stable locators;
- every `blueprint_position_id` and its learning outcome, `assessed_concepts`, item type, `target_bloom`, `target_difficulty`, points, permitted resources, and repetition policy;
- expected distribution totals;
- unsupported or unresolved elements;
- approval status, approver, and timestamp.

For review without an existing blueprint, label it `provisional_review_blueprint`, mark derived fields `inferred`, and stop before revision until the instructor approves it.

## `assessment.md`

Contain student-facing instructions and selected items only. Preserve stable item IDs but omit keys, rationales, review labels, and audit metadata. Declare permitted resources and point values clearly. Use the requested language.

## `answer-key.md`

For MCQs, map item IDs to stable `option_id`, presentation label, answer text, answer rationale, and source locator. For essays, include the answer outline, defensible alternatives, analytic rubric, and reconciled points. Keep the key separate from `assessment.md`.

## `quality-audit.json`

Use valid UTF-8 JSON. The canonical top-level shape is:

```json
{
  "schema_version": "2026.2",
  "workflow_status": "awaiting_final_approval",
  "metadata": {},
  "blueprint": {},
  "exemplar_registries": {},
  "generation_budget": {},
  "candidates": [],
  "final_selection": {},
  "escalations": [],
  "instructor_approval": {}
}
```

### Metadata

Required fields:

```json
{
  "release": "2026.2",
  "manifest_version": "2026.2.0",
  "assessment_language": "en",
  "created_at": "ISO-8601 timestamp",
  "research_basis": {
    "citation": "Isley, C. et al. (2025). Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study. arXiv:2508.08314v1.",
    "extension_not_replication": true,
    "direct_empirical_scope": "short college-level multiple-choice items",
    "essay_workflow_empirically_validated": false,
    "model_difficulty_is_irt": false,
    "post_administration_psychometrics_included": false
  }
}
```

### Blueprint

Required structure:

```json
{
  "kind": "approved_blueprint",
  "status": "approved",
  "positions": [
    {
      "blueprint_position_id": "BP-01",
      "learning_outcome": "...",
      "assessed_concepts": ["..."],
      "item_type": "mcq",
      "target_bloom": "Apply",
      "target_difficulty": "Medium",
      "points": 2,
      "permitted_resources": ["none"],
      "repetition_policy": {
        "concept_repetition_authorized": false,
        "authorized_with_positions": []
      },
      "field_provenance": "provided"
    }
  ]
}
```

`kind` may be `approved_blueprint` or `provisional_review_blueprint`; generation and revision require `status: approved`. `field_provenance` is `provided`, `inferred`, or `mixed`.

### Exemplar registries

```json
{
  "calibration_exemplars": [
    {
      "exemplar_id": "CAL-01",
      "instructor_approved": true,
      "scope_expansion_allowed": false
    }
  ],
  "run_exemplars": {
    "retention_policy": "rolling_fifo",
    "accepted": [],
    "rejected": []
  }
}
```

There may be at most five calibration examples, five retained accepted examples, and five retained rejected examples. Each run entry contains `candidate_id`, `item_summary`, `item_type`, `assessed_concepts`, `blueprint_position_id`, `verdict`, and `justification`.

### Generation budget

Declare:

```json
{
  "initial_candidates_per_position": 2,
  "fresh_replacements_per_position": 2,
  "max_revisions_per_candidate": 2,
  "sequential_generation_required": true
}
```

### Candidate records

Each record requires:

```json
{
  "candidate_id": "BP-01-C1",
  "blueprint_position_id": "BP-01",
  "generation_index": 1,
  "position_sequence": 1,
  "candidate_kind": "initial",
  "replacement_number": 0,
  "revision_count": 0,
  "item_type": "mcq",
  "item": {},
  "scope_evidence": [],
  "answer_evidence": [],
  "scenario_origin": "constructed",
  "assessed_concepts": [],
  "concept_signature": "...",
  "target_bloom": "Apply",
  "reviewed_bloom": "Apply",
  "bloom_fit": "pass",
  "bloom_justification": "...",
  "target_difficulty": "Medium",
  "estimated_difficulty": "Medium",
  "difficulty_fit": "pass",
  "difficulty_justification": "...",
  "classification_review_context": {},
  "classification_revealed_before_target_comparison": true,
  "duplication": {},
  "exemplar_context": {},
  "rejection_checks": [],
  "blind_answer_checks": [],
  "final_judge": {},
  "verdict": "pass",
  "selected": true,
  "final_status": "selected"
}
```

Evidence entries require `source_id`, `locator`, and `supports`. Constructed scenario details need not pretend to be quoted from a source, but assessed principles still require evidence.

For `item_type: mcq`, `item` contains `stem`, `options`, `correct_option_id`, and `answer_rationale`. Each option contains stable `option_id`, `text`, and `misconception_rationale`; the correct option may use `null` for its misconception rationale. Default to three strong options. Use more only when every distractor is genuinely plausible or the approved blueprint requires it; never pad with weak distractors. `correct_option_id` must identify exactly one option.

For `item_type: essay`, `item` contains `prompt`, `answer_outline`, `defensible_alternatives`, `rubric`, and `empirical_limitation_notice`. Each rubric criterion has `criterion_id`, `criterion`, `max_points`, and observable `levels`; criterion maxima must equal the blueprint position points.

Targets and review results are always separate. Use revised Bloom values `Remember`, `Understand`, `Apply`, `Analyze`, `Evaluate`, or `Create`; an MCQ cannot be `Create`. Difficulty values are `Easy`, `Medium`, or `Hard`. Fits are `pass` or `fail`.

`classification_review_context` uses the isolated context declaration below. `classification_revealed_before_target_comparison: true` declares that `reviewed_bloom` and `estimated_difficulty` were recorded before the targets were revealed and fit was calculated. A passing candidate requires both fit fields to pass. A non-passing candidate may retain different reviewed and target values as evidence of a genuine independent review.

`duplication` contains:

```json
{
  "same_position_overlap": "expected",
  "cross_position_overlap": "none",
  "solution_route_overlap": "distinct",
  "max_lexical_similarity": 0.21,
  "lexical_method": "declared normalization and similarity method",
  "compared_candidate_ids": [],
  "manual_review_required": false,
  "manual_review_disposition": "not_required"
}
```

Same-position `expected` does not fail solely for construct overlap. Same-position `excessive`, exact duplication, or an equivalent solution route must not receive an automated pass. Cross-position `substantive` must not pass unless blueprint repetition is authorized and the audit records `materially_distinct_cognition_or_evidence: true`. Similarity at or above `0.85` requires a resolved manual review.

`exemplar_context` contains `calibration_ids`, `accepted_run_ids`, `rejected_run_ids`, and `preceding_same_position_candidate_id`. Candidate 1 uses `null` for the preceding candidate. Each later same-position candidate must name the immediately preceding one, and that ID must occur in its accepted or rejected run IDs. Lists are capped at five each.

Each entry in `rejection_checks` contains `criterion`, `result: pass | fail | not_applicable`, and `justification`. Use these required criterion IDs:

- `course_meta_or_logistics`;
- `explicit_syllabus_wording`;
- `option_to_option_references`;
- `unintended_external_dependencies`;
- `trivial_retrieval_or_formula_substitution`;
- `resource_demands_match_blueprint`;
- `unsupported_concepts`;
- `learning_outcome_alignment`;
- `cognitive_level_alignment`;
- `construct_relevant_difficulty`;
- `stem_clarity_and_self_containment`;
- `stem_task_understandable_before_options`;
- `stem_relevance_and_concision`;
- `negative_wording_justified`;
- `one_best_answer`;
- `answer_defensible_without_unstated_assumptions`;
- `distractor_quality`;
- `option_mutual_exclusivity`;
- `option_parallelism`;
- `answer_clues`;
- `complex_option_formats_absent`;
- `fairness_and_construct_relevance`.

Use `not_applicable` only for a genuinely inapplicable criterion, including MCQ-only form criteria on essays. A passing candidate cannot contain a failed required check. A passing MCQ must record `pass` for every required criterion and satisfy the canonical checklist in `quality-framework.md`; a criterion label does not prove its semantic truth.

For a passing MCQ, `blind_answer_checks` contains exactly two entries. Each contains `reviewer_id`, `selected_option_id`, `options_order`, `options_reordered`, `justification`, and `review_context`. The second entry has `options_reordered: true`; both agree with the key by stable option ID.

The `final_judge` contains `verdict`, `selected_option_id` for MCQs or `scoring_expectations_supported` for essays, `justification`, and `review_context`. A passed candidate requires a passing final judge.

Every isolated review context uses:

```json
{
  "isolation_method": "fresh_reviewer_context",
  "isolation_verified": true,
  "key_visible": false,
  "prior_verdicts_visible": false,
  "rationale_visible": false,
  "revision_history_visible": false,
  "target_metadata_visible": false
}
```

If isolation is not verified, the candidate must be `manual_review`, `revise`, or `reject`, never an automated `pass`.

`verdict` is `pass`, `revise`, `reject`, or `manual_review`. `final_status` is `selected`, `eligible`, `rejected`, `revision_required`, or `instructor_verification_required`.

### Final selection

Required structure:

```json
{
  "selected_candidate_ids": ["BP-01-C1"],
  "by_position": {"BP-01": "BP-01-C1"},
  "assessment_duplication_pass": {
    "completed": true,
    "run_count": 1,
    "status": "pass",
    "comparisons": [],
    "replacement_history": []
  },
  "blueprint_coverage_verified": true,
  "bloom_distribution_verified": true,
  "difficulty_distribution_verified": true,
  "item_type_distribution_verified": true,
  "points_verified": true,
  "answer_key_membership_verified": true
}
```

Select exactly one passing candidate per position. Selected-set comparison entries contain both candidate and position IDs, `cross_position_overlap`, lexical similarity, repetition authorization, `materially_distinct_cognition_or_evidence`, disposition, and justification. A substantive comparison fails unless repetition is authorized and material distinction is true. Similarity at or above `0.85` requires a recorded, resolved manual disposition.

Every replacement must append a history entry and increment `run_count`; rerun all selected-set comparisons, not only the changed pair.

### Approval and workflow status

```json
{
  "blueprint": {
    "status": "approved",
    "approved_by": "instructor",
    "approved_at": "ISO-8601 timestamp"
  },
  "final": {
    "status": "pending",
    "approved_by": null,
    "approved_at": null
  }
}
```

`workflow_status` may be `draft`, `awaiting_final_approval`, or `approved_for_delivery`. `approved_for_delivery` is valid only when final approval is `approved`, no escalation is unresolved, and the selected-set duplication status is `pass`. A structurally valid audit may remain `awaiting_final_approval`, but the assessment must not be described or distributed as approved.

### Compact, observable audit text

Justifications should be one or two short sentences and normally no more than 500 characters. Do not include fields named `chain_of_thought`, `reasoning_trace`, `internal_reasoning`, or equivalents. Store criteria, observations, source locators, verdicts, and concise explanations only.

## Deterministic validation boundary

`validate_audit.py` checks required structure, values, IDs, budgets, answer-key membership declarations, rubric totals, reviewer isolation declarations, exemplar bounds, sequential memory declarations, overlap disposition, and selected-set validation. It does not establish whether a source truly supports a concept, a Bloom label is semantically correct, a distractor is genuinely plausible, or a human approval is authentic.
