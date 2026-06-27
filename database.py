import sqlite3
import pandas as pd

DB_PATH = "sales.db"

def get_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = ""

    for table in tables:
        table_name = table[0]

        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        schema += f"\nTable: {table_name}\n"

        for col in columns:
            schema += f"- {col[1]} ({col[2]})\n"

    conn.close()

    return schema


def run_sql(query):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(sql)

    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    conn.close()

    return columns, rows