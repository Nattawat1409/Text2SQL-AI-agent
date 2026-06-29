import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from models import All_State

load_dotenv()

llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    base_url=os.environ["LITELLM_URL"],
    api_key=os.environ["API_KEY"]
)

# define format of generate answer + SQL query
class Format_generate_answer(BaseModel):
    answer: str = Field(description="A clear, friendly natural-language answer to the user's question")


structured_answer_llm = llm.with_structured_output(Format_generate_answer)  # define response format of llm


def generate_answer(state: All_State) -> dict:
    """
    Turns the query result (or a failed attempt) into a natural-language
    answer. Reads state["execution"] to know which case it's in.
    """
    user_question = state.get("question")

    if state.get("execution") is True:
        system_prompt = (
            "You are a helpful assistant that turns a database query result into a "
            "natural, friendly answer for a non-technical user. Use only the data given - "
            "never make anything up. Answer in 1-2 sentences."
        )
        user_content = f"Question: {user_question}\n\nQuery result:\n{state.get('execute_sql')}"
    else:
        system_prompt = (
            "You are a helpful assistant. The database query for the user's question failed "
            "after multiple attempts. Apologize briefly and explain in plain language that you "
            "could not retrieve this information right now. Do not show raw error messages or "
            "technical details. Keep it to 1-2 sentences."
        )
        user_content = f"Question: {user_question}\n\nLast error: {state.get('sql_error')}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content} # depend on execution pass or fail
    ]

    response_with_query = structured_answer_llm.invoke(messages)

    return {
        "answer": response_with_query.answer
    }


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    from .get_schema import get_schema
    from .generate_sql import generate_sql
    from .check_sql import check_sql
    from .execute_sql import execute_sql


    test_question = "Who is our top-spending customer?"
    state = {"question": test_question}
    state.update(get_schema(state))
    state.update(generate_sql(state))
    state.update(check_sql(state))
    state.update(execute_sql(state))

    output = generate_answer(state)
    
    # Actual case for retrieve
    print("\n--- LangGraph Node Output ---")
    print(f"generate SQL : {state.get('generate_sql')}")
    print(f"execution : {state.get('execution')}")
    print(f"answer    :\n{output['answer']}\n")

    # Failed case for retrieve 
    failed_state = {**state, "execution": False, "sql_error": 'relation "chicken" does not exist'}
    failed_output = generate_answer(failed_state)
    print(f"answer (failure case):\n{failed_output['answer']}\n")
