# Local package test — 2026.11.0

Test date: 27 September 2026. The package was built from commit `67e11f8b5f5eb2e250c7f9b4c1a48ca3750eccb0` with `git archive`, including only `plugin.json`, `assets/`, `skills/`, and `LICENSE`. The resulting ZIP is `assessment-item-designer-2026.11.0.zip` with SHA-256 `c6afab703600b408d374253dcda9e98741eab7ca09ed3867d6c9e09e862c81c6`.

The ZIP passed its integrity check. The manifest declares version `2026.11.0`; its skill, references, validator, assets, and icon paths are present. The extracted skill passed its own validator self-test (33/33).

## Prompt results

| Case in `OPENAI_SUBMISSION.md` | Result | Observed behavior |
| --- | --- | --- |
| Positive 1 | Pass | Creates a grounded two-position blueprint and waits for approval. |
| Positive 2 | Pass | Creates two reviewed MCQs, a separate answer key, an audit, and requests final approval. |
| Positive 3 | Pass | Creates a Dutch MCQ, a separate key, an audit, and requests final approval. |
| Positive 4 | Pass | Creates an essay item with a 10-point rubric, defensible alternatives, an audit, and requests final approval. |
| Positive 5 | Pass | Identifies the unsupported Five Forces position and stops delivery. |
| Negative 1 | Pass | Handles the unrelated bakery request without an assessment workflow. |
| Negative 2 | Pass | Declines to create a grounded exam without authorized evidence. |
| Negative 3 | Pass | Retains the blueprint, review, and final-approval gates. |
| Quickstart | Pass | Runs through explicit blueprint approval, four judged candidates, selected-item duplication, separate assessment and key, audit validation, and a final approval request. |

The Positive 2, 3, and 4 audits and the quickstart audit were independently rechecked with the validator from the extracted ZIP and passed the declared 2026.11 structure and invariant checks. They remain `awaiting_final_approval`. The quickstart records a difficulty caveat: its selected break-even item targets Medium but was independently estimated Easy with medium confidence, so instructor review is still required.

The tests ran against the extracted ZIP files rather than a Plugins Directory installation. Structural audit validation cannot establish source truth, semantic item quality, actual reviewer independence, or instructor identity. The test approvals are fixtures, not permission to administer the generated items. Rebuild and recheck the ZIP if any packaged file changes, including the provisional artwork.
