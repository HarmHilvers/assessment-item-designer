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

The reviewer receives the item content and permitted resources, but not:

- `target_bloom`;
- `target_difficulty`;
- generator labels or rationale;

- earlier verdicts or revision history;
- exemplar memory.

The reviewer records `reviewed_bloom` first, with one or two short sentences citing observable task demands. Only then compare it with `target_bloom` and set `bloom_fit: pass | fail`.

Do not infer level from a single command verb. Consider what information the item supplies, whether answer options reveal the needed reasoning, and the minimum cognitive process sufficient for a well-prepared student to answer correctly.

## Difficulty estimate

Difficulty is related to, but not determined by, Bloom. Estimate it using:

- number and dependency of reasoning steps;
- abstraction;
- context familiarity or novelty;
- integration across concepts or representations;
- scaffolding and cues in the stem and options;
- language and reading load;
- required calculation and permitted resources.

Default anchors:

- **Easy:** Remember or Understand, one step, familiar context, strong cues.
- **Medium:** Apply or introductory Analyze, two or three steps, limited integration.
- **Hard:** advanced Analyze, Evaluate, or Create, multiple dependent steps, novel context, or synthesis.

These are defaults, not conversion rules. A poorly worded Remember item may be hard for irrelevant reasons; that is a quality defect, not desirable difficulty. An Analyze item can be easy when options reveal the comparison.

Record `estimated_difficulty` before viewing `target_difficulty`, then set `difficulty_fit: pass | fail`. Use a concise observation such as: "Requires comparison of three competing explanations using two supplied criteria." Do not record hidden reasoning or chain-of-thought.

## Target-fit guidance

A reviewed category need not always equal the target label exactly if an approved blueprint explicitly defines an acceptable range. Otherwise use exact category fit. A higher reviewed Bloom level is not automatically better: it may violate accessibility, time, points, or intended coverage.

Model estimates are pre-administration design judgments. Never label them IRT difficulty or imply that they predict student-response parameters without empirical data.
