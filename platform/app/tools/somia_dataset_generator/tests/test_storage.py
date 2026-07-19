from somia_dataset_generator.storage import sha256_bytes

def test_sha256_is_stable():
    assert sha256_bytes(b"somia") == sha256_bytes(b"somia")
