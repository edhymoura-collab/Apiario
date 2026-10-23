import base64
import hashlib
import hmac
import secrets

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_KEY_LENGTH = 32


def is_password_hash(value: str) -> bool:
    return value.startswith("$scrypt$")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_KEY_LENGTH,
    )
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    key_text = base64.urlsafe_b64encode(derived_key).decode("ascii").rstrip("=")
    return f"$scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt_text}${key_text}"


def verify_password(password: str, stored_value: str) -> bool:
    if not is_password_hash(stored_value):
        return hmac.compare_digest(password.encode("utf-8"), stored_value.encode("utf-8"))

    try:
        _, algorithm, n, r, p, salt_text, key_text = stored_value.split("$")
        if algorithm != "scrypt":
            return False
        salt = _decode_base64(salt_text)
        expected_key = _decode_base64(key_text)
        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected_key),
        )
    except (ValueError, TypeError, OverflowError):
        return False

    return hmac.compare_digest(actual_key, expected_key)


def _decode_base64(value: str) -> bytes:
    padded_value = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded_value)
