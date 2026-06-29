import os 
from dotenv import load_dotenv
import sqlalchemy # import python for SQL lib 
from sqlalchemy import create_engine  # get the SQL syntax to DB #

load_dotenv() # load env files 

# fill the database url #
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"options": "-c statement_timeout=5000"},  # กัน query ค้างเกิน 5 วิ
)

print(sqlalchemy.__version__)

# sql_query = state.get("generate_sql")


# test_connection = conn.execute((f"EXPLAIN {sql_query}"))
# print(test_connection)