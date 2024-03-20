from openai import OpenAI
import json

# Import your functions
from generate_ioc_report import generate_ioc_report
from query_docs_multiQuery import rag_ask

client = OpenAI()

def load_tools():
    with open('tools.json', 'r') as file:
        return json.load(file)

def run_conversation(question):
    messages = [{"role": "user", "content": question}]
    tools = load_tools()["tools"]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "generate_ioc_report": generate_ioc_report,
            "rag_ask": rag_ask,
        }
        # Note: We're printing the assistant's message before executing the functions.
        print("Assistant's message:", response_message.content)

        # Execute and print the function responses directly.
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            if function_name in available_functions:
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                # Directly print the function response here.
                function_response = function_to_call(**function_args)
                print("Function response:", function_response)
    else:
        # If there are no tool calls, just print the assistant's response.
        print("Assistant's message:", response_message.content)

# Terminal interaction starts here
if __name__ == "__main__":
    while True:
        question = input("Ask a question (type 'exit' to quit): ").strip()
        if question.lower() in ['exit', 'quit']:
            print("Exiting...")
            break
        run_conversation(question)
