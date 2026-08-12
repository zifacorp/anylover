from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from anylover.backup import BackupError, create_encrypted_backup, restore_encrypted_backup
from anylover.config import Settings
from anylover.service import AnyLoverService


class BackupTest(unittest.TestCase):
    def test_encrypted_backup_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            source_settings = Settings(data_dir=root / "source", db_path=root / "source.sqlite3")
            source = AnyLoverService(source_settings)
            source.ensure_default_companion()
            source.remember(
                content="周日喜欢去散步",
                kind="preference",
                consent_basis="explicit",
                source_surface="test",
            )

            bundle = create_encrypted_backup(
                source_settings.db_path,
                root / "backup.albackup",
                passphrase="correct horse battery staple",
            )
            self.assertNotIn("周日喜欢去散步".encode(), bundle.read_bytes())

            restored_path = restore_encrypted_backup(
                bundle,
                root / "restored.sqlite3",
                passphrase="correct horse battery staple",
            )
            restored = AnyLoverService(
                Settings(data_dir=root / "restored", db_path=restored_path)
            )
            self.assertEqual(restored.list_memories()[0].content, "周日喜欢去散步")

            with self.assertRaises(BackupError):
                restore_encrypted_backup(
                    bundle,
                    root / "wrong.sqlite3",
                    passphrase="this passphrase is wrong",
                )


if __name__ == "__main__":
    unittest.main()
