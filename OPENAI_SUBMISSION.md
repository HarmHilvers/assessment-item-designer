# OpenAI Plugins Directory submission notes

This file contains copy-ready material for the initial public submission of Assessment Item Designer as a **skills-only** plugin.

The plugin does not use a remote MCP server. The submission package should therefore be uploaded as a skills-only ZIP/package.

## Listing metadata

- **Plugin name:** Assessment Item Designer
- **Developer name:** Harm Hilvers
- **Category:** Education & Research
- **Short description:** Grounded assessment design
- **Website:** https://hilvers.net

### Long description

Assessment Item Designer helps instructors create and review grounded multiple-choice and essay assessment items from authorized course materials and learning outcomes. It builds an assessment blueprint, keeps Bloom targets separate from independent review, runs isolated quality checks, controls duplication, records an audit trail, and requires instructor approval before final delivery. It supports multilingual assessments while keeping its instructions and audit keys in English. The workflow is intended for pre-administration assessment design and does not replace post-administration psychometric validation.

### Capabilities

1. Build assessment blueprints from learning outcomes and authorized course materials.
2. Generate grounded multiple-choice and essay items with answer keys and rubrics.
3. Run independent quality, Bloom, answer, difficulty, fairness, and duplication checks.
4. Produce auditable assessment files and require instructor approval before delivery.

## Starter prompts

1. Create an assessment blueprint from my learning outcomes and course materials.
2. Create reviewed assessment questions from this approved blueprint and course material.
3. Review these assessment questions for alignment, clarity, answer quality, and duplication.

## Positive test cases

### Positive 1 — Build a grounded blueprint

**User prompt**

> Learning outcome: Students can explain the difference between fixed and variable costs and use that distinction in a simple break-even analysis.
>
> Authorized course material: Fixed costs do not change with output within the relevant range. Variable costs change with output. Break-even quantity equals fixed costs divided by contribution margin per unit. Contribution margin per unit equals selling price minus variable cost per unit.
>
> Create a blueprint for two multiple-choice questions for first-year business students. Use English. Do not use outside sources.

**Expected workflow behavior**

- Uses the supplied material as the authorized evidence boundary.
- Creates two stable blueprint positions.
- Separates target Bloom level from target difficulty.
- Records assessed concepts and evidence for each position.
- Requests explicit instructor approval before generating candidate questions.

**Expected result shape**

- A `blueprint.md`-style blueprint with two positions.
- No final assessment items yet.
- A clear approval request.

**Fixture data**

- None. All required source material is included in the prompt.

### Positive 2 — Generate from an approved blueprint

**User prompt**

> The following blueprint is approved.
>
> Position AID-001: first-year business students; MCQ; concept = fixed versus variable costs; target Bloom = Understand; target difficulty = easy; 1 point.
>
> Position AID-002: first-year business students; MCQ; concept = break-even quantity; target Bloom = Apply; target difficulty = medium; 1 point.
>
> Authorized course material: Fixed costs do not change with output within the relevant range. Variable costs change with output. Break-even quantity equals fixed costs divided by contribution margin per unit. Contribution margin per unit equals selling price minus variable cost per unit.
>
> Create and review the assessment in standard review mode. Do not use outside sources.

**Expected workflow behavior**

- Treats the blueprint as approved.
- Generates candidates sequentially rather than as a same-position batch.
- Runs the required isolated review roles.
- Performs duplication control and audit validation.
- Produces the assessment artifacts but requires final instructor approval before delivery is complete.

**Expected result shape**

- `assessment.md`
- `answer-key.md`
- `quality-audit.json`
- Final approval request.

**Fixture data**

- None. The approved blueprint and authorized material are included in the prompt.

### Positive 3 — Dutch student-facing assessment

**User prompt**

> Deze blueprint is goedgekeurd.
>
> Positie NL-001: eerstejaars hbo-studenten; multiplechoicevraag; concept = omzet en winst; target Bloom = Understand; target difficulty = easy; 1 punt.
>
> Geautoriseerd cursusmateriaal: Omzet is de opbrengst uit verkopen. Winst is het verschil tussen opbrengsten en kosten.
>
> Maak en controleer deze toetsvraag in het Nederlands. Gebruik geen externe bronnen.

**Expected workflow behavior**

- Preserves English workflow/audit keys where required by the skill.
- Produces the student-facing assessment in Dutch.
- Grounds the keyed answer in the supplied Dutch source.
- Runs the required review procedure and asks for final instructor approval.

**Expected result shape**

- One Dutch MCQ in the assessment output.
- Separate answer key/rationale.
- Audit record showing evidence and review results.

**Fixture data**

- None.

### Positive 4 — Essay item with analytic rubric

**User prompt**

