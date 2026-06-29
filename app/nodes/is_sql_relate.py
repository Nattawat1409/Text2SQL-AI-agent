from typing import Literal

from langgraph.types import Command

from models import All_State

__all__ = ["is_sql_relate"]


def is_sql_relate(state: All_State) -> Command[Literal["normal_response", "get_schema"]]:
    """
    Reads the boolean set by classify_question and routes the graph directly
    via Command(goto=...) - no separate router function / add_conditional_edges
    needed for this decision, the node itself decides where execution goes next.
    """
    question_type = state.get("is_sql_relate")

    if question_type is True:
        return Command(goto="get_schema")

    # else case
    return Command(goto="normal_response")


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    # print("--- isolated: both routing outcomes ---")
    # print(f"is_sql_relate=True  -> {is_sql_relate({'is_sql_relate': True})}") # refer from state.py 
    # print(f"is_sql_relate=False -> {is_sql_relate({'is_sql_relate': False})}\n")

    print("--- chained with the real classify_question node ---")
    from .classify import classify_question

    test_question = "How many customers are there?"
    
    state = {"question": test_question}
    state.update(classify_question(state))  # sets state["is_sql_relate"] for real

    print(f"is_sql_relate (from classifier): {state['is_sql_relate']}")
    print(f"routing decision               : {is_sql_relate(state)}\n")


