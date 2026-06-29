# import os
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain_openai import ChatOpenAI
# from nodes import answer

# load_dotenv()

# llm = ChatOpenAI(
#     model="google/gemini-2.5-flash",
#     base_url=os.environ["LITELLM_URL"],
#     api_key=os.environ["API_KEY"],
# )


# class ClassifyResult(BaseModel):
#     is_sql_related: bool = Field(description="True if the question requires querying the classicmodels database")
#     reason: str = Field(description="One short sentence explaining the classification")


# structured_llm = llm.with_structured_output(ClassifyResult)

# if __name__ == "__main__":
#     test_question = "Who is our top-spending customer?"

#     result = structured_llm.invoke(test_question)

#     print(f"\ntype(result) : {type(result)}")
#     print(f"result        : {result}")
#     print(f"is_sql_related: {result.is_sql_related}")
#     print(f"reason        : {result.reason}\n")
