
from app.services.generators import _page_range, _level
from app.services.corpus import CorpusSet, get_corpus
from app.config import Config


def test_page_range_compression():
    assert _page_range(list(range(41, 78))) == "41-77"
    assert _page_range([1, 2, 3, 9]) == "1-3, 9"
    assert _page_range([5]) == "5"
    assert _page_range([]) == "n/c"


def test_level_deduced_from_retrieved_extract():
    corpus = get_corpus(Config.CORPUS_PATH)
    hits = corpus.search("la pollution de lair", top_k=3)
    extracts = [e for e, _ in hits]
    assert _level(corpus, None, extracts) == "6e"
    assert _level(corpus, "3e", extracts) == "3e"
