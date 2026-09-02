import uuid

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_argon2_password_hashing() -> None:
    encoded = hash_password("correct horse battery staple")
    assert encoded.startswith("$argon2id$")
    assert verify_password(encoded, "correct horse battery staple")
    assert not verify_password(encoded, "incorrect")
    assert not verify_password("malformed", "anything")


def test_access_token_is_signed_and_typed() -> None:
    user_id = uuid.uuid4()
    settings = Settings(jwt_secret="test-secret-that-is-at-least-32-bytes")
    payload = decode_access_token(create_access_token(user_id, "ADMIN", settings), settings)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_access_token_rejects_wrong_secret() -> None:
    token = create_access_token(
        uuid.uuid4(), "VIEWER", Settings(jwt_secret="first-secret-that-is-long-enough")
    )
    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(token, Settings(jwt_secret="second-secret-that-is-long-enough"))
