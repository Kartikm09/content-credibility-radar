import unittest

from credibility_radar.radar import analyze_content


class CredibilityRadarTests(unittest.TestCase):
    def test_unsupported_claims_lower_score(self):
        report = analyze_content(
            {
                "transcript": "This shocking secret changes everything.",
                "claims": [{"id": "c1", "text": "Unsupported claim"}],
                "sources": [],
            }
        )
        self.assertEqual(report.status, "high-risk")
        self.assertIn("Unsupported claim", report.unsupported_claims)
        self.assertIn("shocking", report.emotional_language_flags)

    def test_supported_claims_can_be_publishable(self):
        report = analyze_content(
            {
                "transcript": "Neutral explanation with sources.",
                "claims": [{"id": "c1", "text": "Official claim"}],
                "sources": [
                    {"type": "official", "supports": ["c1"]},
                    {"type": "research", "supports": ["c1"]},
                    {"type": "reputable_media", "supports": ["c1"]},
                ],
            }
        )
        self.assertGreaterEqual(report.score, 80)
        self.assertEqual(report.status, "publishable")


if __name__ == "__main__":
    unittest.main()
