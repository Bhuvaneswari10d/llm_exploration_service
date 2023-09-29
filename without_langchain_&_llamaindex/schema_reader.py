from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import NoSuchModuleError
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())

# Define a function to connect to the database and retrieve schema
def get_database_schema(db_type, host, port, user, password, database):
    try:
        # Create a SQLAlchemy connection string
        sqlalchemy_connection_string = f"{db_type}://{user}:{password}@{host}:{port}/{database}"

        # Create a SQLAlchemy engine
        engine = create_engine(sqlalchemy_connection_string)

        # Create a MetaData object
        metadata = MetaData()


        # Reflect the database schema
        metadata.reflect(bind=engine)
        # print(metadata)
        formatted_output = ""
        for table in metadata.tables.values():
            formatted_output += f"Column names for table {table.name}\n"
            for column in table.columns:
                formatted_output += f"  {column.name}\n"
        # print(formatted_output)
        return formatted_output

    except NoSuchModuleError:
        print(f"Database type '{db_type}' is not supported.")
    except Exception as e:
        print(f"Error: {e}")
