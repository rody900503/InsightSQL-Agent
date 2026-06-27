import os
from dotenv import load_dotenv
from google import genai
from database import get_schema

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

print("API Key exists:", API_KEY is not None)

print("API Key prefix:", API_KEY[:10] if API_KEY else "None")

client = genai.Client(api_key=API_KEY)

def generate_sql(user_question):
    schema = get_schema()

    prompt = f"""
You are a professional SQL data analyst agent.

Database schema:
{schema}

User question:
{user_question}

Rules:
1. Generate only one safe SQLite SELECT query.
2. Do not explain the SQL.
3. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or REPLACE.
4. If the user asks for revenue or sales, calculate revenue as:
   SUM(quantity * unit_price) AS total_revenue
5. If the user asks for the highest, best, top, or most, include the relevant metric in SELECT.
6. If grouping by a category such as region, product_category, product_name, or customer_name, include both the category and the metric in SELECT.
7. Use clear aliases such as total_revenue, total_quantity, average_order_value.
8. Order results by the relevant metric in descending order when looking for top or highest values.

Return only the SQLite SQL query.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text.strip()
    sql = sql.replace("```sql", "")
    sql = sql.replace("```sqlite", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    if sql.lower().startswith("ite"):
        sql = sql[3:].strip()

    return sql


def generate_business_insight(question, sql, columns, rows):
    result_text = f"Columns: {columns}\nRows: {rows}"

    prompt = f"""
You are a business data analyst.

User question:
{question}

SQL query:
{sql}

Query result:
{result_text}

Explain the result in simple English.
Provide:
1. Key finding
2. Business insight
3. Recommended action
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def validate_sql(sql):
    sql_lower = sql.lower().strip()

    blocked_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "replace"
    ]

    if not sql_lower.startswith("select"):
        return False, "Only SELECT queries are allowed."

    for keyword in blocked_keywords:
        if keyword in sql_lower:
            return False, f"Blocked unsafe SQL keyword: {keyword}"

    return True, "SQL is safe to execute."