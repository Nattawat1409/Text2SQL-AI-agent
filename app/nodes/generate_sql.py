import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from models import All_State # import all nodes from all states
from pydantic import BaseModel, Field

load_dotenv() # load ENV files #


llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    base_url=os.environ["LITELLM_URL"],
    api_key=os.environ["API_KEY"]
)


class GenerateSQLResult(BaseModel):
    sql_syntax: str = Field(description="A single valid PostgreSQL SELECT statement that answers the user's question")


structured_llm = llm.with_structured_output(GenerateSQLResult) # define rule format to llm


def generate_sql(state: All_State) -> dict:
    """
    Generates a single PostgreSQL SELECT statement for the user's question,
    using db_schema (set by get_schema) as the schema/rules context.

    If looping back after a check_sql/execute_sql failure, state["sql_error"]
    is set - in that case this fixes the previous attempt instead of writing
    a fresh query from scratch (no separate fix_sql node needed).
    """
    db_schema = state.get("db_schema")
    user_question = state.get("question")
    previous_sql = state.get("generate_sql")
    sql_error = state.get("sql_error")

    if not db_schema:
        raise ValueError("generate_sql requires db_schema in state - run get_schema first")

    if sql_error:
        user_content = (
            f"{user_question}\n\n"
            f"Your previous attempt produced this SQL:\n{previous_sql}\n\n"
            f"It failed with this error:\n{sql_error}\n\n"
            "Fix the SQL so it correctly answers the question."
        )
    else:
        user_content = user_question

    messages = [
        {"role": "system", "content": db_schema},
        {"role": "user", "content": user_content}
    ]

    gen_sql_syntax = structured_llm.invoke(messages)

    return {
        "generate_sql": gen_sql_syntax.sql_syntax # return only generate sql
    }


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    from .get_schema import get_schema

    test_question = "how many customer within table of customer"

    # mirror the real graph: get_schema runs before generate_sql
    schema_output = get_schema({"question": test_question})

    mock_state = {
        "question": test_question,
        "get_schema": schema_output["get_schema"],
        "db_schema": schema_output["db_schema"],
    }
    
    output = generate_sql(mock_state)
    print("\n--- LangGraph Node Output ---")
    print(f"generate_sql :\n{output['generate_sql']}\n")
    print("\n-----------------------------")
    # eval: actually run the generated SQL against the real database
    # from sqlalchemy import text
    # from tools.db import engine

    # try:
    #     with engine.connect() as conn:
    #         rows = conn.execute(text(output["generate_sql"])).fetchall()
    #     print(f"--- Executed against classicmodels: {len(rows)} row(s) ---")
    #     for row in rows:
    #         print(row)
    # except Exception as e:
    #     print(f"--- SQL failed to execute: {e} ---")


# WORKING #