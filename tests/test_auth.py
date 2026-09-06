import auth


def test_verify_password_round_trip():
    salt_hex, hash_hex = auth.hash_password("correct horse battery staple")
    assert auth.verify_password("correct horse battery staple", salt_hex, hash_hex) is True


def test_verify_password_rejects_wrong_password():
    salt_hex, hash_hex = auth.hash_password("correct horse battery staple")
    assert auth.verify_password("wrong password", salt_hex, hash_hex) is False


def test_hash_password_uses_unique_salt_per_call():
    salt1, hash1 = auth.hash_password("same password")
    salt2, hash2 = auth.hash_password("same password")
    assert salt1 != salt2
    assert hash1 != hash2


def test_verify_password_rejects_empty_against_real_password():
    salt_hex, hash_hex = auth.hash_password("test")
    assert auth.verify_password("", salt_hex, hash_hex) is False
