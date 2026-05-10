"""
Unit tests for app.services.embedding — sentence-transformer embedding generation.

NOTE: These tests load the actual SentenceTransformer model (all-MiniLM-L6-v2)
      on first run, which may take a few seconds. Subsequent runs use the cached model.
"""
import pytest


class TestGenerateEmbedding:
    def test_returns_list_of_floats(self):
        from app.services.embedding import generate_embedding
        result = generate_embedding("Python FastAPI Developer")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    def test_consistent_dimension(self):
        from app.services.embedding import generate_embedding
        r1 = generate_embedding("Hello world")
        r2 = generate_embedding("Another completely different text")
        assert len(r1) == len(r2)
        # all-MiniLM-L6-v2 outputs 384-dimensional vectors
        assert len(r1) == 384

    def test_deterministic_output(self):
        from app.services.embedding import generate_embedding
        r1 = generate_embedding("Deterministic test input")
        r2 = generate_embedding("Deterministic test input")
        assert r1 == r2

    def test_different_inputs_produce_different_embeddings(self):
        from app.services.embedding import generate_embedding
        r1 = generate_embedding("Python backend developer")
        r2 = generate_embedding("French pastry chef")
        assert r1 != r2

    def test_empty_string_does_not_crash(self):
        from app.services.embedding import generate_embedding
        result = generate_embedding("")
        assert isinstance(result, list)
        assert len(result) == 384


class TestGetModel:
    def test_singleton_model(self):
        from app.services.embedding import get_model
        m1 = get_model()
        m2 = get_model()
        assert m1 is m2
