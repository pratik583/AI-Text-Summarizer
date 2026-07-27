import re

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Splits on sentence-ending punctuation followed by whitespace + a capital
# letter/digit/quote. Simple and dependency-free (no NLTK downloads needed).
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'])')


def split_sentences(text: str) -> list[str]:
    """Break raw text into a list of cleaned sentences."""
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def summarize(text: str, num_sentences: int = 3) -> dict:
    """
    Extractive summarization using TF-IDF + cosine similarity + TextRank
    (PageRank over a sentence-similarity graph). Fully local, no API calls,
    no large model downloads.

    Returns a dict with the summary, original sentence count, and stats.
    """
    sentences = split_sentences(text)
    original_count = len(sentences)

    if original_count == 0:
        return {
            "summary": "",
            "original_sentences": 0,
            "summary_sentences": 0,
            "original_words": 0,
            "summary_words": 0,
        }

    # Nothing meaningful to trim -- just return the original text.
    if original_count <= num_sentences:
        summary = " ".join(sentences)
        return {
            "summary": summary,
            "original_sentences": original_count,
            "summary_sentences": original_count,
            "original_words": len(text.split()),
            "summary_words": len(summary.split()),
        }

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sim_matrix = cosine_similarity(tfidf_matrix)
        np.fill_diagonal(sim_matrix, 0)

        graph = nx.from_numpy_array(sim_matrix)
        scores = nx.pagerank(graph, max_iter=200)

        ranked_idx = sorted(
            range(len(sentences)), key=lambda i: scores[i], reverse=True
        )[:num_sentences]
        ranked_idx.sort()  # restore original reading order
    except ValueError:
        # Falls back to the first N sentences if TF-IDF ends up empty
        # (e.g. very short / all-stopword input).
        ranked_idx = list(range(min(num_sentences, original_count)))

    summary_sentences = [sentences[i] for i in ranked_idx]
    summary = " ".join(summary_sentences)

    return {
        "summary": summary,
        "original_sentences": original_count,
        "summary_sentences": len(summary_sentences),
        "original_words": len(text.split()),
        "summary_words": len(summary.split()),
    }
