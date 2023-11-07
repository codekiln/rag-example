FROM python:3.11-slim-bookworm

ENV HOST=0.0.0.0
ENV LISTEN_PORT 8080
EXPOSE 8080

# Set the working directory in the container to /app
WORKDIR /app

COPY --chmod=0700 requirements /app/requirements

RUN --mount=type=cache,id=pip_cache,sharing=locked,target=/root/.cache/pip \
    pip install --quiet --upgrade $(grep -e '^pip' /app/requirements/requirements-pip.txt) \
    && pip install --quiet setuptools \
    && pip install --quiet pip-tools==7.3.0

# Install packages
RUN pip-sync /app/requirements/requirements.txt

RUN mkdir /app/doc_index

# Copy the current directory contents into the container at /app
COPY document_chatbot.py /app
COPY document_chatbot_ui.py /app
COPY index_documents.py /app
COPY search_index.py /app
COPY search_index_ui.py /app

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app.py when the container launches
CMD ["streamlit", "run", "search_index_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
