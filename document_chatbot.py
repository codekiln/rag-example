"""Simplest script for creating retrieval pipeline and invoking an LLM."""

# Copyright (c) 2023 Brent Benson
#
# This file is part of [project-name], licensed under the MIT License.
# See the LICENSE file in this repository for details.

import os
import pprint

from dotenv import load_dotenv

load_dotenv()

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import AzureChatOpenAI, BedrockChat
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

# Log full text sent to LLM
VERBOSE = False

# Details of persisted embedding store index
COLLECTION_NAME = "federalist_papers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
PERSIST_DIR = "doc_index"

# Size of window for buffered window memory
MEMORY_WINDOW_SIZE = 10


def main():
    azure_model_name = os.getenv("OPENAI_MODEL_NAME")
    aws_bedrock_model_id = os.getenv("AWS_BEDROCK_MODEL_ID")
    aws_credential_profile_name = os.getenv("AWS_CREDENTIAL_PROFILE_NAME")

    # Access persisted embeddings and expose through langchain retriever
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = Chroma(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )
    retriever = db.as_retriever()

    # This version is for AzureOpenAI. Change this function to use
    # a different LLM API
    if azure_model_name:
        llm = AzureChatOpenAI(temperature=0.5, deployment_name=azure_model_name, verbose=VERBOSE)
    elif all([aws_bedrock_model_id, aws_credential_profile_name]):
        # BEDROCK_CLIENT = boto3.client("bedrock", 'us-east-1')
        llm = BedrockChat(temperature=0.5, model_id=aws_bedrock_model_id, credentials_profile_name=aws_credential_profile_name, verbose=VERBOSE)

    # Establish a memory buffer for conversational continuity
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True,
        window_size=MEMORY_WINDOW_SIZE,
    )

    # Put together all of the components into the full
    # chain with memory and retrieval-agumented generation
    query_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=retriever,
        verbose=VERBOSE,
        return_source_documents=True,
    )

    prompt = (
        "How should government responsibility be divided between "
        "the states and the federal government?"
    )
    query_response = query_chain({"question": prompt})
    pprint.pprint(query_response)


if __name__ == "__main__":
    main()
