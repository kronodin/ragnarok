import unittest, json
from src.redteam.temp-mail.engine import TempMailEngine

class TestTempMailEngine(unittest.TestCase):
    def test_alias_generation(self):
        alias = TempMailEngine.generate_alias()
        self.assertTrue(alias.startswith("ragnarok_"))
        self.assertEqual(len(alias.split("_")[1]), 12)

    def test_provider_validation(self):
        with self.assertRaises(ValueError):
            TempMailEngine("unknown_provider")

    def test_summary_without_account(self):
        engine = TempMailEngine()
        summary = engine.summary()
        self.assertIn("No account", summary)

if __name__ == "__main__":
    unittest.main()
