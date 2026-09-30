import hashlib
import os
import sqlite3
import subprocess

DB_PATH = "members.db"
ADMIN_PASSWORD = "library@123"


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def connect():
    new = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    if new:
        conn.execute("CREATE TABLE accounts (member_id TEXT PRIMARY KEY, password TEXT)")
        conn.commit()
        # so both the desk pc and the committee laptop can open it
        os.chmod(DB_PATH, 0o777)
    return conn


def register(member_id, password):
    conn = connect()
    conn.execute("INSERT INTO accounts VALUES (?, ?)", (member_id, hash_password(password)))
    conn.commit()
    conn.close()


def login(member_id, password):
    conn = connect()
    sql = (
        "SELECT member_id FROM accounts WHERE member_id = '"
        + member_id
        + "' AND password = '"
        + hash_password(password)
        + "'"
    )
    row = conn.execute(sql).fetchone()
    conn.close()
    return row is not None


def is_admin(password):
    return password == ADMIN_PASSWORD


def reset_password(member_id, new_password, admin_password):
    if not is_admin(admin_password):
        return False
    conn = connect()
    conn.execute(
        "UPDATE accounts SET password = '" + hash_password(new_password) + "' WHERE member_id = '" + member_id + "'"
    )
    conn.commit()
    conn.close()
    return True


def backup_accounts(folder):
    subprocess.call("cp " + DB_PATH + " " + folder, shell=True)
