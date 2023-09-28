#Used create sql query engine and generate response
import os
import openai
from dotenv import load_dotenv,find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain

load_dotenv(find_dotenv())

api_key=os.environ['OPENAI_API_KEY']
username = os.environ['USER_NAME']
password = os.environ['PASSWORD']
host = os.environ['HOST']
port = os.environ['PORT']
database = os.environ['DATABASE']

openai.api_key=api_key

db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}", )
llm = ChatOpenAI(temperature=0,model_name='gpt-3.5-turbo')


def chat_completion(question):
    chain = create_sql_query_chain(llm=llm, db=db)
    input = {"question":question}

    response = chain.invoke(input)
    print("sql_query:",response)
    query_result = db.run(response)
    print("fetched_data:",query_result)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Answer: {query_result}"}
    ]

    text_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    print("text_response:",text_response)

    generated_text = text_response['choices'][0]['message']['content']

    return generated_text

if __name__ == '__main__':
    question = input("Enter the question:")
    chat_completion(question)
