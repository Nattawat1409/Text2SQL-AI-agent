from sqlalchemy import text

from models import All_State
from tools.db import engine



def execute_sql(state: All_State) -> dict:
    """
    Runs the validated SQL (after check_sql passed) against classicmodels and
    formats the rows into text for generate_answer to use.

    check_sql already caught anything regeneratable (bad syntax, unknown
    table/column). A failure here is an infra issue (timeout, dropped
    connection) that regenerating the SQL can't fix, so this does not loop
    back to generate_sql - generate_answer reports it honestly instead.
    """
    sql_query = state['generate_sql']

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
    except Exception as e:
        return {
            "execution": False,
            "sql_error": str(e)
        }

    if not rows:
        formatted = "(no rows returned)"
    else:
        formatted = "\n".join(
            ", ".join(f"{col}={value}" for col, value in zip(columns, row))
            for row in rows
        )

    return {
        "execute_sql": formatted,
        "execution": True
    }


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    from .get_schema import get_schema
    from .generate_sql import generate_sql
    from .check_sql import check_sql

    test_question = "Who is our top 2 spending customer?"

    state = {"question": test_question} # fill question
    state.update(get_schema(state))     # get_schema
    state.update(generate_sql(state))   # generate_SQL 
    state.update(check_sql(state))      # check_SQL
    state.update(execute_sql(state))    # execute_SQL

    output = execute_sql(state)
    print("\n--- LangGraph Node Output ---")
    print(f"generate_sql     : {state['generate_sql']}")
    print(f"check_sql_syntax : {state.get('check_sql_syntax')}")
    print(f"execution        : {output['execution']}")
    print(f"execute_sql      :\n{output['execute_sql']}\n")
