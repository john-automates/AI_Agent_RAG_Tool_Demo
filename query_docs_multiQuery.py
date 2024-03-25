from langchain.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain import hub
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import os
from langchain.prompts import ChatPromptTemplate
from langchain.load import dumps, loads
from operator import itemgetter
import re
from dotenv import load_dotenv
import json

# Load the .env file
load_dotenv()

class SimpleQuerySystem:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        db_type = os.getenv("DB_TYPE")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        self.connection_string = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        self.setup()

    def setup(self):
        # Set up templates and embeddings
        self.multi_query_template = """You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions separated by newlines. Original question: {question}"""

        self.LLM_prompt = '''You are recognized as an expert in addressing questions on specialized topics. I am about to ask you a question that requires a detailed and informed response. Please adhere to the following guidelines in your reply:

Comprehensive Answers: Your response should thoroughly address the question, incorporating relevant details and interpretations based on the context provided.

Contextual Quotes: Whenever possible, include quotes from the provided context to support your answers and ALWAYS cite the source. Use markdown syntax for formatting quotes, emphasizing text, and organizing your answer for enhanced readability.

Markdown Formatting: Ensure your response is formatted using markdown to enhance readability and organization. This includes using > for block quotes, ** for bold text, * for italicized text, and properly formatting any links or references.

Answer Structure: Begin with a brief introduction, followed by the quoted evidence, and conclude with a summary or interpretation if necessary. Make sure your answer directly addresses the question, drawing from the specific context given.

Provided Context: {context}

Your Question: {question}'''

        self.prompt_perspectives = ChatPromptTemplate.from_template(self.multi_query_template)
        self.generate_queries = (
            self.prompt_perspectives
            | ChatOpenAI(temperature=0)
            | StrOutputParser()
            | (lambda x: x.split("\n"))
        )

        self.embeddings = OpenAIEmbeddings()
        self.store = PGVector(
            collection_name=self.collection_name,
            connection_string=self.connection_string,
            embedding_function=self.embeddings,
        )

    @staticmethod
    def get_unique_union(documents):
        # Function to get the unique union of documents
        flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
        unique_docs = list(set(flattened_docs))
        return [loads(doc) for doc in unique_docs]

    @staticmethod
    def format_docs(docs):
        # Format documents with page_content and include metadata if needed
        formatted_docs = []
        for doc in docs:
            formatted_doc = f"{doc.page_content}\n\nSource: {doc.metadata['source']}"
            formatted_docs.append(formatted_doc)
        return "\n\n".join(formatted_docs)




    def generate_answer(self, question):
        retriever = self.store.as_retriever(search_kwargs={"k": 3})
        retrieval_chain = self.generate_queries | retriever.map() | self.get_unique_union
        prompt = ChatPromptTemplate.from_template(self.LLM_prompt)
        llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: self.format_docs(x["context"])))
            | prompt
            | llm
            | StrOutputParser()
        )
        final_rag_chain = RunnableParallel(
            {"context": retrieval_chain, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)
        result = final_rag_chain.invoke({"question": question})
        report = f"Context: {result['context']}\n--------\n"
        report += f"Question: {result['question']['question']}\n--------\n"
        report += f"Answer: {result['answer']}\n--------\n"

        return report

# Assuming the SimpleQuerySystem class definition is in the same file or imported properly

def rag_ask(question, collection_name="cyber_security_handbook"):
    """
    A simple function to query the system with a user's question.

    Parameters:
    question (str): The question posed by the user.
    collection_name (str): The name of the collection to query against. Defaults to "cyber_security_handbook".

    Returns:
    The result of the query as processed by the SimpleQuerySystem.
    """
    system = SimpleQuerySystem(collection_name)
    result = system.generate_answer(question)
    return result

# Usage example:
if __name__ == "__main__":
    question = "Who is this handbook for?"
    report = rag_ask(question)
    print(report)

