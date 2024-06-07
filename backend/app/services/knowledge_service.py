# backend/app/services/knowledge_service.py

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import EnsembleRetriever
import os
from dotenv import load_dotenv

load_dotenv()

class KnowledgeService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.vectorstore = None
        self.purchase_vectorstore = None
        self.load_store_data('data/store_data.csv')
        self.load_purchase_data('data/purchases.csv')

    def load_store_data(self, file_path):
        loader = CSVLoader(file_path=file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    def load_purchase_data(self, file_path):
        loader = CSVLoader(file_path=file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        self.purchase_vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    def get_retriever(self):
        if self.vectorstore is None:
            raise ValueError("Vectorstore has not been initialized. Ensure load_store_data has been called.")
        return self.vectorstore.as_retriever()

    def get_purchase_retriever(self):
        if self.purchase_vectorstore is None:
            raise ValueError("Purchase vectorstore has not been initialized. Ensure load_purchase_data has been called.")
        return self.purchase_vectorstore.as_retriever()

    def get_qa_chain(self):
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        retriever = self.get_retriever()

        purchase_retriever = self.get_purchase_retriever()
        
        retrievers = [retriever, purchase_retriever]

        ensemble_retriever = EnsembleRetriever(retrievers=retrievers)
        history_aware_retriever = create_history_aware_retriever(self.llm, ensemble_retriever, contextualize_q_prompt)
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise. Only consider the purchases made by the user asking the question."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        return create_retrieval_chain(history_aware_retriever, question_answer_chain)