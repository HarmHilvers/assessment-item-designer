# Research basis and limitations

## Attribution

This plugin credits the paper supplied with its design brief and the accompanying replication repository:

> Isley, C. et al. (2025). *Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study*. arXiv:2508.08314v1.

- Reviewed paper version: arXiv:2508.08314v1, especially §3.1 and §4.3
- Paper identifier: <https://arxiv.org/abs/2508.08314>
- Replication repository: <https://github.com/calisley/ai_exams>

The plugin adapts the pre-administration question-generation procedure described by Isley et al. (2025), particularly its course-bounded generation, iterative generate–judge–refine loop, use of accepted and rejected examples, and separate final judging stage. It extends that procedure with assessment blueprints, revised Bloom classification, source-evidence requirements, blind answer verification, deterministic validation, bounded revision, and mandatory instructor approval. The plugin does not reproduce the study’s post-administration psychometric validation, and the study’s empirical findings apply directly to multiple-choice items rather than the essay workflow introduced here.

## What is adapted

The procedure takes inspiration from these pre-administration features:

- generation bounded by course content;
- iterative generation followed by judging;
- accepted and rejected candidates used as later examples;
- a separate final judging step;
- removal of questions that duplicate concepts already covered;
- concrete MCQ rejection rules.

The paper used five fixed AP Statistics questions as positive calibration examples and, during generation, up to five previously accepted and five rejected questions. This plugin separates those roles into optional instructor-approved `calibration_exemplars` and adaptive `run_exemplars`.

## Original extensions and departures

This is an extension of Isley et al.'s iterative generation-and-judging architecture, not a replication or methodologically equivalent implementation. Its original or materially changed components include:

- an instructor-approved assessment blueprint;
- revised Bloom classification and target-fit review;
- explicit `scope_evidence`, `answer_evidence`, and `scenario_origin` fields;
- two context-isolated blind MCQ answer solvers;
- deterministic validation and stable IDs;
- position-aware conceptual duplication rules;
- bounded candidate generation and revision;
- independent FIFO windows for accepted, revisable and rejected examples rather than the paper's first-five good/bad examples;
- explicit uncertainty and basis for pre-administration difficulty estimates;
- support for essay questions, answer outlines, and analytic rubrics;
- mandatory instructor approval gates;
- final selection based on exact blueprint coverage rather than selection of the hardest candidates.

The paper's §3.1 describes generating 20 accepted items and selecting the ten judged hardest after a further review. Its §4.3 reports that generated items were nevertheless empirically easier than the standardized comparison items. This plugin therefore treats Easy/Medium/Hard and confidence as pre-administration design estimates, not psychometric measurements. An uncertain adjacent-category difference can be retained for instructor review; substantive mismatches require resolution. It selects against approved targets rather than simply maximizing predicted difficulty.

The accepted/revisable/rejected memory semantics are our extension. `revise` preserves a useful concept while identifying a correctable defect; it is not a generic bad example. Unresolved human-review cases are excluded from generation memory. An immutable judgment history preserves what was known before each generation call, including later revisions and human resolutions.

All candidates still use separate independent classification and final reviewers; MCQs additionally use two blind answer solvers. The paper does not validate this particular isolation architecture, three-category memory, confidence policy or their effect on assessment quality.

## Empirical scope

The study's direct empirical evidence concerns short, college-level multiple-choice questions. It does not validate this plugin as a whole. In particular, the following are extensions that the study did not empirically evaluate:

- essay generation;
- revised Bloom classification;
- analytic rubrics;
- blind answer verification as specified here;
- blueprint conformance controls;
- human approval gates.

The study names open-response questions as a possible future extension. Do not cite it as evidence that the essay workflow is effective.

Model-estimated difficulty is a pre-administration judgment, not an empirical calibration. IRT difficulty is estimated from student-response data. The two must remain distinct in language and audit fields. The finding that generated items were empirically easier also cautions against treating a model's difficulty label as measurement evidence.

Release 2026.6 performs pre-administration quality control only. It does not reproduce post-administration item analysis, student-response-based IRT calibration, or the field study's causal and comparative analyses.

## MCQ item-writing evidence

The canonical MCQ quality gate also draws on established item-writing guidance. These sources support general design principles such as alignment, focused stems, one-best-answer construction, plausible distractors, parallel options, cue avoidance, and construct-relevant fairness. They do not validate this plugin's complete workflow, automated judgments, Bloom classifications, or essay extensions.

- `[S1]` Haladyna, T. M., Downing, S. M., & Rodriguez, M. C. (2002). *A review of multiple-choice item-writing guidelines for classroom assessment*. Applied Measurement in Education, 15(3), 309–333. <https://doi.org/10.1207/S15324818AME1503_5>
- `[S2]` Rodriguez, M. C. (2005). *Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research*. Educational Measurement: Issues and Practice, 24(2), 3–13. <https://doi.org/10.1111/j.1745-3992.2005.00006.x>
- `[S3]` McGill University Teaching and Learning Knowledge Base. *Guidelines for Writing MCQs*. <https://teachingkb.mcgill.ca/tlk/guidelines-for-writing-mcqs>
- `[S4]` Yale University Poorvu Center for Teaching and Learning. *Designing Assessment Questions*. <https://poorvucenter.yale.edu/teaching/teaching-resource-library/designing-assessment-questions>
- `[S5]` National Board of Medical Examiners. *NBME Item-Writing Guide*, 6th ed. <https://www.nbme.org/sites/default/files/2021-02/NBME_Item%20Writing%20Guide_R_6.pdf>

The three-option recommendation is a default against padding, not a claim that every four-option item is defective. More options remain permissible when all distractors are genuinely plausible or the approved blueprint requires them.

## Repository reuse and licensing

At initial packaging time, the Isley et al. replication repository root exposed no visible `LICENSE` file. Absence of a license is not permission to copy copyrighted material.

Therefore:

- instructions and scripts in this plugin must be independently authored;
- methodological ideas may be described with clear attribution;
- repository code and prompt templates must not be copied verbatim unless a later license or explicit permission allows it;
- the repository license must be checked again before any later packaging;
- this project's independently authored instructions, documentation and scripts are licensed under the [MIT License](../LICENSE); that grant does not extend to third-party research or repository materials.

This notice concerns reuse permission, not the scholarly citation obligation, which applies regardless.
