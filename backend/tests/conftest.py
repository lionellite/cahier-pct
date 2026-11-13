import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app import create_app  # noqa: E402
from app.config import Config  # noqa: E402
from app.services.corpus import clear_corpus_cache  # noqa: E402


class TestConfig(Config):
    TESTING = True
    LLM_MODE = "mock"
    ANTHROPIC_API_KEY = ""
    CORPUS_PATH = Config.CORPUS_PATH


@pytest.fixture(scope="session", autouse=True)
def _clear_cache():
    clear_corpus_cache()
    yield
    clear_corpus_cache()


@pytest.fixture()
def app():
    return create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()
