# Research basis and limitations

## Attribution

This plugin credits the paper supplied with its design brief and the accompanying replication repository:

> Isley, C., Gilbert, J., Kassos, E., et al. (2026). *Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study*. Proceedings of the AAAI Conference on Artificial Intelligence, 40(45), 38626–38634. <https://doi.org/10.1609/aaai.v40i45.41205>

- Published paper: <https://doi.org/10.1609/aaai.v40i45.41205>
- Original preprint: arXiv:2508.08314 <https://arxiv.org/abs/2508.08314>
- Replication repository: <https://github.com/calisley/ai_exams>

The plugin adapts the pre-administration question-generation procedure described by Isley et al. (2026), particularly its course-bounded generation, iterative generate–judge–refine loop, use of accepted and rejected examples, and separate judging stages. It extends that procedure with assessment blueprints, revised Bloom classification, source-evidence requirements, context-isolated role separation, adaptive escalation, deterministic validation, bounded revision, and mandatory instructor approval. The plugin does not reproduce the study’s post-administration psychometric validation, and the study’s empirical findings apply directly to multiple-choice items rather than the essay workflow introduced here.

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

All candidates use context-isolated role separation. Standard MCQs use a target-blind classifier and key-blind item judge, with adaptive escalation to a third key-blind reviewer when uncertainty or disagreement warrants it. High-assurance MCQs retain two blind answer solvers and a final judge; essays use a classifier and independent final/scoring judge. The paper does not validate this particular isolation architecture, adaptive reviewer count, three-category memory, confidence policy or their effect on assessment quality.

## Empirical scope

The study's direct empirical evidence concerns short, college-level multiple-choice questions. It does not validate this plugin as a whole. In particular, the following are extensions that the study did not empirically evaluate:

- essay generation;
- revised Bloom classification;
- analytic rubrics;
- context-isolated reviewer roles and high-assurance answer verification as specified here;
- blueprint conformance controls;
- human approval gates.

The study names open-response questions as a possible future extension. Do not cite it as evidence that the essay workflow is effective.

Model-estimated difficulty is a pre-administration judgment, not an empirical calibration. IRT difficulty is estimated from student-response data. The two must remain distinct in language and audit fields. The finding that generated items were empirically easier also cautions against treating a model's difficulty label as measurement evidence.

Release 2026.10 performs pre-administration quality control only. It does not reproduce post-administration item analysis, student-response-based IRT calibration, or the field study's causal and comparative analyses. Additional high-assurance reviewers provide procedural assurance, but their marginal psychometric benefit has not been established here. Independent LLM agreement is not empirical validation.

## Post-administration psychometric quality

Pre-administration review can establish evidence about alignment, clarity, one-best-answer form, distractor plausibility, cue avoidance, fairness risks, and other construction properties. It cannot establish how an item actually functions in a population. That requires student-response data and a separate documented analysis. Isley et al. (2026) used item response theory in their field study; release 2026.10 does not reproduce that psychometric evaluation.

When response data become available, appropriate post-administration evidence may include:

- observed item difficulty, such as proportion correct, interpreted relative to the assessment purpose and population;
- item discrimination, such as a corrected item-total relationship or another defensible discrimination index;
- distractor functioning, including how often distractors are selected and whether their selection pattern is consistent with lower versus higher overall performance;
- score reliability or test information when appropriate to the intended score interpretation;
- IRT item parameters and test information only when sample size, model fit, dimensionality, and design support the selected model;
- differential item functioning or other group-based fairness analyses when relevant groups, sample sizes, and the assessment design permit defensible inference;
- qualitative review of anomalous items alongside statistical evidence before retaining, revising, or retiring them.

No single statistic proves that an item or test is valid. Interpret empirical item statistics together with content evidence, response processes, internal structure, relationships to other variables where relevant, fairness, and the intended use of scores. Thresholds are context-dependent; this framework does not impose universal cutoffs. [S6, S7, S8, S9, S10]

Keep model-estimated pre-administration difficulty separate from empirical post-administration results in both language and data structures. A future psychometric workflow should preserve the administered item version and response population, document exclusions and scoring, and avoid retroactively overwriting the pre-administration audit.

## MCQ item-writing evidence

