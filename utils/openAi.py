import os
import textwrap
from openai import OpenAI

def call_openai_api(ioc_report, prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)

    # Convert ai_prompt to a string and concatenate it with ioc_report
    content = prompt + "\n" + ioc_report

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": content}],
    )

    # Extract the content and CompletionUsage
    response_content = response.choices[0].message.content
    response_usage = response.usage

    # Format the content
    formatted_content = textwrap.fill(response_content, width=80)

    # Format the usage
    formatted_usage = f"```\nCompletion Tokens: {response_usage.completion_tokens}\n" \
                      f"Prompt Tokens: {response_usage.prompt_tokens}\n" \
                      f"Total Tokens: {response_usage.total_tokens}\n```"

    return formatted_content, formatted_usage