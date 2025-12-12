from __future__ import annotations
import os
import bcrypt

SEED_DIR = "seed"
USERS_TXT = os.path.join(SEED_DIR, "users.txt")

def make_hash(plain: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_hash(plain: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), stored_hash.encode("utf-8"))

def ensure_seed_folder() -> None:
    os.makedirs(SEED_DIR, exist_ok=True)

def append_user_to_file(handle: str, password: str, access_level: str) -> None:
    """
    File persistence format:
    handle,pass_hash,access_level
    """
    ensure_seed_folder()
    handle = handle.strip()
    access_level = access_level.strip()
    if not handle or not password or not access_level:
        raise ValueError("handle/password/access_level required")

    pass_hash = make_hash(password)

    # prevent duplicate handle lines (simple scan)
    if os.path.exists(USERS_TXT):
        with open(USERS_TXT, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(",")]
                if len(parts) >= 1 and parts[0] == handle:
                    return

    with open(USERS_TXT, "a", encoding="utf-8") as f:
        f.write(f"{handle},{pass_hash},{access_level}\n")
