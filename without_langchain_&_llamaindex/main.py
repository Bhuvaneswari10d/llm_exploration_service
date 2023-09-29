import os
import openai
from dotenv import load_dotenv,find_dotenv
from sqlalchemy import create_engine, text
from schema_reader import get_database_schema
import time

load_dotenv(find_dotenv())

api_key=os.environ['OPENAI_API_KEY']
user = os.environ['USER_NAME']
password = os.environ['PASSWORD']
host = os.environ['HOST']
port = os.environ['PORT']
database = os.environ['DATABASE']
db_type = os.environ['DB_TYPE']

openai.api_key=api_key

sqlalchemy_connection_string=f"{db_type}://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(sqlalchemy_connection_string)
conn=engine.connect()


def chat_completion(question):
    schema_reader = get_database_schema(db_type, host, port, user, password, database)
    # print(schema_reader)
    top_k=10
    PROMPT_SUFFIX = f"""Only use the following tables:
    {schema_reader}

    Question: {question}"""

    _DEFAULT_TEMPLATE = f"""Given an input question, first create a syntactically correct dialect query to run. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

    Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    
    Additionally, all searches will be case-insensitive, ensuring that values are found regardless of case. Use the `ILIKE` operator for case-insensitive searches in your SQL queries

    Use the following format:

    Question: Question here
    SQLQuery: SQL Query to run
        use_distinct: True

    """
    prompt= _DEFAULT_TEMPLATE+PROMPT_SUFFIX
    template = prompt.format(input=question)
    messages=[
        {"role": "system", "content": f"You are a helpful assistant to generate sql query by following instructions given {template}."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Answer: return sql query"}
    ]
    query_gen_start_time=time.time()
    sql_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    query_gen_end_time=time.time()
    print("="*150)
    print("Time taken to generate query:",query_gen_end_time-query_gen_start_time)
    # print(sql_response)
    query=sql_response['choices'][0]['message']['content']
    print("=" * 150)
    print("query",query)
    query_res=query.replace('SQLQuery: ','').strip()
    fetch_result_start_time = time.time()
    query_result=conn.execute(text(f"{query_res}"))
    fetch_result_end_time = time.time()
    print("=" * 150)
    print("Time taken to fetch the data from db",fetch_result_end_time-fetch_result_start_time)
    result=[]
    if query_result:
        fetched_data=query_result.fetchall() or query_result.scalar()
        result.append(fetched_data)
    else:
        print(query_result)
    print("=" * 150)
    print("fetched_data:",result)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Answer: {result}, also give with oncological information with generated text"}
    ]
    gen_text_start_time=time.time()
    text_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    gen_text_end_time = time.time()
    print("=" * 150)
    print("Time taken to generate text",gen_text_end_time-gen_text_start_time)
    # print("text_response:",text_response)

    generated_text = text_response['choices'][0]['message']['content']
    print("=" * 150)
    print("generated_text:",generated_text)

    return generated_text

if __name__ == '__main__':
    # question = input("Enter the question:")
    # question="List the drugs with target as TROP2"
    # question = "How many trials are currently open"
    question="How many drugs are there in phase 2"
    chat_completion(question)
