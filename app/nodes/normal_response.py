import os
from models import All_State
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

__all__ = ["normal_response"]

load_dotenv()

llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    base_url=os.environ["LITELLM_URL"],
    api_key=os.environ["API_KEY"]
)

class Format_normal_response(BaseModel):
    normal_res: str = Field(description="answer with concise and provide assistant to normal question")

format_normal_llm = llm.with_structured_output(Format_normal_response) # define rule format to llm


def normal_response(state: All_State) -> dict:
    """
    Handles questions classify_question routed away from SQL - both genuine
    small talk and SQL-sounding questions that don't match this database's
    schema. Uses classify_question's reason as context so an out-of-schema
    question gets answered clearly instead of the LLM re-guessing from scratch.
    """
    user_question = state.get("question")
    classification_reason = state.get("classify_question")

    system_prompt = (
        "You are a helpful assistant for a text-to-SQL system over the 'classicmodels' database. "
        "The user's question does not require querying that database. Answer naturally and "
        "concisely (1-2 sentences). If the classification reason below explains that the question "
        "asks about something this database doesn't contain, tell the user that clearly and "
        "mention what the database does cover instead of just repeating the reason verbatim."
    )

    user_content = f"Question: {user_question}"
    if classification_reason:
        user_content += f"\n\nClassification reason: {classification_reason}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    normal_resp = format_normal_llm.invoke(messages)

    return {"normal_response": normal_resp.normal_res}


# <-- TEST STANDALONE NODE --> #

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    from .classify import classify_question

    print("--- genuine small talk ---")
    state = {"question": "hello, who are you?"}
    state.update(classify_question(state))
    output = normal_response(state)
    print(f"classify_question reason: {state['classify_question']}")
    print(f"normal_response        : {output['normal_response']}\n")

    print("--- out-of-schema question ---")
    state2 = {"question": "give the number of menu in KFC"}
    state2.update(classify_question(state2))
    output2 = normal_response(state2)
    print(f"classify_question reason: {state2['classify_question']}")
    print(f"normal_response        : {output2['normal_response']}\n")

