from langchain.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from langchain.prompts import ChatPromptTemplate
from langchain.load import dumps, loads
from operator import itemgetter
from langchain_core.runnables import RunnableParallel
import re
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


CONNECTION_STRING = "postgresql://postgres:<password>@<ip>:<port>"


multi_query_template = """You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions separated by newlines. Original question: {question}"""

LLM_prompt = '''You are recognized as an expert in addressing questions on specialized topics. I am about to ask you a question that requires a detailed and informed response. Please adhere to the following guidelines in your reply:

Comprehensive Answers: Your response should thoroughly address the question, incorporating relevant details and interpretations based on the context provided.

Contextual Quotes: Whenever possible, include quotes from the provided context to support your answers and ALWAYS cite the source. Use markdown syntax for formatting quotes, emphasizing text, and organizing your answer for enhanced readability.

Markdown Formatting: Ensure your response is formatted using markdown to enhance readability and organization. This includes using > for block quotes, ** for bold text, * for italicized text, and properly formatting any links or references.

Answer Structure: Begin with a brief introduction, followed by the quoted evidence, and conclude with a summary or interpretation if necessary. Make sure your answer directly addresses the question, drawing from the specific context given.

Provided Context: {context}

Your Question: {question}'''


def get_unique_union(documents: list[list]):
    """
    Get the unique union of retrieved documents.

    This function takes a list of lists of documents, flattens it into a single list, and removes any duplicate documents. It uses the json.dumps function to convert each document (which is a dictionary) into a string, because dictionaries cannot be directly compared for equality in Python. It then uses the set data structure to remove duplicates, and finally converts each document back into a dictionary using json.loads.

    Parameters:
    documents (list[list]): A list of lists of documents. Each document is a dictionary.

    Returns:
    list: A list of unique documents. Each document is a dictionary.
    """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]

def format_docs(docs):
    """
    Format the documents including their source formatted appropriately based on the path structure.
    
    This function assumes that the source follows the <author>/<book>/<chapter> format. If a source does not have at least three parts when split by '/', it is considered an "Unknown source".
    
    Parameters:
    docs (list): A list of documents. Each document is a dictionary that includes the document content and metadata.

    Returns:
    str: A string that includes the formatted document content and source for each document in the input list. Each document is separated by two newline characters.
    """
    formatted_docs = []
    for doc in docs:
        source = doc.metadata['source']
        parts = source.split('/')
        if len(parts) >= 3:
            author = parts[-3]
            book = parts[-2]
            chapter_with_extension = parts[-1]
            chapter = chapter_with_extension.split('.')[0]  # Remove the file extension
            formatted_source = f"Author: {author}\n Book: {book}\n Chapter: {chapter}"
        else:
            formatted_source = "Unknown source"
        
        # Formatting the document content with the formatted source
        formatted_doc = f"{doc.page_content}\n\nSource: {formatted_source}"
        formatted_docs.append(formatted_doc)
    
    return "\n\n" + "\n\n".join(formatted_docs)


# Multi Query: Different Perspectives

prompt_perspectives = ChatPromptTemplate.from_template(multi_query_template)

generate_queries = (
    prompt_perspectives 
    | ChatOpenAI(temperature=0) 
    | StrOutputParser() 
    | (lambda x: x.split("\n"))
)


def generate_answer(question, generate_queries, get_unique_union, templates, collection_name):
    # Create embeddings and store inside the function
    embeddings = OpenAIEmbeddings()

    store = PGVector(
        collection_name=collection_name,
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
    )
    # gives back the top 3 documents -> You can change the number of documents to retrieve by changing the value of k
    retriever = store.as_retriever(search_kwargs={"k": 3})
    
    # Retrieve
    retrieval_chain = generate_queries | retriever.map() | get_unique_union

    # RAG
    prompt = ChatPromptTemplate.from_template(LLM_prompt)
    llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")

    # Create a chain that generates an answer from the documents
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    # Create a parallel chain that retrieves the documents and generates an answer
    final_rag_chain = RunnableParallel(
        {"context": retrieval_chain, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    # Invoke the chain with a question
    result = final_rag_chain.invoke({"question": question})

    return result


def main():
    question = "<question>"
    result = generate_answer(question, generate_queries, get_unique_union, LLM_prompt, "<collection_name>")
    print(result)