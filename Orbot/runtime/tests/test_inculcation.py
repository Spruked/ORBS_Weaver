"""Desktop extensions to the source harness outline, not a canonical semantic judge."""
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from runtime.cognition_governance.inculcation import (
    ROOT, SOURCE, TITLES, FoundationError, FoundationLoader, canonical, compile_foundation, digest,
)
from runtime.communication.conformance import ConformanceError, validate_response, validate_tool_correspondence
from runtime.communication.providers import LlamaCppProvider, RemoteChatProvider


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "inculcation"
        shutil.copytree(ROOT, self.root)
        self.loader = FoundationLoader(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_invariant_baseline_first(self):
        f = self.loader.load()
        artifact = json.loads(f.artifact_json)
        self.assertEqual([s["title"] for s in artifact["training_sections"]], list(TITLES))
        self.assertLess(f.prefix.index("Ground reasoning in evidence"), f.prefix.index("## 1. Who am I?"))
        self.assertIn("Consider competing explanations", f.prefix)
        self.assertIn("Do not substitute generic advice", f.prefix)
        self.assertIn("Recognize when changing one component", f.prefix)

    def test_protected_snapshot_is_reused(self):
        f = self.loader.load()
        self.assertIs(f, self.loader.load())
        self.assertEqual(self.loader.loads, 1)
        with self.assertRaises(FrozenInstanceError):
            f.prefix = "conversation replacement"

    def test_restart_reconstructs_identical_foundation(self):
        first = self.loader.load()
        restored = FoundationLoader(self.root).load()
        self.assertEqual(first, restored)
        self.assertIsNot(first, restored)

    def test_changed_compiled_content_is_rejected(self):
        self.loader.load()
        path = self.root / "inculcation.compiled.json"
        path.write_bytes(path.read_bytes().replace(b"Orbot", b"Other"))
        with self.assertRaises(FoundationError):
            self.loader.load()

    def test_missing_activation_is_rejected(self):
        (self.root / "activation.json").unlink()
        with self.assertRaises(FoundationError):
            self.loader.load()

    def test_wrong_activation_version_is_rejected(self):
        path = self.root / "activation.json"
        data = json.loads(path.read_bytes())
        data["version"] = "9.9"
        path.write_bytes(canonical(data))
        with self.assertRaises(FoundationError):
            self.loader.load()

    def test_malformed_activation_is_an_explicit_foundation_failure(self):
        (self.root / "activation.json").write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(FoundationError, "Invalid foundation JSON"):
            self.loader.load()

    def test_pinned_reference_change_is_rejected(self):
        path = self.root / "references/ORB_Inculcation_Harness_Outline.txt"
        path.write_text("Changed outline", encoding="utf-8")
        with self.assertRaisesRegex(FoundationError, "Source integrity"):
            self.loader.load()

    def test_baseline_change_cannot_be_hidden_by_source_hash_update(self):
        path = self.root / "Core_Four_Baseline.txt"
        path.write_text("Ground reasoning in evidence", encoding="utf-8")
        manifest = json.loads((self.root / "sources.json").read_bytes())
        manifest["Core_Four_Baseline.txt"] = digest(path.read_bytes())
        (self.root / "sources.json").write_bytes(canonical(manifest))
        with self.assertRaisesRegex(FoundationError, "complete canonical"):
            self.loader.load()

    def test_new_compilation_without_activation_is_rejected(self):
        current = self.loader.load().version
        path = self.root / SOURCE
        path.write_text(path.read_text(encoding="utf-8").replace("Version: " + current, "Version: 9.0"), encoding="utf-8")
        (self.root / "inculcation.compiled.json").write_bytes(canonical(compile_foundation(self.root)))
        with self.assertRaisesRegex(FoundationError, "not been activated"):
            self.loader.load()

    def test_explicit_offline_version_update_invalidates_snapshot(self):
        before = self.loader.load()
        path = self.root / SOURCE
        path.write_text(path.read_text(encoding="utf-8").replace("Version: " + before.version, "Version: 9.0"), encoding="utf-8")
        data = canonical(compile_foundation(self.root))
        (self.root / "inculcation.compiled.json").write_bytes(data)
        result = subprocess.run([sys.executable, "-B", "-m", "runtime.cognition_governance.inculcation",
            "activate", "--root", str(self.root), "--approve-sha256", digest(data),
            "--expected-previous", before.sha256], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.loader.load()
        self.assertEqual(after.version, "9.0")
        self.assertNotEqual(before.sha256, after.sha256)
        self.assertIsNot(before, after)

    def test_stale_previous_activation_is_rejected(self):
        f = self.loader.load()
        result = subprocess.run([sys.executable, "-B", "-m", "runtime.cognition_governance.inculcation",
            "activate", "--root", str(self.root), "--approve-sha256", f.sha256,
            "--expected-previous", "none"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_replacement_cannot_reuse_the_current_version(self):
        before = self.loader.load()
        path = self.root / SOURCE
        path.write_text(path.read_text(encoding="utf-8").replace("Your deployed name is Orbot", "Your deployed name remains Orbot"), encoding="utf-8")
        data = canonical(compile_foundation(self.root))
        (self.root / "inculcation.compiled.json").write_bytes(data)
        result = subprocess.run([sys.executable, "-B", "-m", "runtime.cognition_governance.inculcation",
            "activate", "--root", str(self.root), "--approve-sha256", digest(data),
            "--expected-previous", before.sha256], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("advance the version", result.stderr)

    def test_cognition_evaluation_waits_for_valid_foundation(self):
        from runtime.cognition_governance import service
        with patch.object(service.loader, "load", side_effect=FoundationError("Invalid")), \
             patch.object(service, "evaluate_core4") as evaluate:
            with self.assertRaises(FoundationError):
                service.evaluate(None, None)
        evaluate.assert_not_called()


def missing_section_case(index):
    def test(self):
        path = self.root / SOURCE
        text = path.read_text(encoding="utf-8")
        text = text.replace(f"## {index + 1}. {TITLES[index]}", f"### Removed subject {index + 1}")
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(FoundationError, "twelve ordered"):
            compile_foundation(self.root)
    return test


for index in range(12):
    setattr(FoundationTests, f"test_required_subject_{index + 1:02d}_cannot_be_omitted", missing_section_case(index))


class LifecycleTests(unittest.TestCase):
    def test_foundation_survives_session_purge_and_restarts_without_truth_promotion(self):
        from runtime.communication.memory import HostMemory
        with tempfile.TemporaryDirectory() as directory:
            f = FoundationLoader().load()
            memory = HostMemory(Path(directory))
            try:
                activation = memory.bind_professional_foundation(f)
                self.assertEqual(memory.bind_professional_foundation(f), activation)
                first = memory.start("harness")
                memory.set_objective(first, "Prepare a project explanation")
                memory.remember(first, {"user": "Temporary scratch note"})
                retained = memory.remember(first, {"user": "Project Blue Lantern"}, important=True,
                                           reason="Explicit harness retention")
                report = memory.end(first)
                self.assertEqual(report["pruned"], 1)
                self.assertNotIn(first, memory.sessions)
                second = memory.start("harness")
                self.assertIsNone(memory.working_context(second)["objective"])
                self.assertEqual(memory.items(second), [])
                self.assertEqual(memory.professional_foundation_status()["sha256"], f.sha256)
                atom = memory.aims.vault.get(retained["atom_id"])
                self.assertEqual(atom.status.value, "probation")
                self.assertEqual(atom.derived_from, [retained["entry_id"]])
                self.assertEqual(atom.metadata["authority_class"], "assertion")
                memory.end(second)
            finally:
                memory.db.close()
                memory.aims.close()
            restored = HostMemory(Path(directory))
            try:
                restored.bind_professional_foundation(FoundationLoader().load())
                self.assertEqual(restored.professional_foundation_status()["sha256"], f.sha256)
                self.assertEqual(restored.sessions, {})
            finally:
                restored.db.close()
                restored.aims.close()


class ConformanceTests(unittest.TestCase):
    def test_plain_response_without_tool_claim_is_allowed(self):
        self.assertEqual(validate_response({"text": "I can help plan the work.", "requested_tool": None,
                                            "tool_claims": []}), "I can help plan the work.")

    def test_model_tool_request_cannot_become_execution(self):
        with self.assertRaises(ConformanceError):
            validate_response({"text": "A request", "requested_tool": {"operation": "send"}, "tool_claims": []})

    def test_false_tool_narration_has_established_failure_label(self):
        with self.assertRaises(ConformanceError) as error:
            validate_response({"text": "I have sent your email.", "requested_tool": None, "tool_claims": []})
        self.assertEqual(error.exception.label, "FALSE_TOOL_NARRATION")

    def test_absent_event_cannot_verify_a_result(self):
        with self.assertRaises(ConformanceError):
            validate_tool_correspondence({"event_id": "invented"}, [])

    def test_matching_authorized_verified_event(self):
        event = {"event_id": "e1", "tool_id": "fixture-only", "operation": "read", "target": "fixture", "status": "verified",
                 "authorization_reference": "fixture-approval", "evidence_reference": "fixture-observation"}
        validate_tool_correspondence(event, [event])

    def test_wrong_target_is_rejected(self):
        event = {"event_id": "e1", "tool_id": "fixture-only", "operation": "read", "target": "a", "status": "verified"}
        with self.assertRaises(ConformanceError):
            validate_tool_correspondence({**event, "target": "b"}, [event])

    def test_dispatched_is_not_verified(self):
        event = {"event_id": "e1", "status": "executing"}
        with self.assertRaises(ConformanceError):
            validate_tool_correspondence(event, [event])

    def test_remote_contract_cannot_silently_inherit_native_assumptions(self):
        with patch.dict("os.environ", {"ORBOT_REMOTE_URL": "https://example.invalid/v1", "ORBOT_REMOTE_MODEL": "fixture"}):
            provider = RemoteChatProvider()
            with self.assertRaisesRegex(RuntimeError, "verified tokenizer"):
                provider.foundation_preflight()

    def test_invalid_model_output_gets_only_one_repair_and_is_withheld(self):
        provider = LlamaCppProvider()
        completion_calls = []
        def native(route, payload=None):
            if route == "/props":
                return {"default_generation_settings": {"n_ctx": 8192}}
            if route == "/apply-template":
                return {"prompt": json.dumps(payload["messages"])}
            if route == "/tokenize":
                return {"tokens": [1] * 7100}
            if route == "/completion":
                completion_calls.append(payload)
                return {"content": json.dumps({"text": "I sent the email.", "requested_tool": None, "tool_claims": []})}
            raise AssertionError(route)
        with patch.object(provider, "models", return_value=["fixture"]), \
             patch.object(provider, "_native_request", side_effect=native):
            with self.assertRaisesRegex(ValueError, "bounded deterministic"):
                provider.reply("Send this email")
        self.assertEqual(len(completion_calls), 2)

    def test_cold_shared_slot_still_gets_complete_foundation(self):
        provider = LlamaCppProvider()
        prefixes = []
        def native(route, payload=None):
            if route == "/props":
                return {"default_generation_settings": {"n_ctx": 8192}, "total_slots": 2}
            if route == "/apply-template":
                prefixes.append(payload["messages"][0]["content"])
                return {"prompt": json.dumps(payload["messages"])}
            if route == "/tokenize":
                return {"tokens": [1] * 7100}
            if route == "/completion":
                self.assertNotIn("id_slot", payload)
                return {"content": json.dumps({"text": "I can explain that.", "requested_tool": None, "tool_claims": []}),
                        "timings": {"cache_n": 0}, "truncated": False}
            raise AssertionError("Shared slots must not be erased or controlled")
        with patch.object(provider, "models", return_value=["fixture"]), \
             patch.object(provider, "_native_request", side_effect=native):
            provider.reply("Hello")
            provider.reply("Continue", [{"user": "Hello", "assistant": "I can explain that."}])
        self.assertEqual(prefixes, [FoundationLoader().load().prefix] * 2)


class HttpBoundaryTests(unittest.TestCase):
    def setUp(self):
        from runtime.communication import service
        from runtime.communication.memory import HostMemory
        from fastapi.testclient import TestClient
        self.service = service
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name))
        self.memory_patch = patch.object(service, "get_memory", return_value=self.memory)
        self.token_patch = patch.object(service, "dock_token", return_value="fixture-server-side-token")
        self.memory_patch.start()
        self.token_patch.start()
        self.client = TestClient(service.app)

    def tearDown(self):
        self.memory_patch.stop()
        self.token_patch.stop()
        self.memory.close_all()
        self.memory.db.close()
        self.memory.aims.close()
        self.temp.cleanup()

    def test_dock_status_requires_existing_server_credential(self):
        self.assertEqual(self.client.get("/inculcation/status").status_code, 401)
        result = self.client.get("/inculcation/status", headers={"Authorization": "Bearer fixture-server-side-token"})
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.json()["execution_authority"])

    def test_collection_api_cannot_write_professional_foundation(self):
        result = self.client.post("/memory/collections/inculcation", json={"payload": {}, "reason": "chat replacement"},
                                  headers={"Authorization": "Bearer fixture-server-side-token"})
        self.assertEqual(result.status_code, 404)

    def test_objective_is_session_context_not_professional_education(self):
        before = FoundationLoader().load()
        with patch.object(self.service.language, "reply", return_value="I can help plan it.") as reply:
            first = self.client.post("/conversation", json={"text": "Help plan it", "objective": "Plan Blue Lantern"}).json()
            self.client.post("/conversation", json={"text": "Continue", "session_id": first["session_id"]})
        self.assertEqual(reply.call_args.kwargs["turn_context"]["working_memory"]["objective"], "Plan Blue Lantern")
        self.client.post("/sessions/end", json={"session_id": first["session_id"]})
        next_session = self.client.post("/sessions", json={}).json()["session_id"]
        self.assertIsNone(self.memory.working_context(next_session)["objective"])
        self.assertEqual(before.sha256, FoundationLoader().load().sha256)

    def test_integrity_failure_prevents_articulation(self):
        with patch.object(self.service.loader, "load", side_effect=FoundationError("Tampered")), \
             patch.object(self.service.language, "reply") as reply:
            result = self.client.post("/conversation", json={"text": "hello"})
        self.assertEqual(result.status_code, 503)
        reply.assert_not_called()


if __name__ == "__main__":
    unittest.main()
