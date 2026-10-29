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

    def test_health_shows_unconfigured_without_leaking_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            result = self.client.get("/api/health")
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.json["api_configured"])
        self.assertEqual(result.json["provider"], "gemini")
        self.assertEqual(result.json["model"], "gemini-3.8-flash")
        self.assertNotIn("key", result.json)

    def test_health_selects_gemini_if_both_providers_configured(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "g-secret", "ANTHROPIC_API_KEY": "a-secret"}):
            result = self.client.get("/api/health")
        self.assertEqual(result.json["provider"], "gemini")
        self.assertNotIn("g-secret", result.get_data(as_text=True))

    def test_reject_invalid_mode(self):
        result = self.client.post("/api/generate", json={"mode": "other", "query": "test"})
        self.assertEqual(result.status_code, 400)

    def test_reject_oversize_query(self):
        result = self.client.post("/api/generate", json={"mode": "question", "query": "x" * 1201})
        self.assertEqual(result.status_code, 400)

    def test_missing_api_key_explains_gemini_setup(self):
        with patch.dict(os.environ, {}, clear=True):
            result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 503)
        self.assertIn("GEMINI_API_KEY", result.json["error"])

    @patch("app.requests.post")
    def test_gemini_success_uses_server_key_and_returns_sources(self, post):
        post.return_value = Mock(status_code=200, json=lambda: {"candidates": [{"content": {"parts": [{"text": "Réponse Gemini sourcée."}]}}]})
        post.return_value.raise_for_status.return_value = None
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-secret"}, clear=True):
            result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["answer"], "Réponse Gemini sourcée.")
        self.assertEqual(result.json["provider"], "Gemini 3.8 Flash")
        self.assertGreater(len(result.json["sources"]), 0)
        self.assertNotIn("test-secret", result.get_data(as_text=True))
        self.assertNotIn("test-secret", post.call_args.args[0])
        self.assertEqual(post.call_args.kwargs["headers"]["x-goog-api-key"], "test-secret")
        self.assertIn("EXTRAITS DU PROGRAMME OFFICIEL", post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"])

    @patch("app.requests.post")
    def test_anthropic_fallback_still_works(self, post):
        post.return_value = Mock(status_code=200, json=lambda: {"content": [{"type": "text", "text": "Réponse Claude."}]})
        post.return_value.raise_for_status.return_value = None
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-secret"}, clear=True):
            result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["provider"], "Claude")

    @patch("app.requests.post")
    def test_rate_limit_is_explained(self, post):
        response = Mock(status_code=429)
        post.return_value.raise_for_status.side_effect = pct.requests.HTTPError(response=response)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-secret"}, clear=True):
            result = self.client.post("/api/generate", json={"mode": "question", "query": "compétence disciplinaire"})
        self.assertEqual(result.status_code, 429)
        self.assertIn("quota gratuit", result.json["error"])

    def test_frontend_does_not_contain_corpus_or_secret(self):
        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Gemini 3.8 Flash", result.data)
        self.assertNotIn(b"const CORPUS", result.data)
        self.assertNotIn(b"test-secret", result.data)

    def test_unknown_query_returns_no_grounded_answer(self):
        result = self.client.post("/api/generate", json={"mode": "question", "query": "zzzxxyyqqq"})
        self.assertEqual(result.status_code, 422)


if __name__ == "__main__":
    unittest.main()
