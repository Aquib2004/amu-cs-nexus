# Tests for the embedder.

from app.embedder import HashEmbedder, ProviderEmbedder


def test_hash_embedder_shape() -> None:
    vector = HashEmbedder(384).embed("exam schedule october")
    assert len(vector) == 384


def test_hash_embedder_deterministic() -> None:
    embedder = HashEmbedder(384)
    assert embedder.embed("hello world") == embedder.embed("hello world")


def test_embed_many() -> None:
    out = HashEmbedder(8).embed_many(["a", "b c"])
    assert len(out) == 2
    assert all(len(v) == 8 for v in out)


def test_provider_not_wired() -> None:
    try:
        ProviderEmbedder().embed("x")
        raise AssertionError("ProviderEmbedder should be unimplemented")
    except NotImplementedError:
        pass
