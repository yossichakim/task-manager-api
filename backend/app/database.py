"""Provide SQLite connections and initialize the application's schema."""

import sqlite3

from flask import current_app


def get_database_connection():
    """Return a configured SQLite connection for the current application.

    The database path comes from ``current_app.config["DATABASE"]``. Returned
    connections produce ``sqlite3.Row`` values and enforce foreign keys.
    Callers must commit writes and close the connection.
    """
    database_name = current_app.config["DATABASE"]

    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """Create required tables and migrate legacy task schemas if necessary.

    Initialization is idempotent, adds ``tasks.user_id`` to legacy databases,
    and commits and closes its own connection.
    """
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'general',
            status TEXT NOT NULL DEFAULT 'pending',
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS revoked_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jti TEXT NOT NULL UNIQUE,
        revoked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
)

    # Preserve databases created before tasks were associated with users.
    task_columns = cursor.execute(
        "PRAGMA table_info(tasks)"
    ).fetchall()

    column_names = [
        column["name"] for column in task_columns
    ]

    if "user_id" not in column_names:
        cursor.execute(
            """
            ALTER TABLE tasks
            ADD COLUMN user_id INTEGER
            """
        )

    connection.commit()
    connection.close()
