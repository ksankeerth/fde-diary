"""Vector search over chunks: embeddings stored in sqlite-vec. EMBED_MODEL picks the model (default minilm)."""
import os
import sqlite3
from functools import lru_cache

import sqlite_vec

# key: (model name, prefix for queries; chunks get none)
MODELS = {
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", ""),
    "bge-small": ("BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: "),
}
MODEL_KEY = os.environ.get("EMBED_MODEL", "minilm")
NAME, QUERY_PREFIX = MODELS[MODEL_KEY]  # both models give 384-dimensional vectors


@lru_cache(maxsize=None)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(NAME)


def __getattr__(name):  # `from search import MODEL` loads the model on first use
    if name == "MODEL":
        return _model()
    raise AttributeError(name)


def embed(texts, query=False):
    prefix = QUERY_PREFIX if query else ""
    return _model().encode([prefix + t for t in texts], normalize_embeddings=True, show_progress_bar=False)


def build_index(chunks):
    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)  # raises AttributeError if this Python's sqlite3 was built without it
    sqlite_vec.load(db)
    db.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT)")
    db.execute("CREATE VIRTUAL TABLE vec_chunks USING vec0(embedding float[384])")
    for i, (text, vec) in enumerate(zip(chunks, embed(chunks))):
        db.execute("INSERT INTO chunks VALUES (?, ?)", (i, text))
        db.execute("INSERT INTO vec_chunks(rowid, embedding) VALUES (?, ?)", (i, sqlite_vec.serialize_float32(vec)))
    return db


def search(db, query, k=3):
    """Top-k (chunk id, distance, text), nearest first."""
    q = sqlite_vec.serialize_float32(embed([query], query=True)[0])
    return db.execute(
        "SELECT v.rowid, v.distance, c.text FROM vec_chunks v JOIN chunks c ON c.id = v.rowid "
        "WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance",
        (q, k),
    ).fetchall()