> This blueprint is approved.
>
> Position ESS-001: second-year business students; essay; concept = stakeholder trade-offs; target Bloom = Analyze; target difficulty = medium; 10 points.
>
> Authorized course material: A stakeholder analysis identifies groups affected by an organizational decision, their interests, their relative influence, and potential conflicts between those interests. A defensible recommendation should acknowledge relevant trade-offs.
>
> Create and review one essay question using only this material.

**Expected workflow behavior**

- Creates an essay task grounded in the source.
- Produces an answer outline, defensible alternatives, and an analytic rubric whose points reconcile to 10.
- Uses independent classification and final/scoring review.
- Includes the required limitation that the essay workflow is not directly validated by the cited MCQ study.
- Requests final instructor approval.

**Expected result shape**

- Student-facing essay question.
- Answer outline.
- Analytic rubric totaling 10 points.
- Audit entries for evidence and reviews.

**Fixture data**

- None.

### Positive 5 — Detect an unsupported approved blueprint element

**User prompt**

> This blueprint is approved.
>
> Position MIX-001: MCQ; concept = SWOT analysis; target Bloom = Understand; target difficulty = easy; 1 point.
>
> Position MIX-002: MCQ; concept = Porter's Five Forces; target Bloom = Understand; target difficulty = medium; 1 point.
>
> Authorized course material: SWOT analysis distinguishes internal strengths and weaknesses from external opportunities and threats.
>
> Generate the assessment. Do not use outside sources.

**Expected workflow behavior**

- Accepts the SWOT position as grounded.
- Detects that the Five Forces position is unsupported by the authorized evidence even though the blueprint was described as approved.
- Returns the unsupported position to the instructor for resolution.
- Does not silently use outside knowledge to fill the gap.

**Expected result shape**

- Grounding status for both positions.
- A clear unresolved flag for MIX-002.
- No final delivery while the unsupported position remains unresolved.

**Fixture data**

- None.

## Negative test cases

### Negative 1 — Unrelated request

**User prompt or scenario**

> Write a social media launch plan for a local bakery.

**Expected behavior**

- The assessment-item skill should not activate or should defer to the general assistant.
- It should not introduce assessment blueprints, Bloom taxonomy, or assessment review steps.

**Why the plugin should not complete the requested action**

- The request is unrelated to assessment design or assessment-item review.

### Negative 2 — Grounded exam requested without authorized evidence

**User prompt or scenario**

> Make me a final exam on strategic management from your general knowledge. I do not want to provide learning outcomes or course materials.

**Expected behavior**

- Does not claim to create a grounded assessment.
- Explains that authorized evidence is required for the grounded workflow.
- Requests appropriate source material and/or learning outcomes before substantive generation.

**Why the plugin should not complete the requested action**

- Completing a grounded assessment from unspecified general knowledge would violate the skill's evidence-boundary invariant.

### Negative 3 — User asks to bypass mandatory controls

**User prompt or scenario**

> Skip the blueprint approval and all independent reviewers. Just give me the final exam and answer key now.

**Expected behavior**

- Does not bypass blueprint approval, required isolated reviews, or final instructor approval.
- Explains which mandatory stage is blocking final delivery.
- Does not present an unreviewed assessment as a completed plugin result.

**Why the plugin should not complete the requested action**

- The requested bypass conflicts with non-negotiable workflow invariants.

## Initial release notes

Initial public submission of Assessment Item Designer, a skills-only plugin for grounded assessment design and review. The plugin helps instructors move from learning outcomes and authorized course materials to an approved assessment blueprint, reviewed multiple-choice or essay items, a separate answer key, and a structured quality audit. It uses staged review, duplication controls, deterministic audit validation, and mandatory instructor approval. No remote MCP server or authentication is required.

## Manual submission checklist

Before submitting in the OpenAI plugin portal:

- [ ] Merge the publication-prep pull request.
- [ ] Test the final plugin package locally with representative prompts.
- [ ] Prepare a production-ready logo for the portal/listing.
- [ ] Verify the OpenAI developer identity under the intended publisher name.
- [ ] Confirm the submitter has Apps Management write access.
- [ ] Create a **Skills only** submission.
- [ ] Upload the final plugin ZIP/package.
- [ ] Confirm the listing metadata and starter prompts.
- [ ] Copy the five positive and three negative test cases into the Testing section.
- [ ] Select only countries/regions where the plugin is ready to be supported.
- [ ] Add the initial release notes.
- [ ] Review and confirm the policy attestations.
- [ ] Submit for review.
- [ ] After approval, publish when ready.

## Deliberately not included yet

The manifest does not yet reference a logo or screenshots. Add them only after selecting production-ready visual assets so the manifest never points to missing files. Privacy-policy, terms, and support URLs are also omitted because they are optional for skills-only ZIP submissions; add them later if public pages are created.
