from src.infrastructure.security.password import (
    hash_password,
    verify_password
)


def test_password_is_hashed():
    password = "hello123"

    password_hash = hash_password(password)

    assert password_hash != password


def test_correct_password_verifies():
    password = "hello123"

    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_wrong_password_does_not_verify():
    password = "hello123"
    wrong_password = "wrongpassword"

    password_hash = hash_password(password)

    assert verify_password(wrong_password, password_hash) is False


def test_same_password_produces_different_hashes():
    password = "hello123"

    password_hash_1 = hash_password(password)
    password_hash_2 = hash_password(password)

    assert password_hash_1 != password_hash_2

