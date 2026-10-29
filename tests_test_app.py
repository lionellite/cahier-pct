import os
import unittest
from unittest.mock import Mock, patch

import app as pct


class RetrievalTests(unittest.TestCase):
    def test_official_corpus_has_32_chunks(self):
        self.assertEqual(len(pct.CORPUS), 32)

    def test_retrieval_returns_relevant_sections(self):
        hits = pct.retrieve("critères évaluation explication phénomène")
        self.assertTrue(hits)
        self.assertLessEqual(len(hits), 5)
        self.assertTrue(any("competence" in h["section"] or "orientations" in h["section"] for h in hits))

    def test_irrelevant_query_has_no_result(self):
        self.assertEqual(pct.retrieve("zzzxxyyqqq"), [])


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = pct.app.test_client()
        self.key = patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
        self.key.start()
        self.addCleanup(self.key.stop)

    def test_health(self):
        result = self.client.get("/api/health")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["corpus_chunks"], 32)

    def test_reject_invalid_mode(self):
        result = self.client.post("/api/generate", json={"mode": "other", "query": "test"})
        self.assertEqual(result.status_code, 400)

    def test_reject_oversize_query(self):
        result = self.client.post("/api/generate", json={"mode": "question", "query": "x" * 1201})
        self.assertEqual(result.status_code, 400)

    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 503)

    @patch("app.requests.post")
    def test_success_passes_only_retrieved_context(self, post):
        post.return_value = Mock(status_code=200, json=lambda: {"content": [{"type": "text", "text": "Réponse sourcée."}]})
        post.return_value.raise_for_status.return_value = None
        result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["answer"], "Réponse sourcée.")
        self.assertGreater(len(result.json["sources"]), 0)
        sent = post.call_args.kwargs["json"]["messages"][0]["content"]
        self.assertIn("EXTRAITS DU PROGRAMME OFFICIEL", sent)
        self.assertNotIn("orientations_generales", sent[:80])

    def test_unknown_query_returns_no_grounded_answer(self):
        result = self.client.post("/api/generate", json={"mode": "question", "query": "zzzxxyyqqq"})
        self.assertEqual(result.status_code, 422)


if __name__ == "__main__":
    unittest.main()
