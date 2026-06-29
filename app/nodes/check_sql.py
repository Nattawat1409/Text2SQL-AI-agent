from sqlalchemy import text
from models import All_State
from tools.db import engine
from typing import Literal                  # import litreal -> define path
from langgraph.types import Command         # commander -> take action

MAX_RETRIES = 3  # fixed regenerate attempts at check_sql for mex retry round = 3


def check_sql(state: All_State) -> Command[Literal["execute_sql", "generate_sql", "generate_answer"]]:
    """
    Validates generate_sql by asking Postgres to plan it (EXPLAIN) without
    executing it - catches syntax/schema errors safely, no data is touched.

    Routes directly via Command(goto=...): valid SQL -> execute_sql, invalid
    with retries left -> generate_sql to self-correct, invalid at MAX_RETRIES
    -> generate_answer (gives up, no separate fix_sql/return_error node).
    """
    sql_query = state.get("generate_sql")
    retry_count = state.get("retry_count", 0) # define it as 0

    try:
        with engine.connect() as conn:
            conn.execute(text(f"EXPLAIN {sql_query}")) # check connection before fetchAll
        is_valid = True
    except Exception as e:
        is_valid = False
        error_message = str(e)

    if is_valid:
        return Command(
            goto="execute_sql",
            update={
                "check_sql_syntax": True, # explain is passed
                "retry_count": 0
            }
        )

    # if not valid
    retry_count += 1
    next_node = "generate_answer" if retry_count >= MAX_RETRIES else "generate_sql" # looping -> generate_SQL untill retry_count >= escape the loop -> generate answer

    return Command(
        goto=next_node,                         # (2 possible nodes -> generate_answer or generate_sql) depend on retry_count
        update={
            "check_sql_syntax": False,          # not pass for explain
            "retry_count": retry_count,         # retry round left  -> generate_sql
            "sql_error": error_message,         # fed back to -> generate_sql
            "return_error": retry_count >= MAX_RETRIES  # graph stops looping when round >= 3 times is TRUE
        }
    )


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    # inject input directly to test check_sql node in isolation
    fake_state = {
        "generate_sql": "SELECT COUNT(customernumber) FROM customers;",
        "retry_count": 0
    }
    isolated_output = check_sql(fake_state)

    print(f" routing decision : {isolated_output}")
    print(f" check_sql_syntax : {isolated_output.update['check_sql_syntax']}")
    print(f" retry_count      : {isolated_output.update['retry_count']}\n")


