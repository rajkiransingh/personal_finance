"""Idempotent migration + seed for multi-user access control.

Run from the repo root:

    .venv/bin/python scripts/migrate_auth_schema.py

It adds the auth columns to `users`, creates the household/preference tables,
adds an owner column to liabilities, and seeds the three accounts:

    Rajkiran Singh  (user, household view)   rajkiran@homeservermanagement101
    Ashwini Singh   (user, personal view)    ashwini@homeservermanagement101
    Financer        (admin, no data view)    financer@homeservermanagement101

Existing data is preserved. The default password is read from BOOTSTRAP_PASSWORD
or generated and printed once; users are forced to change it on first login.

The script is safe to re-run: existing columns/tables/rows are left alone.
"""

import os
import secrets
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def migration_url() -> str:
    explicit = os.getenv("MIGRATION_DATABASE_URL")
    if explicit:
        return explicit
    url = os.getenv("DATABASE_URL", "")
    if url:
        try:
            host = url.split("@")[-1].split("/")[0].split(":")[0]
            socket.gethostbyname(host)
            return url
        except (OSError, IndexError):
            pass
    # Running on the host: reach the published MySQL port.
    user = os.getenv("MYSQL_USER", "user")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "personal_finance_db")
    return f"mysql+pymysql://{user}:{password}@localhost:3399/{database}"


COLUMNS = {
    "users": {
        "email": "VARCHAR(255) NULL UNIQUE",
        "password_hash": "VARCHAR(255) NULL",
        "role": "VARCHAR(20) NOT NULL DEFAULT 'user'",
        "is_active": "BOOLEAN NOT NULL DEFAULT 1",
        "auth_provider": "VARCHAR(20) NOT NULL DEFAULT 'local'",
        "external_sub": "VARCHAR(255) NULL UNIQUE",
        "must_change_password": "BOOLEAN NOT NULL DEFAULT 0",
        "last_login_at": "DATETIME NULL",
    },
    "liabilities": {
        "user_id": "INT NULL",
    },
}


def main() -> int:
    engine = create_engine(migration_url())
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        # Fail fast instead of hanging behind a metadata lock.
        conn.execute(text("SET SESSION lock_wait_timeout = 10"))

        for table, columns in COLUMNS.items():
            if table not in existing_tables:
                print(f"! table {table} missing — run the base schema first")
                return 1
            present = {c["name"] for c in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in present:
                    conn.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
                    )
                    print(f"+ {table}.{name}")

        if "households" not in existing_tables:
            conn.execute(
                text(
                    """CREATE TABLE households (
                        household_id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        shared_domains TEXT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NULL
                    )"""
                )
            )
            print("+ households")

        if "household_members" not in existing_tables:
            conn.execute(
                text(
                    """CREATE TABLE household_members (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        household_id INT NOT NULL,
                        user_id INT NOT NULL,
                        scope_mode VARCHAR(20) NOT NULL DEFAULT 'self',
                        FOREIGN KEY (household_id) REFERENCES households(household_id),
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )"""
                )
            )
            print("+ household_members")

        if "user_preferences" not in existing_tables:
            conn.execute(
                text(
                    """CREATE TABLE user_preferences (
                        user_id INT PRIMARY KEY,
                        theme VARCHAR(20) NULL,
                        filters TEXT NULL,
                        strategies TEXT NULL,
                        page_size INT NULL,
                        updated_at DATETIME NULL,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )"""
                )
            )
            print("+ user_preferences")

        # Existing loans predate ownership and belong to the original account.
        conn.execute(
            text("UPDATE liabilities SET user_id = 1 WHERE user_id IS NULL")
        )

        rows = conn.execute(
            text("SELECT user_id, name FROM users ORDER BY user_id")
        ).fetchall()
        users = {int(row[0]): row[1] for row in rows}

        seeds = [
            (1, "Rajkiran Singh", "rajkiran@homeservermanagement101", "user"),
            (2, "Ashwini Singh", "ashwini@homeservermanagement101", "user"),
        ]
        for user_id, name, email, role in seeds:
            # Only seed once. On later runs the admin may have renamed the
            # account, changed its role or set a different email in the console.
            conn.execute(
                text(
                    "UPDATE users SET name = :name, email = :email, role = :role, "
                    "is_active = 1, auth_provider = 'local' "
                    "WHERE user_id = :id AND email IS NULL"
                ),
                {"name": name, "email": email, "role": role, "id": user_id},
            )

        existing_admin = conn.execute(
            text(
                "SELECT user_id FROM users WHERE lower(name) = 'financer' "
                "OR email = 'financer@homeservermanagement101' LIMIT 1"
            )
        ).fetchone()
        if existing_admin:
            admin_id = int(existing_admin[0])
        else:
            result = conn.execute(
                text(
                    "INSERT INTO users (name, email, role, is_active, auth_provider) "
                    "VALUES ('Financer', :email, 'admin', 1, 'local')"
                ),
                {"email": "financer@homeservermanagement101"},
            )
            admin_id = int(result.lastrowid)
            print(f"+ admin user Financer (id {admin_id})")

        # Household: user 1 may switch to the combined view, user 2 may not.
        households = conn.execute(text("SELECT household_id FROM households")).fetchall()
        if households:
            household_id = int(households[0][0])
        else:
            result = conn.execute(
                text(
                    "INSERT INTO households (name, shared_domains, is_active, created_at) "
                    "VALUES ('Household', 'all', 1, :now)"
                ),
                {"now": datetime.now(timezone.utc)},
            )
            household_id = int(result.lastrowid)
            print(f"+ household {household_id}")

        for user_id, scope_mode in ((1, "household"), (2, "self")):
            if user_id not in users:
                continue
            found = conn.execute(
                text(
                    "SELECT id FROM household_members WHERE household_id = :h "
                    "AND user_id = :u"
                ),
                {"h": household_id, "u": user_id},
            ).fetchone()
            if found:
                # Keep the admin's chosen scope_mode; do not reset it on restart.
                pass
            else:
                conn.execute(
                    text(
                        "INSERT INTO household_members (household_id, user_id, scope_mode) "
                        "VALUES (:h, :u, :mode)"
                    ),
                    {"h": household_id, "u": user_id, "mode": scope_mode},
                )

        # One shared bootstrap password, printed once, forced reset on login.
        password = os.getenv("BOOTSTRAP_PASSWORD") or secrets.token_urlsafe(12)
        digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM users WHERE password_hash IS NULL "
                "OR password_hash = ''"
            )
        ).fetchone()
        if result[0]:
            conn.execute(
                text(
                    "UPDATE users SET password_hash = :hash, "
                    "must_change_password = 1 WHERE password_hash IS NULL "
                    "OR password_hash = ''"
                ),
                {"hash": digest},
            )
            print("\nTemporary password (shown once): " + password)
            print("Users must change it on first login.\n")

    print("Auth schema migration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
