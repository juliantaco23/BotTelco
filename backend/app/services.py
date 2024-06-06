from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
import csv as csv
from datetime import datetime
from app.models import User

load_dotenv()

class KnowledgeService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.vectorstore = None
        self.load_store_data('data/store_data.csv')

    def load_store_data(self, file_path):
        loader = CSVLoader(file_path=file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    def get_retriever(self):
        if self.vectorstore is None:
            raise ValueError("Vectorstore has not been initialized. Ensure load_store_data has been called.")
        return self.vectorstore.as_retriever()

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
        history_aware_retriever = create_history_aware_retriever(self.llm, retriever, contextualize_q_prompt)

        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
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

class ChatService:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.store = {}
        self.load_store_data('data/store_data.csv')  # Cargar los datos del CSV al inicializar

    def load_store_data(self, file_path):
        self.knowledge_service.load_store_data(file_path)

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def get_response(self, message, session_id: str):
        chain = self.knowledge_service.get_qa_chain()
        history = self.get_session_history(session_id)
        conversational_rag_chain = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        result = conversational_rag_chain.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
        response = result["answer"]
        history.add_message({"role": "assistant", "content": response})
        return response
    
class UserService:
    def __init__(self):
        self.users = {}

    def get_user_context(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = ChatMessageHistory()
        return self.users[user_id]
