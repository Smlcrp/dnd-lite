"""Password hashing for local accounts. Pure stdlib -- no new dependency.

This is a local, single-player CLI tool, not a networked service; the goal
here is "don't store plaintext passwords," not defending against a
sophisticated attacker with access to the account files.
"""

import hashlib
import hmac
import os

_ITERATIONS = 200_000


def hash_password(password: str) -> tuple:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return hmac.compare_digest(digest.hex(), hash_hex)
