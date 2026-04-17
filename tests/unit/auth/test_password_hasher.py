from src.auth.infra.password_hasher import BcryptPasswordHasher


def test_hash_and_verify_success():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("mysecretpassword")
    assert hasher.verify("mysecretpassword", hashed) is True


def test_verify_wrong_password_returns_false():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("correctpassword")
    assert hasher.verify("wrongpassword", hashed) is False


def test_hash_produces_different_results():
    hasher = BcryptPasswordHasher()
    hash1 = hasher.hash("samepassword")
    hash2 = hasher.hash("samepassword")
    assert hash1 != hash2
