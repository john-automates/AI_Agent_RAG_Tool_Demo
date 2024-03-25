FROM python:3.10

RUN mkdir /app /app/utils /app/utils/prompts

# Install requirements first (since it takes a long time and changes less often)
COPY [ "requirements.txt", "/app"]
RUN cd /app && pip install -r requirements.txt

# Copy all files
COPY ["utils", "/app/utils"]
COPY ["Cybersecurity Handbook", "/app/Cybersecurity Handbook"]
COPY ["agent.py", "document_ingest_Recursive.py", "generate_ioc_report.py", "query_docs_multiQuery.py", "tools.json", "/app"]

WORKDIR "/app"
CMD ["tail", "-f", "/dev/null"]
