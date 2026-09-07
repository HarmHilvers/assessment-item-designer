# Assessment Item Designer

Assessment Item Designer is an English-language Codex plugin for creating and reviewing grounded multiple-choice and essay assessment items through staged, auditable quality controls.

Release **2026.4** uses manifest version **2026.4.0**.

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

## How it works

1. **Provide your materials.** Supply an assessment blueprint, or learning outcomes and authorized course materials. Specify the audience, language, question types and assessment requirements.
2. **Approve the blueprint.** Agree on the concepts, points and intended cognitive demand and difficulty for each question. Revised Bloom taxonomy describes the thinking students must demonstrate; difficulty is a separate judgment.
3. **Generate and review questions.** Candidates are created one at a time, with earlier review results informing the next candidate. Independent subagents assess cognitive demand, difficulty and answerability without seeing the intended answers or target labels. Their findings are then compared with the blueprint.
4. **Assemble the assessment.** Select questions that pass the required checks, review the complete set for duplication, and verify coverage, points and answer-key consistency.
5. **Give final approval.** Review the assessment and separate answer key before approving them for use. Unresolved quality checks must be completed first.

Bloom levels are based on the work a student must actually perform. A fixed-response multiple-choice question cannot demonstrate `Create`. Estimated difficulty is a design judgment before administration; measuring actual item difficulty requires student-response data.

## Outputs

Each completed assessment produces:

- `blueprint.md` — approved assessment blueprint;
- `assessment.md` — student-facing assessment;
- `answer-key.md` — answers, rationales, outlines, and rubrics;
- `quality-audit.json` — structured record of candidates, reviews, evidence, budgets, duplication controls, and approvals.

## Installation

Installation depends on your AI application. The [Agent Plugins standard](https://agent-plugins.org/plugin-authors/build-an-agent-plugin) defines a portable package format, while installation and distribution remain application-specific.

This repository currently provides a Codex plugin manifest at `.codex-plugin/plugin.json` and a standalone skill under `skills/assessment-item-designer/`. It does not yet include the root `plugin.json` required by the portable Agent Plugins format. The instructions below install the skill in Codex; they are not a universal plugin installation command.

Install with Codex's built-in skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo HarmHilvers/assessment-item-designer \
  --path skills/assessment-item-designer
```

This installs the skill into `~/.codex/skills/assessment-item-designer/`. The destination must not already exist. Open a new Codex task and try:

```text
$assessment-item-designer Help me create a grounded assessment.
```

The workflow requires an application that can run fresh subagents, read and write assessment files, and execute Python 3. For other applications, consult their installation documentation and verify these capabilities before use.

## Research basis and limitations

The design credits:

> Isley, C. et al. (2025). *Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study*. arXiv:2508.08314v1.

- [Paper on arXiv](https://arxiv.org/abs/2508.08314)
- [Replication repository](https://github.com/calisley/ai_exams)

The plugin adapts the paper's pre-administration, course-bounded generate–judge–refine procedure, its use of accepted and rejected examples, and a separate final judging stage. It extends that procedure with assessment blueprints, revised Bloom classification, evidence requirements, blind answer verification, deterministic validation, bounded refinement, essays, rubrics, and instructor approval.

This is an extension, not a replication or methodologically equivalent implementation. The study's direct empirical evidence concerns short, college-level MCQs. It does not directly validate the essay workflow, Bloom classification, rubrics, approval gates, or the plugin as a whole. Release 2026.4 does not reproduce post-administration psychometric validation.

The MCQ quality gate additionally draws on:

- [Haladyna, Downing, and Rodriguez (2002)](https://doi.org/10.1207/S15324818AME1503_5);
- [Rodriguez (2005)](https://doi.org/10.1111/j.1745-3992.2005.00006.x);
- [McGill University’s Guidelines for Writing MCQs](https://teachingkb.mcgill.ca/tlk/guidelines-for-writing-mcqs);
- [Yale Poorvu Center’s Designing Assessment Questions](https://poorvucenter.yale.edu/teaching/teaching-resource-library/designing-assessment-questions);
- [NBME Item-Writing Guide, 6th ed.](https://www.nbme.org/sites/default/files/2021-02/NBME_Item%20Writing%20Guide_R_6.pdf).

These sources support general MCQ item-writing principles, not the complete plugin workflow or its automated semantic judgments.

See [`research-basis.md`](skills/assessment-item-designer/references/research-basis.md) for the complete attribution, departures, and empirical limitations.

## License

Licensed under the [MIT License](LICENSE). Copyright © 2026 Harm Hilvers.

The license covers this project's original instructions, documentation and scripts. Referenced research and third-party materials retain their own terms.
