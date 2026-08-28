# Assessment Item Designer

Assessment Item Designer is an English-language Codex plugin for creating and reviewing grounded multiple-choice and essay assessment items through staged, auditable quality controls.

Release **2026.1** uses manifest version **2026.1.0**.

## What it does

The plugin helps instructors move from course materials and learning outcomes to an approved assessment. It supports:

- assessment blueprints with stable item positions;
- revised Bloom targets and independent Bloom review;
- separate target and estimated difficulty fields;
- sequential candidate generation with accepted and rejected exemplars;
- position-aware conceptual and lexical duplication checks;
- isolated, key-blind answer verification for multiple-choice questions;
- answer outlines and analytic rubrics for essay questions;
- bounded generation and revision;
- deterministic audit validation;
- mandatory instructor approval before delivery.

The instructions and audit keys are English. Generated assessments may use another language requested by the instructor.

## Quality-control workflow

1. Collect an assessment blueprint, or learning outcomes plus authorized course materials.
2. Establish grounding and create stable blueprint positions.
3. Obtain instructor approval of the blueprint.
4. Register optional calibration exemplars.
5. Generate candidates sequentially, updating accepted and rejected run exemplars after every verdict.
6. Review grounding, Bloom, difficulty, item form, fairness, duplication, and answerability in separate passes.
7. Select one passed candidate per blueprint position.
8. Run a new duplication review over the selected assessment only.
9. Validate blueprint coverage, distributions, points, answer-key membership, and the JSON audit.
10. Obtain final instructor approval before delivery.

The workflow fails closed when grounding, reviewer isolation, duplication disposition, budget compliance, or approval cannot be established.

## Bloom and difficulty

Difficulty is designed through revised Bloom taxonomy and independently reviewed from the actual cognitive work required by the item.

The audit separates:

- `target_bloom` from `reviewed_bloom`;
- `target_difficulty` from `estimated_difficulty`;
- target fit from the independent classification itself.

A fixed-response MCQ cannot be classified as `Create`. Model-estimated difficulty is a pre-administration design judgment and must not be described as student-response-based IRT difficulty.

## Position-aware duplication

Alternative candidates for the same blueprint position are expected to assess the same construct. They do not fail merely because their assessed concepts overlap. They are instead checked for excessive similarity in wording, structure, scenario, evidence, and solution route.

Across different blueprint positions, substantive conceptual overlap fails unless the approved blueprint explicitly authorizes repetition. When repetition is authorized, context-only variation is insufficient: the items must require materially different cognition or evidence.

Exact duplicates fail. Normalized lexical similarity of `0.85` or higher requires manual review, but low lexical similarity never proves conceptual distinctness.

## Outputs

Each completed assessment produces:

- `blueprint.md` — approved assessment blueprint;
- `assessment.md` — student-facing assessment;
- `answer-key.md` — answers, rationales, outlines, and rubrics;
- `quality-audit.json` — structured record of candidates, reviews, evidence, budgets, duplication controls, and approvals.

## Audit validator

The included validator checks the declared 2026.1 audit structure and deterministic invariants:

```bash
python3 skills/assessment-item-designer/scripts/validate_audit.py quality-audit.json
```

Run the built-in positive and negative fixture suite with:

```bash
python3 skills/assessment-item-designer/scripts/validate_audit.py --self-test
```

The validator checks structure, IDs, declared budgets, evidence-field separation, option membership, rubric totals, reviewer-isolation declarations, exemplar bounds, sequential memory, overlap disposition, selected-set validation, and approval-state consistency. It cannot prove that a source truly supports a claim, a semantic judgment is correct, reviewers were genuinely independent, or an approver's identity is authentic.

## Repository structure

```text
assessment-item-designer/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── assessment-item-designer/
│       ├── SKILL.md
│       ├── references/
│       │   ├── bloom-framework.md
│       │   ├── output-contract.md
│       │   ├── quality-framework.md
│       │   └── research-basis.md
│       └── scripts/
│           └── validate_audit.py
└── README.md
```

Release 2026.1 deliberately contains no MCP server, app, hook, `agents/openai.yaml`, or marketplace configuration.

## Repository-scoped testing

Codex can discover a repository-scoped copy of the skill under `.agents/skills/`. For local behavioral testing without a marketplace, copy the skill into a temporary or test repository:

```bash
mkdir -p .agents/skills/assessment-item-designer
cp -R skills/assessment-item-designer/. .agents/skills/assessment-item-designer/
```

Then test explicit activation with `$assessment-item-designer` and implicit activation with assessment-design or assessment-review requests. This does not constitute a complete ChatGPT Desktop plugin installation test.

## Research basis and limitations

The design credits:

> Isley, C. et al. (2025). *Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study*. arXiv:2508.08314v1.

- [Paper on arXiv](https://arxiv.org/abs/2508.08314)
- [Replication repository](https://github.com/calisley/ai_exams)

The plugin adapts the paper's pre-administration, course-bounded generate–judge–refine procedure, its use of accepted and rejected examples, and a separate final judging stage. It extends that procedure with assessment blueprints, revised Bloom classification, evidence requirements, blind answer verification, deterministic validation, bounded refinement, essays, rubrics, and instructor approval.

This is an extension, not a replication or methodologically equivalent implementation. The study's direct empirical evidence concerns short, college-level MCQs. It does not directly validate the essay workflow, Bloom classification, rubrics, approval gates, or the plugin as a whole. Release 2026.1 does not reproduce post-administration psychometric validation.

See [`research-basis.md`](skills/assessment-item-designer/references/research-basis.md) for the complete attribution, departures, and empirical limitations.

## Licensing and reuse

The Isley et al. replication repository exposed no visible license when release 2026.1 was packaged. Its code and prompt templates were therefore not copied into this plugin. The plugin's instructions and validation script were independently authored while methodological ideas are credited.

This repository currently makes no open-source license grant. Unless and until a license is added, default copyright rules apply.

## Author

Created by **Harm Hilvers**.

- Website: [hilvers.net](https://hilvers.net)
- GitHub: [HarmHilvers](https://github.com/HarmHilvers)
