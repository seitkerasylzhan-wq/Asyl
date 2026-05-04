from pathlib import Path
import psycopg2

from config import load_config, load_admin_config

BASE_DIR = Path(__file__).resolve().parent


def execute_sql_file(cursor, filename):
    sql_path = BASE_DIR / filename
    if not sql_path.exists():
        print(f"SQL file not found: {sql_path}")
        return

    with sql_path.open("r", encoding="utf-8") as f:
        cursor.execute(f.read())


def create_database_if_not_exists():
    db_name = load_config()["database"]
    admin_cfg = load_admin_config()

    conn = psycopg2.connect(**admin_cfg)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Database '{db_name}' created.")
            else:
                print(f"Database '{db_name}' already exists.")
    finally:
        conn.close()


def setup_database():
    create_database_if_not_exists()

    conn = None
    try:
        conn = psycopg2.connect(**load_config())

        with conn, conn.cursor() as cur:
            execute_sql_file(cur, "schema.sql")
            execute_sql_file(cur, "procedures.sql")

        print("Database fully initialized (schema + procedures).")

    except Exception as error:
        print(f"Database setup error: {error}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    setup_database()
