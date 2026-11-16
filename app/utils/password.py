"""密码哈希，与若依 PwdUtil（bcrypt）兼容。"""

import bcrypt


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
