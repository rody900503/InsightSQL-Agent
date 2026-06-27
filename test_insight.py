from agent import generate_sql, generate_business_insight
from database import execute_sql

question = "What are the top 5 products by revenue?"

sql = generate_sql(question)
columns, rows = execute_sql(sql)

insight = generate_business_insight(question, sql, columns, rows)

print("Question:")
print(question)

print("\nGenerated SQL:")
print(sql)

print("\nQuery Result:")
print(columns)
for row in rows:
    print(row)

print("\nBusiness Insight:")
print(insight)
