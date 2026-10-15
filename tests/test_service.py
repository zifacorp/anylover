from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from anylover.config import Settings
from anylover.service import AnyLoverService, MemoryPolicyError


class ServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.settings = Settings(data_dir=root, db_path=root / "anylover.sqlite3")
        self.service = AnyLoverService(self.settings)
        self.service.ensure_default_companion()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_default_companion_is_sharp_but_not_degrading(self) -> None:
        companion = self.service.get_companion()
        self.assertIn("sharp-tongued", companion.persona)
        self.assertIn("distinct point of view", companion.persona)
        self.assertIn("offer a useful alternative", companion.communication_style)
        self.assertIn("never weaponize private memories", companion.safety_contract)
        self.assertIn("Stop teasing", companion.safety_contract)

    def test_remember_recall_deduplicate_and_forget(self) -> None:
        preference, deduplicated = self.service.remember(
            content="我喜欢直接但温柔的沟通",
            kind="preference",
            consent_basis="explicit",
            source_surface="test",
            importance=0.8,
        )
        self.assertFalse(deduplicated)
        same, deduplicated = self.service.remember(
            content="我喜欢直接但温柔的沟通",
            kind="preference",
            consent_basis="explicit",
            source_surface="claude-code",
            importance=0.9,
        )
        self.assertTrue(deduplicated)
        self.assertEqual(same.id, preference.id)
        self.assertEqual(same.importance, 0.9)

        boundary, _ = self.service.remember(
            content="不要用内疚或吃醋的方式挽留我",
            kind="boundary",
            consent_basis="explicit",
            source_surface="test",
            importance=1.0,
        )
        context = self.service.build_context(query="怎么和我交流", limit=5)
        self.assertIn("我喜欢直接但温柔的沟通", context.prompt)
        self.assertIn("不要用内疚或吃醋的方式挽留我", context.prompt)
        self.assertEqual(context.memories[0].id, boundary.id)

        with self.assertRaises(MemoryPolicyError):
            self.service.forget(preference.id, confirmation="yes", actor="test")
        self.assertTrue(
            self.service.forget(preference.id, confirmation="DELETE", actor="test")
        )
        active_ids = {memory.id for memory in self.service.list_memories()}
        self.assertNotIn(preference.id, active_ids)

    def test_sensitive_and_secret_policy(self) -> None:
        with self.assertRaises(MemoryPolicyError):
            self.service.remember(
                content="这是一个 API token: abc",
                sensitivity="secret",
                consent_basis="explicit",
                source_surface="test",
            )
        with self.assertRaises(MemoryPolicyError):
            self.service.remember(
                content="这是需要谨慎处理的健康信息",
                sensitivity="sensitive",
                consent_basis="explicit",
                source_surface="test",
            )
        with self.assertRaises(MemoryPolicyError):
            self.service.remember(
                content="用户不喜欢某种称呼",
                kind="boundary",
                consent_basis="inferred",
                source_surface="test",
            )

    def test_supersedes_old_fact(self) -> None:
        old, _ = self.service.remember(
            content="用户住在上海",
            consent_basis="explicit",
            source_surface="test",
        )
        new, _ = self.service.remember(
            content="用户现在住在杭州",
            consent_basis="explicit",
            source_surface="test",
            supersedes_id=old.id,
        )
        self.assertEqual(new.supersedes_id, old.id)
        active_ids = {memory.id for memory in self.service.list_memories()}
        self.assertEqual(active_ids, {new.id})

    def test_unicode_script_retrieval(self) -> None:
        samples = (
            ("Пользователь любит тихие вечера", "тихие вечера"),
            ("المستخدم يحب الشاي بالنعناع", "الشاي بالنعناع"),
            ("उपयोगकर्ता को शांत संगीत पसंद है", "शांत संगीत"),
            ("Ο χρήστης προτιμά ήσυχα βράδια", "ήσυχα βράδια"),
        )
        for content, query in samples:
            memory, _ = self.service.remember(
                content=content,
                kind="preference",
                consent_basis="explicit",
                source_surface="test",
            )
            context = self.service.build_context(query=query, limit=1)
            self.assertEqual(context.memories[0].id, memory.id)


if __name__ == "__main__":
    unittest.main()
