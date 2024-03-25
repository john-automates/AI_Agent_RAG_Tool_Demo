#!/usr/bin/env python

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import PyPDFLoader
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

# Get the absolute path to the directory
abs_path = os.path.abspath("Cybersecurity Handbook")

loader = DirectoryLoader(abs_path, glob="**/*.txt")
documents = loader.load()
#print("Loaded", len(documents), "documents")
# Use CharacterTextSplitter instead of TextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=0)
#print("Splitting documents...", text_splitter)
docs = text_splitter.split_documents(documents)
print("Split", len(docs), "documents")

# Prompt the user for confirmation
confirmation = input("Are you sure you want to proceed? (y/n): ")
if confirmation.lower() != "y":
    exit()

embeddings = OpenAIEmbeddings()



COLLECTION_NAME = "cyber_security_handbook"

db_type = os.getenv("DB_TYPE")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

CONNECTION_STRING = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# create the store
db = PGVector.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    pre_delete_collection=False,
)


query = "Who is this book for?"
docs_with_score = db.similarity_search_with_score(query)
for doc, score in docs_with_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)