# AI Agent RAG Tool Demo

Welcome to the AI Agent RAG Tool Demo! This document will guide you through the process of setting up and running this project. We highly recommend using the Windows Subsystem for Linux (WSL) or a Unix-based system to ensure compatibility and smooth operation.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Git
- Python (version 3.8 or later)
- PostgreSQL

If you're using Windows, we recommend setting up WSL for a better development experience. [Follow the official guide to install WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

There is also a Docker version.

## 1. Clone the Repository

First, clone the repository and change into the new directory:

```bash
git clone https://github.com/john-automates/AI_Agent_RAG_Tool_Demo.git
cd AI_Agent_RAG_Tool_Demo
```

## 2. Setup Python Virtual Environment

Setting up a virtual environment is crucial for managing the dependencies. Follow these steps:

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows (WSL) or Unix/MacOS
source venv/bin/activate
```

## 3. Install Dependencies

With your virtual environment activated, install the project dependencies using:

```bash
pip install -r requirements.txt
```

## 4. Setup Vector Database and Ingest Handbook

This project uses PGVector for vector storage. Follow these steps to set up your vector database and ingest the Cybersecurity Handbook:

1. Ensure PostgreSQL is installed and running.
2. Install the pgvector extension by following the instructions from the [official pgvector documentation](https://github.com/pgvector/pgvector).
3. Run the following Python code to load and process the documents:

```python
python document_ingest_Recursive.py
```

## 5. Environment Variables Setup

Make sure to set up your `.env` file with all the necessary API keys and database credentials. Rename `env-template.env` to `.env` and fill in the values:

```plaintext
VIRUS_TOTAL_API=
OTX_API=
SHODAN_API=
OPENAI_API_KEY=
URL_SCAN_API_KEY=
DB_TYPE=postgresql
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## 6. Run the Agent

Finally, to run the agent, execute:

```bash
python agent.py
```

## Docker

You must have Docker Desktop installed to use the Docker version. Note, this is for development purposes right now.

```bash
git clone https://github.com/john-automates/AI_Agent_RAG_Tool_Demo.git
cd AI_Agent_RAG_Tool_Demo
cp env-template.env .env
```

Edit .env

```bash
docker compose up -d
```

In Docker Desktop, find ai_agent_rag_tool_demo, app-1, then click the 3 dots and select "Open in terminal". From there, you can type `./document_ingest_Recursive.py` or `./agent.py`.

If you make script changes you need to rebuild the app image.

```bash
docker compose down
docker compose build
docker compose up -d
```

The postgres database is stored in postgres-data. If you run `docker compose down` the database is persisted so that you don't have to re-run `./document_ingest_Recursive.py`.

## Support

For any additional help or clarification on setup and execution, please refer to the documentation or submit an issue on the GitHub repository.
