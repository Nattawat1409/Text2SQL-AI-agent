import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# FIX: Point exactly to the state module file
from models.states.state import All_State
from nodes.classify import classify_question
from nodes.is_sql_relate import is_sql_relate
from nodes.get_schema import get_schema
from nodes.generate_sql import generate_sql
from nodes.check_sql import check_sql
from nodes.execute_sql import execute_sql
from nodes.generate_answer import generate_answer
from nodes.normal_response import normal_response
# Load environment variables
load_dotenv()

## -- Set LLM Agent -- ##
llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    base_url=os.environ["LITELLM_URL"],
    api_key=os.environ["API_KEY"]
)

# 3. Initialize the StateGraph with your schema
workflow = StateGraph(All_State)

# 4. Add nodes that are implemented
workflow.add_node("classify_question", classify_question)
workflow.add_node("is_sql_relate", is_sql_relate)
workflow.add_node("get_schema", get_schema)
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("check_sql", check_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("normal_response", normal_response)

# 5. Connect edge matching the Mermaid flowchart (docs/text2sql_langgraph.md)

# start -> classify_question
workflow.add_edge(START, "classify_question")

# classify_question -> is_sql_relate -> get_schema else normal_response
# is_sql_relate routes via Command(goto= 2 routes get_schema || normal_response ) 
workflow.add_edge("classify_question", "is_sql_relate")

workflow.add_edge("get_schema", "generate_sql")
workflow.add_edge("generate_sql", "check_sql")

# check_sql routes via Command(goto=...) itself now too - no
# add_conditional_edges needed, same as is_sql_relate above

# make decision base on real data from database
workflow.add_edge("execute_sql", "generate_answer")

workflow.add_edge("normal_response", END)
workflow.add_edge("generate_answer", END)

app = workflow.compile()



#-------------------------------#
# <-- TEST GRAPH TEXT-2-SQL --> #
#-------------------------------#

# --- THIS BLOCK RUNS WHEN YOU EXECUTE THE FILE DIRECTLY ---
if __name__ == "__main__":
    question_user = input("input your question : ")

    result = app.invoke({"question": question_user})

    print("\n" + "=" * 60)
    print(f"Question : {question_user}")
    print("-" * 60)

    if result.get("is_sql_relate"):
        print(f"Route        : SQL")
        print(f"Generated SQL: {result.get('generate_sql')}")
        print(f"check_sql_syntax: {result.get('check_sql_syntax')}  (retries used: {result.get('retry_count', 0)})")
        print(f"execution    : {result.get('execution')}")
        print("-" * 60)
        print(f"Answer       : {result.get('answer')}")
    else:
        print(f"Route        : chat / normal_response")
        print(f"Reason       : {result.get('classify_question')}")
        print("-" * 60)
        print(f"Answer       : {result.get('normal_response')}")

    print("=" * 60 + "\n")


    # =================================================================== #
    # Create IMAGE : graph structure image (always update to current graph)
    # node/edge wiring above
    # =================================================================== #
    png = app.get_graph().draw_mermaid_png()
    with open("docs/graph_structure.png", "wb") as f:
        f.write(png)
    print("graph structure image updated at docs/graph_structure.png")
