# Advanced Document Retrieval and Question Answering System

This project integrates advanced Natural Language Processing (NLP) and database management techniques to provide an innovative document retrieval and question-answering system. Utilizing the powerful capabilities of OpenAI's language models and PostgreSQL with pgvector for vector storage, this system is designed to enhance the way users interact with and retrieve information from a vast collection of documents.

## Features

- **Multi-Perspective Questioning**: Generates multiple versions of a user query to overcome the limitations of distance-based similarity search in vector databases.
- **Rich Document Retrieval**: Utilizes PostgreSQL with pgvector for efficient storage and retrieval of document embeddings.
- **Comprehensive Answer Generation**: Leverages OpenAI's language models to provide detailed answers based on the context of retrieved documents.
- **Flexible Document Loading and Processing**: Supports loading documents from directories and splitting text into manageable chunks for processing.

## Getting Started

### Prerequisites

- Python 3.6+
- PostgreSQL
- pgvector extension for PostgreSQL
- OpenAI API key for accessing language models

### Installation

1. **Clone the repository**:

```bash
git clone <repository-url>
cd <project-directory>
```

2. **Install required Python packages**:

```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL and pgvector**:

Ensure that PostgreSQL is installed and running. Install the pgvector extension following the instructions from the [official pgvector documentation](https://github.com/pgvector/pgvector).

4. **Environment Variables**:

Create a `.env` file in the project root directory and populate it with the necessary environment variables:

```
POSTGRES_PASSWORD=<your-postgres-password>
POSTGRES_IP=<your-postgres-ip>
POSTGRES_PORT=<your-postgres-port>
OPENAI_API_KEY=<your-openai-api-key>
```

5. **Load Environment Variables**:

The project uses `python-dotenv` to manage environment variables. Ensure all variables are loaded correctly by reviewing the `.env` file.

### Usage

1. **Prepare Your Document Collection**:

Place your documents in a structured directory. This project assumes each document is a text file.

2. **Document Loading and Embedding**:

Run the script to load documents, split them into chunks, and store their embeddings in the PostgreSQL database with pgvector.

```bash
python <script-name>
```

3. **Question Answering**:

Use the provided functions to input a question and receive detailed answers based on the retrieved documents.

```python
question = "Your question here"
result = generate_answer(question, ...)
print(result)
```

## Documentation

- **get_unique_union(documents)**: Merges lists of documents, ensuring uniqueness.
- **format_docs(docs)**: Formats the retrieved documents, including metadata parsing.
- **generate_answer(question, ...)**: Orchestrates the retrieval and answering process.
- **main()**: Entry point for running the document processing and retrieval script.

For more detailed information on function parameters and returns, refer to the inline comments in the codebase.

## Contributing

Contributions to enhance the functionality and performance of this project are welcome. Please follow the standard GitHub pull request process to submit your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
