import streamlit as st
import pandas as pd

from agent import generate_sql, generate_business_insight, validate_sql
from database import execute_sql, get_schema

st.set_page_config(page_title="InsightSQL Agent", layout="wide")

st.title("InsightSQL Agent")
st.write(
    "Ask a business question in natural language. "
    "The agent will generate SQL, let you review it, validate it, run it, "
    "visualize the result, and explain the business meaning."
)

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# Sidebar
with st.sidebar:
    st.header("Database Schema")
    st.code(get_schema())

    st.header("Sample Questions")
    st.markdown("""
- What are the top 5 products by revenue?
- Which region generated the highest revenue?
- What is the total revenue by product category?
- Which customers purchased the most items?
- What is the average order value by region?
""")

    st.header("Analysis History")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history, start=1):
            st.markdown(f"**{i}. {item['question']}**")
            st.caption(f"Rows returned: {item['rows']}")
    else:
        st.write("No history yet.")

# Main input
question = st.text_input(
    "Ask a business question:",
    "What are the top 5 products by revenue?"
)

# Generate SQL
if st.button("Generate SQL"):
    with st.spinner("Generating SQL..."):
        st.session_state.generated_sql = generate_sql(question)
        st.session_state.current_question = question

# SQL editor and analysis
if st.session_state.generated_sql:
    st.subheader("Generated SQL")

    edited_sql = st.text_area(
        "You can review or edit the SQL before execution:",
        st.session_state.generated_sql,
        height=220
    )

    if st.button("Run Analysis"):
        is_safe, safety_message = validate_sql(edited_sql)

        if not is_safe:
            st.error(safety_message)
            st.stop()

        st.success(safety_message)

        with st.spinner("Running SQL and generating business insight..."):
            columns, rows = execute_sql(edited_sql)
            df = pd.DataFrame(rows, columns=columns)

            insight = generate_business_insight(
                st.session_state.current_question,
                edited_sql,
                columns,
                rows
            )

            st.session_state.history.append({
                "question": st.session_state.current_question,
                "sql": edited_sql,
                "rows": len(df)
            })

        st.subheader("Query Result")
        st.dataframe(df, use_container_width=True)

        st.subheader("KPI Summary")

        col1, col2, col3 = st.columns(3)

        row_count = len(df)
        col_count = len(df.columns)
        numeric_columns = df.select_dtypes(include="number").columns.tolist()

        with col1:
            st.metric("Rows Returned", row_count)

        with col2:
            st.metric("Columns Returned", col_count)

        with col3:
            if numeric_columns:
                total_value = df[numeric_columns[0]].sum()
                st.metric(f"Total {numeric_columns[0]}", f"{total_value:,.2f}")
            else:
                st.metric("Numeric Columns", 0)

        if not df.empty:
            st.subheader("Auto Chart")
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            text_cols = df.select_dtypes(include="object").columns.tolist()
            if len(text_cols) >= 1 and len(numeric_cols) >= 1:
                chart_df = df.set_index(text_cols[0])[numeric_cols[0]]
                st.bar_chart(chart_df)

            elif len(numeric_cols) >= 2:
                st.line_chart(df[numeric_cols])

            else:
                st.info("No suitable chart available for this query.")

        st.subheader("Business Insight")
        st.write(insight)

        st.subheader("Suggested Follow-up Questions")
        st.markdown("""
- Which region contributed the most revenue?
- Which product category performed best?
- Which customer purchased the most items?
- What is the average order value by region?
""")

        st.subheader("Download Result")

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="insightsql_result.csv",
            mime="text/csv"
        )