The canonical MCQ quality gate also draws on established item-writing guidance and empirical studies of item flaws and distractor functioning. These sources support general design principles such as alignment, focused stems, one-best-answer construction, plausible distractors, parallel options, cue avoidance, and construct-relevant fairness. They also support the distinction between item-construction quality and empirical post-administration functioning. They do not validate this plugin's complete workflow, automated judgments, Bloom classifications, or essay extensions.

- `[S1]` Haladyna, T. M., Downing, S. M., & Rodriguez, M. C. (2002). *A review of multiple-choice item-writing guidelines for classroom assessment*. Applied Measurement in Education, 15(3), 309–333. <https://doi.org/10.1207/S15324818AME1503_5>
- `[S2]` Rodriguez, M. C. (2005). *Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research*. Educational Measurement: Issues and Practice, 24(2), 3–13. <https://doi.org/10.1111/j.1745-3992.2005.00006.x>
- `[S3]` McGill University Teaching and Learning Knowledge Base. *Guidelines for Writing MCQs*. <https://teachingkb.mcgill.ca/tlk/guidelines-for-writing-mcqs>
- `[S4]` Yale University Poorvu Center for Teaching and Learning. *Designing Assessment Questions*. <https://poorvucenter.yale.edu/teaching/teaching-resource-library/designing-assessment-questions>
- `[S5]` National Board of Medical Examiners. *NBME Item-Writing Guide*, 6th ed. <https://www.nbme.org/sites/default/files/2021-02/NBME_Item%20Writing%20Guide_R_6.pdf>
- `[S6]` Downing, S. M. (2005). *The effects of violating standard item writing principles on tests and students: The consequences of using flawed test items on achievement examinations in medical education*. Advances in Health Sciences Education, 10(2), 133–143. <https://doi.org/10.1007/s10459-004-4019-5>
- `[S7]` Tarrant, M., & Ware, J. (2008). *Impact of item-writing flaws in multiple-choice questions on student achievement in high-stakes nursing assessments*. Medical Education, 42(2), 198–206. <https://doi.org/10.1111/j.1365-2923.2007.02957.x>
- `[S8]` Tarrant, M., Ware, J., & Mohammed, A. M. (2009). *An assessment of functioning and non-functioning distractors in multiple-choice questions: A descriptive analysis*. BMC Medical Education, 9, 40. <https://doi.org/10.1186/1472-6920-9-40>
- `[S9]` Haladyna, T. M., & Rodriguez, M. C. (2013). *Developing and Validating Test Items*. Routledge. <https://www.routledge.com/Developing-and-Validating-Test-Items/Haladyna-Rodriguez/p/book/9780415876056>
- `[S10]` American Educational Research Association, American Psychological Association, & National Council on Measurement in Education. (2014). *Standards for Educational and Psychological Testing*. American Educational Research Association. <https://www.aera.net/Publications/Books/Standards-for-Educational-Psychological-Testing-2014-Edition>

[S2] supports three options as a general default, and [S8] shows why adding non-functioning distractors is not a neutral design choice. This plugin therefore defaults to one keyed answer plus two plausible distractors. Add further options only when each additional distractor is independently plausible and construct-relevant or the approved blueprint requires the extra option. If two plausible distractors cannot be written from authorized material, revise the item or escalate rather than add filler.

[S6] and [S7] provide empirical evidence that item-writing flaws can affect examinee performance and introduce construct-irrelevant variance in the studied settings. [S8] provides empirical evidence about non-functioning distractors. [S9] and [S10] provide broader test-development, validity, and fairness frameworks. These sources differ in population, purpose, and evidential scope, so the plugin does not turn their findings into universal numerical thresholds.

## Repository reuse and licensing

At initial packaging time, the Isley et al. replication repository root exposed no visible `LICENSE` file. Absence of a license is not permission to copy copyrighted material.

Therefore:

- instructions and scripts in this plugin must be independently authored;
- methodological ideas may be described with clear attribution;
- repository code and prompt templates must not be copied verbatim unless a later license or explicit permission allows it;
- the repository license must be checked again before any later packaging;
- this project's independently authored instructions, documentation and scripts are licensed under the [MIT License](../LICENSE); that grant does not extend to third-party research or repository materials.

This notice concerns reuse permission, not the scholarly citation obligation, which applies regardless.
