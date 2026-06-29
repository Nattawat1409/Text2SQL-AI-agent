from typing import Annotated
from typing_extensions import TypedDict


class All_State(TypedDict):
    question : str  #__start__#
    classify_question: str 
    is_sql_relate : bool    # is sql-related?  yes or no
    get_schema : bool
    db_schema : str         # actual table/column text passed to generate_sql
    generate_sql : str
    check_sql_syntax : bool     # valid or issue #
    retry_count : int       # how many regenerate attempts so far (max enforced by MAX_RETRIES in check_sql.py)
    execute_sql : str
    execution : bool
    sql_error : str         # latest error from check_sql/execute_sql, fed back into generate_sql to self-correct
    generate_answer :str    # in case question relate with Database #
    normal_response : str   # in case question is normal question 
    return_error : bool
    answer:str      #__end__##
