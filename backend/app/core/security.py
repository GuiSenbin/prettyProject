"""核心安全机制：提供免编译、零外部依赖的加盐哈希密码算法。"""
import hashlib
import os


def get_password_hash(password: str) -> str:
    """生成加盐 PBKDF2 密码散列"""
    salt = os.urandom(16)
    # 用 sha256 迭代 100,000 次，生成加盐哈希
    db_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # 拼装成可拆分解析格式：pbkdf2_sha256$100000$salt_hex$hash_hex
    return f"pbkdf2_sha256$100000${salt.hex()}${db_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """核对明文密码与存储哈希值是否相符"""
    if not hashed_password or "$" not in hashed_password:
        return False
    try:
        algorithm, iterations, salt_hex, hash_hex = hashed_password.split('$')
        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
        return expected_hash.hex() == hash_hex
    except Exception:
        return False
