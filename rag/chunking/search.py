"""Vector search over chunks: MiniLM embeddings stored in sqlite-vec."""
import sqlite3

import sqlite_vec
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts):
    return MODEL.encode(texts, normalize_embeddings=True, show_progress_bar=False)


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
    q = sqlite_vec.serialize_float32(embed([query])[0])
    return db.execute(
        "SELECT v.rowid, v.distance, c.text FROM vec_chunks v JOIN chunks c ON c.id = v.rowid "
        "WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance",
        (q, k),
    ).fetchall()
