# Research basis and limitations

## Attribution

This plugin credits the paper supplied with its design brief and the accompanying replication repository:

> Isley, C. et al. (2025). *Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study*. arXiv:2508.08314v1.

- Supplied paper: `2508.08314v1.pdf`
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
- FIFO run-exemplar memory rather than retaining the paper's first five run examples;
- support for essay questions, answer outlines, and analytic rubrics;
- mandatory instructor approval gates;
- final selection based on exact blueprint coverage rather than selection of the hardest candidates.

The paper selected its hardest judged candidates as a pragmatic response to generated questions being too easy. This plugin does not reproduce that rule. It follows the approved targets for learning outcomes, Bloom level, difficulty, item type, and points.

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

Release 2026.1 performs pre-administration quality control only. It does not reproduce post-administration item analysis, student-response-based IRT calibration, or the field study's causal and comparative analyses.

## Repository reuse and licensing

At packaging time for release 2026.1, the repository root exposed no visible `LICENSE` file. Absence of a license is not permission to copy copyrighted material.

Therefore:

- instructions and scripts in this plugin must be independently authored;
- methodological ideas may be described with clear attribution;
- repository code and prompt templates must not be copied verbatim unless a later license or explicit permission allows it;
- the repository license must be checked again before any later packaging;
- release 2026.1 makes no open-source license claim.

This notice concerns reuse permission, not the scholarly citation obligation, which applies regardless.
