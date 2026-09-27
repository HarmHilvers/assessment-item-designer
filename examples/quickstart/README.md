# 5-minute quickstart

This example is designed to get a first-time user to an **assessment blueprint** with almost no setup. A full generation-and-review run can take longer because the skill performs independent checks before final delivery.

## Goal

Create a two-item multiple-choice assessment for first-year business students using only the supplied learning outcomes and course material.

## Files in this folder

- `learning-outcomes.md` — what students should be able to do;
- `course-material.md` — the authorized evidence boundary;
- `request.md` — a ready-to-copy prompt.

## Try it

1. Make sure Assessment Item Designer is installed in a compatible ChatGPT/Codex environment.
2. Start a new task or chat.
3. Add `learning-outcomes.md` and `course-material.md`.
4. Copy the text from `request.md` into the conversation.
5. Review the proposed blueprint.
6. If it is correct, reply: **I approve this blueprint. Continue in standard review mode.**

## What you should see

Before generating final questions, the skill should:

- treat the supplied course material as the authorized evidence boundary;
- create two stable blueprint positions;
- connect each position to a learning outcome and assessed concept;
- specify target Bloom level and target difficulty separately;
- ask for explicit instructor approval.

After approval, it should generate and review the items, then prepare separate student-facing, answer-key, and audit outputs. Final delivery still requires instructor approval.

## If it stops early

That can be correct behavior. The workflow intentionally stops when it cannot verify required capabilities such as isolated reviewers, file access, or Python execution, or when the supplied evidence does not support a requested assessment position.

For the full workflow and limitations, return to the repository [README](../../README.md).
