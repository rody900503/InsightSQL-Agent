from agent import generate_sql
from database import execute_sql

question = "What are the top 5 products by revenue?"

sql = generate_sql(question)

print(sql)

columns, rows = execute_sql(sql)

print()

print(columns)

print()

for row in rows:
    print(row)