#!/usr/bin/env python3
"""Validate Assessment Item Designer 2026.2 audit declarations.

This validator checks structure and declared invariants. It cannot verify the
truth of semantic judgments, source support, reviewer independence, or human
approval.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import itertools
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


RELEASE = "2026.2"
MANIFEST_VERSION = "2026.2.0"
BLOOM = {"Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"}
DIFFICULTY = {"Easy", "Medium", "Hard"}
FITS = {"pass", "fail"}
VERDICTS = {"pass", "revise", "reject", "manual_review"}
FINAL_STATUSES = {
    "selected",
    "eligible",
    "rejected",
    "revision_required",
    "instructor_verification_required",
}
SCENARIO_ORIGINS = {"source_derived", "constructed", "mixed", "not_applicable"}
REQUIRED_REJECTION_CRITERIA = {
    "answer_defensible_without_unstated_assumptions",
    "answer_clues",
    "cognitive_level_alignment",
    "complex_option_formats_absent",
    "construct_relevant_difficulty",
    "course_meta_or_logistics",
    "distractor_quality",
    "explicit_syllabus_wording",
    "fairness_and_construct_relevance",
    "learning_outcome_alignment",
    "negative_wording_justified",
    "one_best_answer",
    "option_mutual_exclusivity",
    "option_parallelism",
    "option_to_option_references",
    "resource_demands_match_blueprint",
    "stem_clarity_and_self_containment",
    "stem_relevance_and_concision",
    "stem_task_understandable_before_options",
    "trivial_retrieval_or_formula_substitution",
    "unintended_external_dependencies",
    "unsupported_concepts",
}
FORBIDDEN_REASONING_KEYS = {
    "chain_of_thought",
    "chain-of-thought",
    "reasoning_trace",
    "internal_reasoning",
    "hidden_reasoning",
}
ISOLATION_FALSE_FIELDS = {
    "key_visible",
    "prior_verdicts_visible",
    "rationale_visible",
    "revision_history_visible",
    "target_metadata_visible",
}


class AuditValidator:
    def __init__(self, data: Any):
        self.data = data
        self.errors: list[str] = []
        self.positions: dict[str, dict[str, Any]] = {}
        self.candidates: dict[str, dict[str, Any]] = {}

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def require_object(self, value: Any, path: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.error(path, "must be an object")
            return {}
        return value

    def require_list(self, value: Any, path: str) -> list[Any]:
        if not isinstance(value, list):
            self.error(path, "must be an array")
            return []
        return value

    def require_keys(self, obj: dict[str, Any], path: str, keys: Iterable[str]) -> None:
        for key in keys:
            if key not in obj:
                self.error(f"{path}.{key}", "is required")

    def validate(self) -> list[str]:
        root = self.require_object(self.data, "$")
        required = {
            "schema_version",
            "workflow_status",
            "metadata",
            "blueprint",
            "exemplar_registries",
            "generation_budget",
            "candidates",
            "final_selection",
            "escalations",
            "instructor_approval",
        }
        self.require_keys(root, "$", required)
        if root.get("schema_version") != RELEASE:
            self.error("$.schema_version", f"must equal {RELEASE!r}")
        if root.get("workflow_status") not in {
            "draft",
            "awaiting_final_approval",
            "approved_for_delivery",
        }:
            self.error("$.workflow_status", "has an unsupported value")

        self.validate_metadata(root.get("metadata"))
        self.validate_blueprint(root.get("blueprint"))
        self.validate_exemplar_registries(root.get("exemplar_registries"))
        self.validate_budget(root.get("generation_budget"))
        self.validate_candidates(root.get("candidates"))
        self.validate_run_exemplar_consistency(root.get("exemplar_registries"))
        self.validate_final_selection(root.get("final_selection"))
        self.validate_approval(root.get("instructor_approval"), root)
        self.validate_escalations(root.get("escalations"), root)
        self.validate_compact_observations(root)
        return self.errors

    def validate_metadata(self, value: Any) -> None:
        obj = self.require_object(value, "$.metadata")
        self.require_keys(
            obj,
            "$.metadata",
            {"release", "manifest_version", "assessment_language", "created_at", "research_basis"},
        )
        if obj.get("release") != RELEASE:
            self.error("$.metadata.release", f"must equal {RELEASE!r}")
        if obj.get("manifest_version") != MANIFEST_VERSION:
            self.error("$.metadata.manifest_version", f"must equal {MANIFEST_VERSION!r}")
        for key in ("assessment_language", "created_at"):
            if not isinstance(obj.get(key), str) or not obj.get(key, "").strip():
                self.error(f"$.metadata.{key}", "must be a non-empty string")
        research = self.require_object(obj.get("research_basis"), "$.metadata.research_basis")
        self.require_keys(
            research,
            "$.metadata.research_basis",
            {
                "citation",
                "extension_not_replication",
                "direct_empirical_scope",
                "essay_workflow_empirically_validated",
                "model_difficulty_is_irt",
                "post_administration_psychometrics_included",
            },
        )
        citation = str(research.get("citation", ""))
        if "Isley" not in citation or "2508.08314" not in citation:
            self.error("$.metadata.research_basis.citation", "must identify Isley et al. and arXiv:2508.08314")
        expected = {
            "extension_not_replication": True,
            "essay_workflow_empirically_validated": False,
            "model_difficulty_is_irt": False,
            "post_administration_psychometrics_included": False,
        }
        for key, wanted in expected.items():
            if research.get(key) is not wanted:
                self.error(f"$.metadata.research_basis.{key}", f"must be {wanted}")

    def validate_blueprint(self, value: Any) -> None:
        obj = self.require_object(value, "$.blueprint")
        self.require_keys(obj, "$.blueprint", {"kind", "status", "positions"})
        if obj.get("kind") not in {"approved_blueprint", "provisional_review_blueprint"}:
            self.error("$.blueprint.kind", "must be approved_blueprint or provisional_review_blueprint")
        if obj.get("status") != "approved":
            self.error("$.blueprint.status", "must be approved before candidate generation or revision")
        positions = self.require_list(obj.get("positions"), "$.blueprint.positions")
        if not positions:
            self.error("$.blueprint.positions", "must contain at least one position")
        for index, raw in enumerate(positions):
            path = f"$.blueprint.positions[{index}]"
            pos = self.require_object(raw, path)
            self.require_keys(
                pos,
                path,
                {
                    "blueprint_position_id",
                    "learning_outcome",
                    "assessed_concepts",
                    "item_type",
                    "target_bloom",
                    "target_difficulty",
                    "points",
                    "permitted_resources",
                    "repetition_policy",
                    "field_provenance",
                },
            )
            pid = pos.get("blueprint_position_id")
            if not isinstance(pid, str) or not pid.strip():
                self.error(f"{path}.blueprint_position_id", "must be a non-empty string")
            elif pid in self.positions:
                self.error(f"{path}.blueprint_position_id", f"duplicate ID {pid!r}")
            else:
                self.positions[pid] = pos
            if not isinstance(pos.get("learning_outcome"), str) or not pos.get("learning_outcome", "").strip():
                self.error(f"{path}.learning_outcome", "must be a non-empty string")
            concepts = self.require_list(pos.get("assessed_concepts"), f"{path}.assessed_concepts")
            if not concepts or any(not isinstance(x, str) or not x.strip() for x in concepts):
                self.error(f"{path}.assessed_concepts", "must contain non-empty strings")
            if pos.get("item_type") not in {"mcq", "essay"}:
                self.error(f"{path}.item_type", "must be mcq or essay")
            if pos.get("target_bloom") not in BLOOM:
                self.error(f"{path}.target_bloom", "must be a revised Bloom level")
            if pos.get("item_type") == "mcq" and pos.get("target_bloom") == "Create":
                self.error(f"{path}.target_bloom", "fixed-response MCQs cannot target Create")
            if pos.get("target_difficulty") not in DIFFICULTY:
                self.error(f"{path}.target_difficulty", "must be Easy, Medium, or Hard")
            points = pos.get("points")
            if not isinstance(points, (int, float)) or isinstance(points, bool) or points <= 0:
                self.error(f"{path}.points", "must be a positive number")
            self.require_list(pos.get("permitted_resources"), f"{path}.permitted_resources")
            if pos.get("field_provenance") not in {"provided", "inferred", "mixed"}:
                self.error(f"{path}.field_provenance", "must be provided, inferred, or mixed")
            policy = self.require_object(pos.get("repetition_policy"), f"{path}.repetition_policy")
            self.require_keys(policy, f"{path}.repetition_policy", {"concept_repetition_authorized", "authorized_with_positions"})
            if not isinstance(policy.get("concept_repetition_authorized"), bool):
                self.error(f"{path}.repetition_policy.concept_repetition_authorized", "must be boolean")
            self.require_list(policy.get("authorized_with_positions"), f"{path}.repetition_policy.authorized_with_positions")

    def validate_exemplar_registries(self, value: Any) -> None:
        obj = self.require_object(value, "$.exemplar_registries")
        self.require_keys(obj, "$.exemplar_registries", {"calibration_exemplars", "run_exemplars"})
        calibration = self.require_list(obj.get("calibration_exemplars"), "$.exemplar_registries.calibration_exemplars")
        if len(calibration) > 5:
            self.error("$.exemplar_registries.calibration_exemplars", "cannot exceed five")
        ids: set[str] = set()
        for index, raw in enumerate(calibration):
            path = f"$.exemplar_registries.calibration_exemplars[{index}]"
            item = self.require_object(raw, path)
            self.require_keys(item, path, {"exemplar_id", "instructor_approved", "scope_expansion_allowed"})
            eid = item.get("exemplar_id")
            if not isinstance(eid, str) or not eid.strip() or eid in ids:
                self.error(f"{path}.exemplar_id", "must be a unique non-empty string")
            else:
                ids.add(eid)
            if item.get("instructor_approved") is not True:
                self.error(f"{path}.instructor_approved", "must be true")
            if item.get("scope_expansion_allowed") is not False:
                self.error(f"{path}.scope_expansion_allowed", "must be false")

        run = self.require_object(obj.get("run_exemplars"), "$.exemplar_registries.run_exemplars")
        self.require_keys(run, "$.exemplar_registries.run_exemplars", {"retention_policy", "accepted", "rejected"})
        if run.get("retention_policy") != "rolling_fifo":
            self.error("$.exemplar_registries.run_exemplars.retention_policy", "must be rolling_fifo")
        for bucket in ("accepted", "rejected"):
            entries = self.require_list(run.get(bucket), f"$.exemplar_registries.run_exemplars.{bucket}")
            if len(entries) > 5:
                self.error(f"$.exemplar_registries.run_exemplars.{bucket}", "cannot exceed five")
            for index, raw in enumerate(entries):
                path = f"$.exemplar_registries.run_exemplars.{bucket}[{index}]"
                item = self.require_object(raw, path)
                self.require_keys(
                    item,
                    path,
                    {
                        "candidate_id",
                        "item_summary",
                        "item_type",
                        "assessed_concepts",
                        "blueprint_position_id",
                        "verdict",
                        "justification",
                    },
                )

    def validate_budget(self, value: Any) -> None:
        obj = self.require_object(value, "$.generation_budget")
        expected = {
            "initial_candidates_per_position": 2,
            "fresh_replacements_per_position": 2,
            "max_revisions_per_candidate": 2,
            "sequential_generation_required": True,
        }
        self.require_keys(obj, "$.generation_budget", expected)
        for key, wanted in expected.items():
            if obj.get(key) != wanted:
                self.error(f"$.generation_budget.{key}", f"must equal {wanted!r}")

    def validate_candidates(self, value: Any) -> None:
        candidates = self.require_list(value, "$.candidates")
        generation_indices: set[int] = set()
        per_position: dict[str, list[dict[str, Any]]] = {}

        for index, raw in enumerate(candidates):
            path = f"$.candidates[{index}]"
            candidate = self.require_object(raw, path)
            self.validate_candidate(candidate, path)
            cid = candidate.get("candidate_id")
            if isinstance(cid, str) and cid:
                if cid in self.candidates:
                    self.error(f"{path}.candidate_id", f"duplicate ID {cid!r}")
                else:
                    self.candidates[cid] = candidate
            gi = candidate.get("generation_index")
            if not isinstance(gi, int) or isinstance(gi, bool) or gi < 1:
                self.error(f"{path}.generation_index", "must be a positive integer")
            elif gi in generation_indices:
                self.error(f"{path}.generation_index", "must be globally unique")
            else:
                generation_indices.add(gi)
            pid = candidate.get("blueprint_position_id")
            if isinstance(pid, str):
                per_position.setdefault(pid, []).append(candidate)

        for pid, items in per_position.items():
            ordered = sorted(items, key=lambda x: x.get("position_sequence", 10**9))
            sequences = [x.get("position_sequence") for x in ordered]
            if sequences != list(range(1, len(items) + 1)):
                self.error(f"$.candidates[{pid}]", "position_sequence must be contiguous from 1")
            if len(items) > 4:
                self.error(f"$.candidates[{pid}]", "exceeds two initial plus two replacement candidates")
            if sum(x.get("candidate_kind") == "initial" for x in items) > 2:
                self.error(f"$.candidates[{pid}]", "exceeds two initial candidates")
            if sum(x.get("candidate_kind") == "replacement" for x in items) > 2:
                self.error(f"$.candidates[{pid}]", "exceeds two replacements")
            for offset, candidate in enumerate(ordered):
                context = candidate.get("exemplar_context") if isinstance(candidate.get("exemplar_context"), dict) else {}
                preceding = context.get("preceding_same_position_candidate_id")
                if offset == 0:
                    if preceding is not None:
                        self.error(f"$.candidates[{candidate.get('candidate_id')}].exemplar_context", "first candidate must have no preceding same-position candidate")
                    continue
                previous = ordered[offset - 1]
                previous_id = previous.get("candidate_id")
                if preceding != previous_id:
                    self.error(f"$.candidates[{candidate.get('candidate_id')}].exemplar_context.preceding_same_position_candidate_id", f"must equal {previous_id!r}")
                memory = list(context.get("accepted_run_ids", [])) + list(context.get("rejected_run_ids", []))
                if previous_id not in memory:
                    self.error(f"$.candidates[{candidate.get('candidate_id')}].exemplar_context", "must include the immediately preceding candidate after its verdict")
                if isinstance(previous.get("generation_index"), int) and isinstance(candidate.get("generation_index"), int):
                    if previous["generation_index"] >= candidate["generation_index"]:
                        self.error(f"$.candidates[{candidate.get('candidate_id')}].generation_index", "must follow the preceding candidate's judgment")

    def validate_candidate(self, candidate: dict[str, Any], path: str) -> None:
        required = {
            "candidate_id",
            "blueprint_position_id",
            "generation_index",
            "position_sequence",
            "candidate_kind",
            "replacement_number",
            "revision_count",
            "item_type",
            "item",
            "scope_evidence",
            "answer_evidence",
            "scenario_origin",
            "assessed_concepts",
            "concept_signature",
            "target_bloom",
            "reviewed_bloom",
            "bloom_fit",
            "bloom_justification",
            "target_difficulty",
            "estimated_difficulty",
            "difficulty_fit",
            "difficulty_justification",
            "classification_review_context",
            "classification_revealed_before_target_comparison",
            "duplication",
            "exemplar_context",
            "rejection_checks",
            "blind_answer_checks",
            "final_judge",
            "verdict",
            "selected",
            "final_status",
        }
        self.require_keys(candidate, path, required)
        pid = candidate.get("blueprint_position_id")
        position = self.positions.get(pid)
        if position is None:
            self.error(f"{path}.blueprint_position_id", "does not identify a blueprint position")
        if candidate.get("candidate_kind") not in {"initial", "replacement"}:
            self.error(f"{path}.candidate_kind", "must be initial or replacement")
        replacement_number = candidate.get("replacement_number")
        if not isinstance(replacement_number, int) or isinstance(replacement_number, bool) or not 0 <= replacement_number <= 2:
            self.error(f"{path}.replacement_number", "must be an integer from 0 to 2")
        if candidate.get("candidate_kind") == "initial" and replacement_number != 0:
            self.error(f"{path}.replacement_number", "initial candidates must use 0")
        if candidate.get("candidate_kind") == "replacement" and replacement_number not in {1, 2}:
            self.error(f"{path}.replacement_number", "replacement candidates must use 1 or 2")
        revisions = candidate.get("revision_count")
        if not isinstance(revisions, int) or isinstance(revisions, bool) or not 0 <= revisions <= 2:
            self.error(f"{path}.revision_count", "must be an integer from 0 to 2")
        if candidate.get("item_type") not in {"mcq", "essay"}:
            self.error(f"{path}.item_type", "must be mcq or essay")
        if position and candidate.get("item_type") != position.get("item_type"):
            self.error(f"{path}.item_type", "does not match its blueprint position")

        self.validate_evidence(candidate.get("scope_evidence"), f"{path}.scope_evidence")
        self.validate_evidence(candidate.get("answer_evidence"), f"{path}.answer_evidence")
        if candidate.get("scenario_origin") not in SCENARIO_ORIGINS:
            self.error(f"{path}.scenario_origin", "has an unsupported value")
        concepts = self.require_list(candidate.get("assessed_concepts"), f"{path}.assessed_concepts")
        if not concepts:
            self.error(f"{path}.assessed_concepts", "cannot be empty")
        if not isinstance(candidate.get("concept_signature"), str) or not candidate.get("concept_signature", "").strip():
            self.error(f"{path}.concept_signature", "must be a non-empty string")

        for field in ("target_bloom", "reviewed_bloom"):
            if candidate.get(field) not in BLOOM:
                self.error(f"{path}.{field}", "must be a revised Bloom level")
        if candidate.get("item_type") == "mcq" and candidate.get("reviewed_bloom") == "Create":
            self.error(f"{path}.reviewed_bloom", "fixed-response MCQs cannot be Create")
        for field in ("target_difficulty", "estimated_difficulty"):
            if candidate.get(field) not in DIFFICULTY:
                self.error(f"{path}.{field}", "must be Easy, Medium, or Hard")
        for field in ("bloom_fit", "difficulty_fit"):
            if candidate.get(field) not in FITS:
                self.error(f"{path}.{field}", "must be pass or fail")
        if position:
            if candidate.get("target_bloom") != position.get("target_bloom"):
                self.error(f"{path}.target_bloom", "does not match blueprint target")
            if candidate.get("target_difficulty") != position.get("target_difficulty"):
                self.error(f"{path}.target_difficulty", "does not match blueprint target")
        for field in ("bloom_justification", "difficulty_justification"):
            if not isinstance(candidate.get(field), str) or not candidate.get(field, "").strip():
                self.error(f"{path}.{field}", "must be a concise observable justification")
        self.validate_review_context(
            candidate.get("classification_review_context"),
            f"{path}.classification_review_context",
            candidate.get("verdict"),
        )
        if candidate.get("classification_revealed_before_target_comparison") is not True:
            self.error(
                f"{path}.classification_revealed_before_target_comparison",
                "must be true",
            )
        if candidate.get("verdict") == "pass" and (
            candidate.get("bloom_fit") != "pass" or candidate.get("difficulty_fit") != "pass"
        ):
            self.error(path, "passing candidates require passing Bloom and difficulty fit")

        item = self.require_object(candidate.get("item"), f"{path}.item")
        if candidate.get("item_type") == "mcq":
            self.validate_mcq(item, candidate, path)
        elif candidate.get("item_type") == "essay":
            self.validate_essay(item, position, path)
        self.validate_duplication(candidate.get("duplication"), candidate, path)
        self.validate_exemplar_context(candidate.get("exemplar_context"), path)
        self.validate_rejection_checks(candidate.get("rejection_checks"), candidate, path)

        if candidate.get("verdict") not in VERDICTS:
            self.error(f"{path}.verdict", "has an unsupported value")
        if not isinstance(candidate.get("selected"), bool):
            self.error(f"{path}.selected", "must be boolean")
        if candidate.get("final_status") not in FINAL_STATUSES:
            self.error(f"{path}.final_status", "has an unsupported value")
        if candidate.get("selected") and candidate.get("verdict") != "pass":
            self.error(path, "selected candidates must have verdict pass")
        if candidate.get("selected") and candidate.get("final_status") != "selected":
            self.error(f"{path}.final_status", "must be selected when selected is true")

    def validate_run_exemplar_consistency(self, value: Any) -> None:
        registries = value if isinstance(value, dict) else {}
        run = registries.get("run_exemplars") if isinstance(registries.get("run_exemplars"), dict) else {}
        observed: dict[str, list[str]] = {"accepted": [], "rejected": []}
        for bucket in ("accepted", "rejected"):
            for entry in run.get(bucket, []) if isinstance(run.get(bucket), list) else []:
                if not isinstance(entry, dict):
                    continue
                cid = entry.get("candidate_id")
                if isinstance(cid, str):
                    observed[bucket].append(cid)
                    candidate = self.candidates.get(cid)
                    if candidate is None:
                        self.error(f"$.exemplar_registries.run_exemplars.{bucket}", f"unknown candidate {cid!r}")
                    elif bucket == "accepted" and candidate.get("verdict") != "pass":
                        self.error(f"$.exemplar_registries.run_exemplars.{bucket}", f"{cid!r} was not accepted")
                    elif bucket == "rejected" and candidate.get("verdict") == "pass":
                        self.error(f"$.exemplar_registries.run_exemplars.{bucket}", f"{cid!r} was accepted, not rejected")
        ordered = sorted(
            self.candidates.values(),
            key=lambda candidate: candidate.get("generation_index", 10**9),
        )
        expected_accepted = [candidate.get("candidate_id") for candidate in ordered if candidate.get("verdict") == "pass"][-5:]
        expected_rejected = [candidate.get("candidate_id") for candidate in ordered if candidate.get("verdict") != "pass"][-5:]
        if observed["accepted"] != expected_accepted:
            self.error("$.exemplar_registries.run_exemplars.accepted", "must contain the final FIFO window of accepted candidates in order")
        if observed["rejected"] != expected_rejected:
            self.error("$.exemplar_registries.run_exemplars.rejected", "must contain the final FIFO window of rejected candidates in order")

        for left, right in itertools.combinations(ordered, 2):
            left_text = normalize_text(candidate_prompt_text(left))
            right_text = normalize_text(candidate_prompt_text(right))
            if not left_text or not right_text:
                continue
            score = difflib.SequenceMatcher(None, left_text, right_text).ratio()
            later = right if right.get("generation_index", 0) > left.get("generation_index", 0) else left
            duplication = later.get("duplication") if isinstance(later.get("duplication"), dict) else {}
            if left_text == right_text and later.get("verdict") == "pass":
                self.error("$.candidates", f"exact duplicate {left.get('candidate_id')}/{right.get('candidate_id')} cannot pass")
            if score >= 0.85 and later.get("verdict") == "pass":
                if duplication.get("manual_review_required") is not True or duplication.get("manual_review_disposition") in {None, "", "not_required", "unresolved"}:
                    self.error("$.candidates", f"lexical similarity {score:.3f} for {left.get('candidate_id')}/{right.get('candidate_id')} requires resolved manual review")

    def validate_evidence(self, value: Any, path: str) -> None:
        entries = self.require_list(value, path)
        if not entries:
            self.error(path, "must contain at least one evidence entry")
        for index, raw in enumerate(entries):
            item_path = f"{path}[{index}]"
            item = self.require_object(raw, item_path)
            self.require_keys(item, item_path, {"source_id", "locator", "supports"})
            for key in ("source_id", "locator", "supports"):
                if not isinstance(item.get(key), str) or not item.get(key, "").strip():
                    self.error(f"{item_path}.{key}", "must be a non-empty string")

    def validate_mcq(self, item: dict[str, Any], candidate: dict[str, Any], path: str) -> None:
        item_path = f"{path}.item"
        self.require_keys(item, item_path, {"stem", "options", "correct_option_id", "answer_rationale"})
        if not isinstance(item.get("stem"), str) or not item.get("stem", "").strip():
            self.error(f"{item_path}.stem", "must be a non-empty string")
        options = self.require_list(item.get("options"), f"{item_path}.options")
        if len(options) < 3:
            self.error(f"{item_path}.options", "must contain at least three options; three strong options are the default")
        ids: set[str] = set()
        for index, raw in enumerate(options):
            option_path = f"{item_path}.options[{index}]"
            option = self.require_object(raw, option_path)
            self.require_keys(option, option_path, {"option_id", "text", "misconception_rationale"})
            oid = option.get("option_id")
            if not isinstance(oid, str) or not oid.strip() or oid in ids:
                self.error(f"{option_path}.option_id", "must be a unique non-empty stable ID")
            else:
                ids.add(oid)
            if not isinstance(option.get("text"), str) or not option.get("text", "").strip():
                self.error(f"{option_path}.text", "must be a non-empty string")
        key = item.get("correct_option_id")
        if key not in ids:
            self.error(f"{item_path}.correct_option_id", "must identify exactly one option")
        for index, option in enumerate(options):
            if not isinstance(option, dict):
                continue
            rationale = option.get("misconception_rationale")
            if option.get("option_id") == key:
                if rationale is not None and not isinstance(rationale, str):
                    self.error(f"{item_path}.options[{index}].misconception_rationale", "must be null or a string for the correct option")
            elif not isinstance(rationale, str) or not rationale.strip():
                self.error(f"{item_path}.options[{index}].misconception_rationale", "is required for each distractor")
        if not isinstance(item.get("answer_rationale"), str) or not item.get("answer_rationale", "").strip():
            self.error(f"{item_path}.answer_rationale", "must be a non-empty string")

        checks = self.require_list(candidate.get("blind_answer_checks"), f"{path}.blind_answer_checks")
        if candidate.get("verdict") == "pass" and len(checks) != 2:
            self.error(f"{path}.blind_answer_checks", "passing MCQs require exactly two blind checks")
        for index, raw in enumerate(checks):
            check_path = f"{path}.blind_answer_checks[{index}]"
            check = self.require_object(raw, check_path)
            self.require_keys(check, check_path, {"reviewer_id", "selected_option_id", "options_order", "options_reordered", "justification", "review_context"})
            if check.get("selected_option_id") not in ids:
                self.error(f"{check_path}.selected_option_id", "must identify an option")
            if candidate.get("verdict") == "pass" and check.get("selected_option_id") != key:
                self.error(f"{check_path}.selected_option_id", "must agree with the key for an automated pass")
            order = self.require_list(check.get("options_order"), f"{check_path}.options_order")
            if len(order) != len(ids) or set(order) != ids:
                self.error(f"{check_path}.options_order", "must list every stable option ID exactly once")
            if index == 1 and check.get("options_reordered") is not True:
                self.error(f"{check_path}.options_reordered", "second blind check must use reordered options")
            self.validate_review_context(check.get("review_context"), f"{check_path}.review_context", candidate.get("verdict"))

        final = self.require_object(candidate.get("final_judge"), f"{path}.final_judge")
        self.require_keys(final, f"{path}.final_judge", {"verdict", "selected_option_id", "justification", "review_context"})
        if candidate.get("verdict") == "pass":
            if final.get("verdict") != "pass" or final.get("selected_option_id") != key:
                self.error(f"{path}.final_judge", "must independently pass and agree by option ID")
        self.validate_review_context(final.get("review_context"), f"{path}.final_judge.review_context", candidate.get("verdict"))

    def validate_essay(self, item: dict[str, Any], position: dict[str, Any] | None, path: str) -> None:
        item_path = f"{path}.item"
        self.require_keys(item, item_path, {"prompt", "answer_outline", "defensible_alternatives", "rubric", "empirical_limitation_notice"})
        for key in ("prompt", "answer_outline", "empirical_limitation_notice"):
            if not isinstance(item.get(key), str) or not item.get(key, "").strip():
                self.error(f"{item_path}.{key}", "must be a non-empty string")
        self.require_list(item.get("defensible_alternatives"), f"{item_path}.defensible_alternatives")
        rubric = self.require_list(item.get("rubric"), f"{item_path}.rubric")
        total = 0.0
        for index, raw in enumerate(rubric):
            criterion_path = f"{item_path}.rubric[{index}]"
            criterion = self.require_object(raw, criterion_path)
            self.require_keys(criterion, criterion_path, {"criterion_id", "criterion", "max_points", "levels"})
            points = criterion.get("max_points")
            if not isinstance(points, (int, float)) or isinstance(points, bool) or points < 0:
                self.error(f"{criterion_path}.max_points", "must be a non-negative number")
            else:
                total += float(points)
            levels = self.require_object(criterion.get("levels"), f"{criterion_path}.levels")
            if len(levels) < 2:
                self.error(f"{criterion_path}.levels", "must contain at least two observable performance levels")
        if position and abs(total - float(position.get("points", 0))) > 1e-9:
            self.error(f"{item_path}.rubric", "criterion maxima must equal blueprint points")
        checks = self.require_list(self._candidate_value(path, "blind_answer_checks"), f"{path}.blind_answer_checks")
        if checks:
            self.error(f"{path}.blind_answer_checks", "essay candidates do not use MCQ blind answer checks")
        final = self.require_object(self._candidate_value(path, "final_judge"), f"{path}.final_judge")
        self.require_keys(final, f"{path}.final_judge", {"verdict", "scoring_expectations_supported", "justification", "review_context"})
        verdict = self._candidate_value(path, "verdict")
        if verdict == "pass" and (final.get("verdict") != "pass" or final.get("scoring_expectations_supported") is not True):
            self.error(f"{path}.final_judge", "must pass and support scoring expectations")
        self.validate_review_context(final.get("review_context"), f"{path}.final_judge.review_context", verdict)

    def _candidate_value(self, path: str, key: str) -> Any:
        match = re.fullmatch(r"\$\.candidates\[(\d+)\]", path)
        if not match or not isinstance(self.data, dict):
            return None
        candidates = self.data.get("candidates", [])
        index = int(match.group(1))
        if index >= len(candidates) or not isinstance(candidates[index], dict):
            return None
        return candidates[index].get(key)

    def validate_review_context(self, value: Any, path: str, verdict: Any) -> None:
        context = self.require_object(value, path)
        self.require_keys(context, path, {"isolation_method", "isolation_verified", *ISOLATION_FALSE_FIELDS})
        if context.get("isolation_method") != "fresh_reviewer_context":
            self.error(f"{path}.isolation_method", "must be fresh_reviewer_context")
        for field in ISOLATION_FALSE_FIELDS:
            if context.get(field) is not False:
                self.error(f"{path}.{field}", "must be false")
        if verdict == "pass" and context.get("isolation_verified") is not True:
            self.error(f"{path}.isolation_verified", "must be true for an automated pass")
        elif not isinstance(context.get("isolation_verified"), bool):
            self.error(f"{path}.isolation_verified", "must be boolean")

    def validate_duplication(self, value: Any, candidate: dict[str, Any], path: str) -> None:
        dup = self.require_object(value, f"{path}.duplication")
        self.require_keys(
            dup,
            f"{path}.duplication",
            {
                "same_position_overlap",
                "cross_position_overlap",
                "solution_route_overlap",
                "max_lexical_similarity",
                "lexical_method",
                "compared_candidate_ids",
                "manual_review_required",
                "manual_review_disposition",
            },
        )
        if dup.get("same_position_overlap") not in {"expected", "excessive"}:
            self.error(f"{path}.duplication.same_position_overlap", "must be expected or excessive")
        if dup.get("cross_position_overlap") not in {"none", "partial", "substantive"}:
            self.error(f"{path}.duplication.cross_position_overlap", "must be none, partial, or substantive")
        if dup.get("solution_route_overlap") not in {"distinct", "partial", "equivalent"}:
            self.error(f"{path}.duplication.solution_route_overlap", "must be distinct, partial, or equivalent")
        similarity = dup.get("max_lexical_similarity")
        if not isinstance(similarity, (int, float)) or isinstance(similarity, bool) or not 0 <= similarity <= 1:
            self.error(f"{path}.duplication.max_lexical_similarity", "must be between 0 and 1")
        self.require_list(dup.get("compared_candidate_ids"), f"{path}.duplication.compared_candidate_ids")
        if not isinstance(dup.get("manual_review_required"), bool):
            self.error(f"{path}.duplication.manual_review_required", "must be boolean")
        if candidate.get("verdict") == "pass":
            if dup.get("same_position_overlap") == "excessive" or dup.get("solution_route_overlap") == "equivalent":
                self.error(f"{path}.duplication", "excessive same-position duplication cannot pass")
            if dup.get("cross_position_overlap") == "substantive":
                if not (dup.get("repetition_authorized") is True and dup.get("materially_distinct_cognition_or_evidence") is True):
                    self.error(f"{path}.duplication", "substantive cross-position overlap requires authorization and material distinction")
            if isinstance(similarity, (int, float)) and similarity >= 0.85:
                if dup.get("manual_review_required") is not True or dup.get("manual_review_disposition") in {None, "", "not_required", "unresolved"}:
                    self.error(f"{path}.duplication", "lexical similarity >= 0.85 requires a resolved manual review")

    def validate_exemplar_context(self, value: Any, path: str) -> None:
        context = self.require_object(value, f"{path}.exemplar_context")
        self.require_keys(context, f"{path}.exemplar_context", {"calibration_ids", "accepted_run_ids", "rejected_run_ids", "preceding_same_position_candidate_id"})
        for field in ("calibration_ids", "accepted_run_ids", "rejected_run_ids"):
            entries = self.require_list(context.get(field), f"{path}.exemplar_context.{field}")
            if len(entries) > 5:
                self.error(f"{path}.exemplar_context.{field}", "cannot exceed five")

    def validate_rejection_checks(self, value: Any, candidate: dict[str, Any], path: str) -> None:
        checks = self.require_list(value, f"{path}.rejection_checks")
        seen: set[str] = set()
        results: dict[str, Any] = {}
        for index, raw in enumerate(checks):
            check_path = f"{path}.rejection_checks[{index}]"
            check = self.require_object(raw, check_path)
            self.require_keys(check, check_path, {"criterion", "result", "justification"})
            if isinstance(check.get("criterion"), str):
                criterion = check["criterion"]
                if criterion in seen:
                    self.error(f"{check_path}.criterion", "must not duplicate another rejection criterion")
                seen.add(criterion)
                results[criterion] = check.get("result")
            if check.get("result") not in {"pass", "fail", "not_applicable"}:
                self.error(f"{check_path}.result", "must be pass, fail, or not_applicable")
            if not isinstance(check.get("justification"), str) or not check.get("justification", "").strip():
                self.error(f"{check_path}.justification", "must be a non-empty concise observation")
        missing = REQUIRED_REJECTION_CRITERIA - seen
        if missing:
            self.error(f"{path}.rejection_checks", f"missing criteria: {', '.join(sorted(missing))}")
        if candidate.get("verdict") == "pass":
            failed = sorted(criterion for criterion in REQUIRED_REJECTION_CRITERIA if results.get(criterion) == "fail")
            if failed:
                self.error(f"{path}.rejection_checks", f"passing candidates cannot fail criteria: {', '.join(failed)}")
            if candidate.get("item_type") == "mcq":
                inapplicable = sorted(
                    criterion for criterion in REQUIRED_REJECTION_CRITERIA
                    if results.get(criterion) == "not_applicable"
                )
                if inapplicable:
                    self.error(
                        f"{path}.rejection_checks",
                        f"passing MCQs must resolve every required criterion: {', '.join(inapplicable)}",
                    )

    def validate_final_selection(self, value: Any) -> None:
        obj = self.require_object(value, "$.final_selection")
        required = {
            "selected_candidate_ids",
            "by_position",
            "assessment_duplication_pass",
            "blueprint_coverage_verified",
            "bloom_distribution_verified",
            "difficulty_distribution_verified",
            "item_type_distribution_verified",
            "points_verified",
            "answer_key_membership_verified",
        }
        self.require_keys(obj, "$.final_selection", required)
        selected = self.require_list(obj.get("selected_candidate_ids"), "$.final_selection.selected_candidate_ids")
        by_position = self.require_object(obj.get("by_position"), "$.final_selection.by_position")
        if len(selected) != len(set(selected)):
            self.error("$.final_selection.selected_candidate_ids", "must not contain duplicates")
        if set(by_position) != set(self.positions):
            self.error("$.final_selection.by_position", "must contain exactly one entry for every blueprint position")
        if set(by_position.values()) != set(selected):
            self.error("$.final_selection", "selected_candidate_ids and by_position values must match")
        for pid, cid in by_position.items():
            candidate = self.candidates.get(cid)
            if candidate is None:
                self.error(f"$.final_selection.by_position.{pid}", "references an unknown candidate")
                continue
            if candidate.get("blueprint_position_id") != pid:
                self.error(f"$.final_selection.by_position.{pid}", "candidate belongs to another position")
            if candidate.get("verdict") != "pass" or candidate.get("selected") is not True:
                self.error(f"$.final_selection.by_position.{pid}", "candidate must be selected and passed")
        for field in (
            "blueprint_coverage_verified",
            "bloom_distribution_verified",
            "difficulty_distribution_verified",
            "item_type_distribution_verified",
            "points_verified",
            "answer_key_membership_verified",
        ):
            if obj.get(field) is not True:
                self.error(f"$.final_selection.{field}", "must be true")

        duplication = self.require_object(obj.get("assessment_duplication_pass"), "$.final_selection.assessment_duplication_pass")
        self.require_keys(duplication, "$.final_selection.assessment_duplication_pass", {"completed", "run_count", "status", "comparisons", "replacement_history"})
        if duplication.get("completed") is not True or duplication.get("status") != "pass":
            self.error("$.final_selection.assessment_duplication_pass", "must be completed with status pass")
        if not isinstance(duplication.get("run_count"), int) or duplication.get("run_count", 0) < 1:
            self.error("$.final_selection.assessment_duplication_pass.run_count", "must be a positive integer")
        history = self.require_list(duplication.get("replacement_history"), "$.final_selection.assessment_duplication_pass.replacement_history")
        if isinstance(duplication.get("run_count"), int) and duplication.get("run_count") < len(history) + 1:
            self.error("$.final_selection.assessment_duplication_pass.run_count", "must reflect a full rerun after each replacement")
        comparisons = self.require_list(duplication.get("comparisons"), "$.final_selection.assessment_duplication_pass.comparisons")
        expected_pairs = {frozenset(pair) for pair in itertools.combinations(selected, 2)}
        observed_pairs: set[frozenset[str]] = set()
        for index, raw in enumerate(comparisons):
            path = f"$.final_selection.assessment_duplication_pass.comparisons[{index}]"
            comparison = self.require_object(raw, path)
            self.require_keys(
                comparison,
                path,
                {
                    "candidate_ids",
                    "blueprint_position_ids",
                    "cross_position_overlap",
                    "lexical_similarity",
                    "repetition_authorized",
                    "materially_distinct_cognition_or_evidence",
                    "manual_review_disposition",
                    "disposition",
                    "justification",
                },
            )
            ids = self.require_list(comparison.get("candidate_ids"), f"{path}.candidate_ids")
            if len(ids) == 2:
                observed_pairs.add(frozenset(ids))
            if comparison.get("cross_position_overlap") not in {"none", "partial", "substantive"}:
                self.error(f"{path}.cross_position_overlap", "has an unsupported value")
            similarity = comparison.get("lexical_similarity")
            if not isinstance(similarity, (int, float)) or isinstance(similarity, bool) or not 0 <= similarity <= 1:
                self.error(f"{path}.lexical_similarity", "must be between 0 and 1")
            if comparison.get("cross_position_overlap") == "substantive":
                if not (comparison.get("repetition_authorized") is True and comparison.get("materially_distinct_cognition_or_evidence") is True):
                    self.error(path, "substantive overlap requires authorized repetition and material distinction")
            if isinstance(similarity, (int, float)) and similarity >= 0.85:
                if comparison.get("manual_review_disposition") in {None, "", "not_required", "unresolved"}:
                    self.error(f"{path}.manual_review_disposition", "must resolve lexical similarity >= 0.85")
            if comparison.get("disposition") != "pass":
                self.error(f"{path}.disposition", "must be pass in a passing selected-set review")
        if observed_pairs != expected_pairs:
            self.error("$.final_selection.assessment_duplication_pass.comparisons", "must contain every selected-item pair exactly once")
        self.validate_computed_lexical(selected, comparisons)

    def validate_computed_lexical(self, selected: list[Any], comparisons: list[Any]) -> None:
        lookup: dict[frozenset[str], dict[str, Any]] = {}
        for comparison in comparisons:
            if isinstance(comparison, dict) and isinstance(comparison.get("candidate_ids"), list) and len(comparison["candidate_ids"]) == 2:
                lookup[frozenset(comparison["candidate_ids"])] = comparison
        for left, right in itertools.combinations(selected, 2):
            if not isinstance(left, str) or not isinstance(right, str):
                continue
            a = self.candidates.get(left)
            b = self.candidates.get(right)
            if not a or not b:
                continue
            text_a = candidate_prompt_text(a)
            text_b = candidate_prompt_text(b)
            norm_a, norm_b = normalize_text(text_a), normalize_text(text_b)
            comparison = lookup.get(frozenset({left, right}), {})
            if norm_a and norm_a == norm_b:
                self.error("$.final_selection.assessment_duplication_pass", f"selected items {left} and {right} are exact normalized duplicates")
            score = difflib.SequenceMatcher(None, norm_a, norm_b).ratio() if norm_a and norm_b else 0.0
            if score >= 0.85 and comparison.get("manual_review_disposition") in {None, "", "not_required", "unresolved"}:
                self.error("$.final_selection.assessment_duplication_pass", f"computed lexical similarity for {left}/{right} is {score:.3f} and requires resolved manual review")

    def validate_approval(self, value: Any, root: dict[str, Any]) -> None:
        obj = self.require_object(value, "$.instructor_approval")
        self.require_keys(obj, "$.instructor_approval", {"blueprint", "final"})
        blueprint = self.require_object(obj.get("blueprint"), "$.instructor_approval.blueprint")
        final = self.require_object(obj.get("final"), "$.instructor_approval.final")
        for section, data in (("blueprint", blueprint), ("final", final)):
            self.require_keys(data, f"$.instructor_approval.{section}", {"status", "approved_by", "approved_at"})
        if blueprint.get("status") != "approved" or not blueprint.get("approved_by") or not blueprint.get("approved_at"):
            self.error("$.instructor_approval.blueprint", "must record approval before generation")
        workflow = root.get("workflow_status")
        if workflow == "approved_for_delivery":
            if final.get("status") != "approved" or not final.get("approved_by") or not final.get("approved_at"):
                self.error("$.instructor_approval.final", "must be approved for delivery")
        elif workflow == "awaiting_final_approval" and final.get("status") != "pending":
            self.error("$.instructor_approval.final.status", "must be pending while awaiting final approval")

    def validate_escalations(self, value: Any, root: dict[str, Any]) -> None:
        escalations = self.require_list(value, "$.escalations")
        unresolved = False
        for index, raw in enumerate(escalations):
            path = f"$.escalations[{index}]"
            item = self.require_object(raw, path)
            self.require_keys(item, path, {"escalation_id", "reason", "status"})
            if item.get("status") not in {"resolved", "unresolved"}:
                self.error(f"{path}.status", "must be resolved or unresolved")
            unresolved = unresolved or item.get("status") == "unresolved"
        if root.get("workflow_status") == "approved_for_delivery" and unresolved:
            self.error("$.escalations", "approved delivery cannot contain unresolved escalations")

    def validate_compact_observations(self, value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = key.lower().replace(" ", "_")
                if normalized in FORBIDDEN_REASONING_KEYS:
                    self.error(f"{path}.{key}", "must not store chain-of-thought or hidden reasoning")
                if "justification" in normalized and isinstance(child, str) and len(child) > 500:
                    self.error(f"{path}.{key}", "must be concise (500 characters or fewer)")
                self.validate_compact_observations(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.validate_compact_observations(child, f"{path}[{index}]")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def candidate_prompt_text(candidate: dict[str, Any]) -> str:
    item = candidate.get("item", {})
    if not isinstance(item, dict):
        return ""
    return str(item.get("stem") or item.get("prompt") or "")


def review_context() -> dict[str, Any]:
    return {
        "isolation_method": "fresh_reviewer_context",
        "isolation_verified": True,
        "key_visible": False,
        "prior_verdicts_visible": False,
        "rationale_visible": False,
        "revision_history_visible": False,
        "target_metadata_visible": False,
    }


def rejection_checks() -> list[dict[str, str]]:
    return [
        {"criterion": criterion, "result": "pass", "justification": "No disqualifying feature is observable."}
        for criterion in sorted(REQUIRED_REJECTION_CRITERIA)
    ]


def base_candidate(cid: str, pid: str, gi: int, seq: int, item_type: str, selected: bool) -> dict[str, Any]:
    key = "opt-2"
    if item_type == "mcq":
        item: dict[str, Any] = {
            "stem": f"Which grounded application best resolves case {cid}?",
            "options": [
                {"option_id": "opt-1", "text": "Use the unrelated rule.", "misconception_rationale": "Confuses adjacent principles."},
                {"option_id": "opt-2", "text": "Apply the supported rule.", "misconception_rationale": None},
                {"option_id": "opt-3", "text": "Ignore the relevant evidence.", "misconception_rationale": "Treats evidence as optional."},
            ],
            "correct_option_id": key,
            "answer_rationale": "The supported rule directly addresses the stated evidence.",
        }
        blind = [
            {
                "reviewer_id": f"{cid}-S1",
                "selected_option_id": key,
                "options_order": ["opt-1", "opt-2", "opt-3"],
                "options_reordered": False,
                "justification": "The supported rule is the only option consistent with the case.",
                "review_context": review_context(),
            },
            {
                "reviewer_id": f"{cid}-S2",
                "selected_option_id": key,
                "options_order": ["opt-3", "opt-1", "opt-2"],
                "options_reordered": True,
                "justification": "The same stable option remains correct after reordering.",
                "review_context": review_context(),
            },
        ]
        final_judge = {
            "verdict": "pass",
            "selected_option_id": key,
            "justification": "The item is grounded, aligned, and has one supported answer.",
            "review_context": review_context(),
        }
        bloom = "Apply"
    else:
        item = {
            "prompt": f"Evaluate the grounded decision in case {cid} using two criteria.",
            "answer_outline": "Apply both criteria, weigh the evidence, and defend a conclusion.",
            "defensible_alternatives": ["Either conclusion may earn credit when supported by both criteria."],
            "rubric": [
                {
                    "criterion_id": "R1",
                    "criterion": "Use of the two criteria",
                    "max_points": 3,
                    "levels": {"insufficient": "Uses neither accurately.", "sufficient": "Uses both accurately."},
                },
                {
                    "criterion_id": "R2",
                    "criterion": "Evidence-based judgment",
                    "max_points": 3,
                    "levels": {"insufficient": "No supported judgment.", "sufficient": "Defends a supported judgment."},
                },
            ],
            "empirical_limitation_notice": "Isley et al. (2025) did not empirically evaluate essay generation or rubrics.",
        }
        blind = []
        final_judge = {
            "verdict": "pass",
            "scoring_expectations_supported": True,
            "justification": "The prompt and rubric elicit observable evaluation evidence.",
            "review_context": review_context(),
        }
        bloom = "Evaluate"
    return {
        "candidate_id": cid,
        "blueprint_position_id": pid,
        "generation_index": gi,
        "position_sequence": seq,
        "candidate_kind": "initial",
        "replacement_number": 0,
        "revision_count": 0,
        "item_type": item_type,
        "item": item,
        "scope_evidence": [{"source_id": "COURSE-1", "locator": "section 2", "supports": "The assessed principle is in scope."}],
        "answer_evidence": [{"source_id": "COURSE-1", "locator": "section 2.1", "supports": "The rule or scoring expectation is supported."}],
        "scenario_origin": "constructed",
        "assessed_concepts": [f"concept-{pid}"],
        "concept_signature": f"{pid}:supported-decision",
        "target_bloom": bloom,
        "reviewed_bloom": bloom,
        "bloom_fit": "pass",
        "bloom_justification": "The response must perform the stated cognitive operation on case evidence.",
        "target_difficulty": "Medium",
        "estimated_difficulty": "Medium",
        "difficulty_fit": "pass",
        "difficulty_justification": "The task requires two linked steps with limited integration.",
        "classification_review_context": review_context(),
        "classification_revealed_before_target_comparison": True,
        "duplication": {
            "same_position_overlap": "expected",
            "cross_position_overlap": "none",
            "solution_route_overlap": "distinct",
            "max_lexical_similarity": 0.3,
            "lexical_method": "NFKC casefold, punctuation removal, whitespace collapse, SequenceMatcher",
            "compared_candidate_ids": [],
            "manual_review_required": False,
            "manual_review_disposition": "not_required",
        },
        "exemplar_context": {
            "calibration_ids": [],
            "accepted_run_ids": [],
            "rejected_run_ids": [],
            "preceding_same_position_candidate_id": None,
        },
        "rejection_checks": rejection_checks(),
        "blind_answer_checks": blind,
        "final_judge": final_judge,
        "verdict": "pass",
        "selected": selected,
        "final_status": "selected" if selected else "eligible",
    }


def run_exemplar_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["candidate_id"],
        "item_summary": candidate_prompt_text(candidate),
        "item_type": candidate["item_type"],
        "assessed_concepts": list(candidate["assessed_concepts"]),
        "blueprint_position_id": candidate["blueprint_position_id"],
        "verdict": candidate["verdict"],
        "justification": "The recorded candidate verdict determines its bounded run-memory bucket.",
    }


def valid_fixture() -> dict[str, Any]:
    a1 = base_candidate("BP-01-C1", "BP-01", 1, 1, "mcq", True)
    a2 = base_candidate("BP-01-C2", "BP-01", 2, 2, "mcq", False)
    a2["item"]["stem"] = "In a new case, which action correctly applies the authorized principle?"
    a2["exemplar_context"]["accepted_run_ids"] = ["BP-01-C1"]
    a2["exemplar_context"]["preceding_same_position_candidate_id"] = "BP-01-C1"
    b1 = base_candidate("BP-02-C1", "BP-02", 3, 1, "essay", True)
    b1["exemplar_context"]["accepted_run_ids"] = ["BP-01-C1", "BP-01-C2"]
    b2 = base_candidate("BP-02-C2", "BP-02", 4, 2, "essay", False)
    b2["item"]["prompt"] = "Judge the alternative course of action against the approved criteria and defend the result."
    b2["exemplar_context"]["accepted_run_ids"] = ["BP-01-C1", "BP-01-C2", "BP-02-C1"]
    b2["exemplar_context"]["preceding_same_position_candidate_id"] = "BP-02-C1"
    return {
        "schema_version": RELEASE,
        "workflow_status": "awaiting_final_approval",
        "metadata": {
            "release": RELEASE,
            "manifest_version": MANIFEST_VERSION,
            "assessment_language": "nl",
            "created_at": "2026-08-28T12:00:00+02:00",
            "research_basis": {
                "citation": "Isley, C. et al. (2025). Assessing the Quality of AI-Generated Exams: A Large-Scale Field Study. arXiv:2508.08314v1.",
                "extension_not_replication": True,
                "direct_empirical_scope": "short college-level multiple-choice items",
                "essay_workflow_empirically_validated": False,
                "model_difficulty_is_irt": False,
                "post_administration_psychometrics_included": False,
            },
        },
        "blueprint": {
            "kind": "approved_blueprint",
            "status": "approved",
            "positions": [
                {
                    "blueprint_position_id": "BP-01",
                    "learning_outcome": "Apply a supported principle to a case.",
                    "assessed_concepts": ["application"],
                    "item_type": "mcq",
                    "target_bloom": "Apply",
                    "target_difficulty": "Medium",
                    "points": 2,
                    "permitted_resources": ["none"],
                    "repetition_policy": {"concept_repetition_authorized": False, "authorized_with_positions": []},
                    "field_provenance": "provided",
                },
                {
                    "blueprint_position_id": "BP-02",
                    "learning_outcome": "Evaluate a decision using two criteria.",
                    "assessed_concepts": ["evaluation"],
                    "item_type": "essay",
                    "target_bloom": "Evaluate",
                    "target_difficulty": "Medium",
                    "points": 6,
                    "permitted_resources": ["course summary"],
                    "repetition_policy": {"concept_repetition_authorized": False, "authorized_with_positions": []},
                    "field_provenance": "provided",
                },
            ],
        },
        "exemplar_registries": {
            "calibration_exemplars": [],
            "run_exemplars": {
                "retention_policy": "rolling_fifo",
                "accepted": [
                    run_exemplar_entry(a1),
                    run_exemplar_entry(a2),
                    run_exemplar_entry(b1),
                    run_exemplar_entry(b2),
                ],
                "rejected": [],
            },
        },
        "generation_budget": {
            "initial_candidates_per_position": 2,
            "fresh_replacements_per_position": 2,
            "max_revisions_per_candidate": 2,
            "sequential_generation_required": True,
        },
        "candidates": [a1, a2, b1, b2],
        "final_selection": {
            "selected_candidate_ids": ["BP-01-C1", "BP-02-C1"],
            "by_position": {"BP-01": "BP-01-C1", "BP-02": "BP-02-C1"},
            "assessment_duplication_pass": {
                "completed": True,
                "run_count": 1,
                "status": "pass",
                "comparisons": [
                    {
                        "candidate_ids": ["BP-01-C1", "BP-02-C1"],
                        "blueprint_position_ids": ["BP-01", "BP-02"],
                        "cross_position_overlap": "none",
                        "lexical_similarity": 0.11,
                        "repetition_authorized": False,
                        "materially_distinct_cognition_or_evidence": True,
                        "manual_review_disposition": "not_required",
                        "disposition": "pass",
                        "justification": "The items assess different concepts through different response processes.",
                    }
                ],
                "replacement_history": [],
            },
            "blueprint_coverage_verified": True,
            "bloom_distribution_verified": True,
            "difficulty_distribution_verified": True,
            "item_type_distribution_verified": True,
            "points_verified": True,
            "answer_key_membership_verified": True,
        },
        "escalations": [],
        "instructor_approval": {
            "blueprint": {"status": "approved", "approved_by": "instructor", "approved_at": "2026-08-28T11:00:00+02:00"},
            "final": {"status": "pending", "approved_by": None, "approved_at": None},
        },
    }


def run_self_tests() -> int:
    tests: list[tuple[str, Any, bool]] = []
    tests.append(("valid mixed MCQ/essay and Dutch output", valid_fixture(), True))

    bad = valid_fixture()
    bad["generation_budget"]["fresh_replacements_per_position"] = 99
    tests.append(("generation budget overflow", bad, False))

    bad = valid_fixture()
    bad["candidates"][1]["exemplar_context"]["accepted_run_ids"] = []
    tests.append(("sequential exemplar refresh missing", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["duplication"]["same_position_overlap"] = "excessive"
    tests.append(("same-position excessive duplication", bad, False))

    good = valid_fixture()
    good["candidates"][1]["assessed_concepts"] = list(good["candidates"][0]["assessed_concepts"])
    good["candidates"][1]["duplication"]["same_position_overlap"] = "expected"
    tests.append(("same-position construct overlap is allowed", good, True))

    bad = valid_fixture()
    comparison = bad["final_selection"]["assessment_duplication_pass"]["comparisons"][0]
    comparison["cross_position_overlap"] = "substantive"
    comparison["repetition_authorized"] = False
    tests.append(("cross-position substantive overlap", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["scope_evidence"] = []
    tests.append(("unsupported concept evidence", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["answer_evidence"] = []
    tests.append(("separate answer evidence", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["revision_count"] = 3
    tests.append(("revision budget exhausted", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["blind_answer_checks"][1]["options_reordered"] = False
    tests.append(("blind second-pass reordering", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["blind_answer_checks"][0]["review_context"]["isolation_verified"] = False
    tests.append(("missing reviewer isolation", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["rejection_checks"] = []
    tests.append(("explicit rejection criteria", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["rejection_checks"] = [
        check for check in bad["candidates"][0]["rejection_checks"]
        if check["criterion"] != "one_best_answer"
    ]
    tests.append(("missing canonical MCQ criterion", bad, False))

    bad = valid_fixture()
    next(
        check for check in bad["candidates"][0]["rejection_checks"]
        if check["criterion"] == "one_best_answer"
    )["result"] = "not_applicable"
    tests.append(("passing MCQ cannot skip a quality criterion", bad, False))

    bad = valid_fixture()
    next(
        check for check in bad["candidates"][0]["rejection_checks"]
        if check["criterion"] == "distractor_quality"
    )["result"] = "fail"
    tests.append(("passing candidate cannot fail a quality criterion", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["item"]["options"] = bad["candidates"][0]["item"]["options"][:2]
    bad["candidates"][0]["blind_answer_checks"][0]["options_order"] = ["opt-1", "opt-2"]
    bad["candidates"][0]["blind_answer_checks"][1]["options_order"] = ["opt-2", "opt-1"]
    tests.append(("fewer than three MCQ options", bad, False))

    bad = valid_fixture()
    bad["schema_version"] = "2026.1"
    tests.append(("obsolete audit schema version", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["item"]["correct_option_id"] = "opt-4"
    tests.append(("answer key outside reduced option set", bad, False))

    bad = valid_fixture()
    bad["candidates"][2]["item"]["rubric"][0]["max_points"] = 2
    tests.append(("essay rubric total", bad, False))

    bad = valid_fixture()
    bad["candidates"][0]["chain_of_thought"] = "private reasoning"
    tests.append(("chain-of-thought field", bad, False))

    good = valid_fixture()
    reviewed = good["candidates"][1]
    reviewed["reviewed_bloom"] = "Analyze"
    reviewed["estimated_difficulty"] = "Hard"
    reviewed["bloom_fit"] = "fail"
    reviewed["difficulty_fit"] = "fail"
    reviewed["verdict"] = "revise"
    reviewed["final_status"] = "revision_required"
    good["candidates"][2]["exemplar_context"]["accepted_run_ids"] = ["BP-01-C1"]
    good["candidates"][2]["exemplar_context"]["rejected_run_ids"] = ["BP-01-C2"]
    good["candidates"][3]["exemplar_context"]["accepted_run_ids"] = ["BP-01-C1", "BP-02-C1"]
    good["candidates"][3]["exemplar_context"]["rejected_run_ids"] = ["BP-01-C2"]
    good["exemplar_registries"]["run_exemplars"]["accepted"] = [
        run_exemplar_entry(good["candidates"][0]),
        run_exemplar_entry(good["candidates"][2]),
        run_exemplar_entry(good["candidates"][3]),
    ]
    good["exemplar_registries"]["run_exemplars"]["rejected"] = [run_exemplar_entry(reviewed)]
    tests.append(("reviewed Bloom and difficulty may differ from targets", good, True))

    bad = valid_fixture()
    bad["final_selection"]["assessment_duplication_pass"]["completed"] = False
    tests.append(("selected-set duplication pass", bad, False))

    bad = valid_fixture()
    bad["workflow_status"] = "approved_for_delivery"
    tests.append(("mandatory final instructor approval", bad, False))

    failures = 0
    for name, fixture, expected_valid in tests:
        errors = AuditValidator(fixture).validate()
        actual_valid = not errors
        if actual_valid != expected_valid:
            failures += 1
            print(f"FAIL: {name} (expected valid={expected_valid}, got {actual_valid})")
            for error in errors[:5]:
                print(f"  {error}")
        else:
            print(f"PASS: {name}")
    print(f"\n{len(tests) - failures}/{len(tests)} fixture tests passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Assessment Item Designer 2026.2 quality audit.")
    parser.add_argument("audit", nargs="?", type=Path, help="Path to quality-audit.json")
    parser.add_argument("--self-test", action="store_true", help="Run built-in valid and invalid fixture tests")
    parser.add_argument("--quiet", action="store_true", help="Print only errors")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()
    if args.audit is None:
        parser.error("provide an audit path or use --self-test")
    try:
        data = json.loads(args.audit.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.audit}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid UTF-8 JSON: {exc}", file=sys.stderr)
        return 2
    errors = AuditValidator(data).validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Audit invalid: {len(errors)} error(s)")
        return 1
    if not args.quiet:
        print("Audit valid: declared 2026.2 structure and invariants passed.")
        print("Semantic judgments, source truth, reviewer independence, and human identity were not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
