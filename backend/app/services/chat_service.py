# backend/app/services/chat_service.py

from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.purchase_service import PurchaseService
from app.services.knowledge_service import KnowledgeService
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

class ChatService:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.store = {}
        self.user_service = UserService()
        self.product_service = ProductService()
        self.purchase_service = PurchaseService()

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
            self.add_initial_message(session_id)
        return self.store[session_id]

    def add_initial_message(self, session_id: str):
        initial_message = (
            "Hello! I am your assistant. You can ask me anything about our products or your previous purchases. "
            "To buy a product, simply type 'buy [product_name]'. For example: 'buy laptop'."
        )
        self.store[session_id].add_message({"role": "assistant", "content": initial_message})

    def get_response(self, message, session_id: str):
        history = self.get_session_history(session_id)
        if message.lower().startswith("buy "):
            product_name = message[4:].strip()
            response = self.handle_purchase(product_name, session_id)
        else:
            chain = self.knowledge_service.get_qa_chain()
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

    def handle_purchase(self, product_name, session_id: str):
        username = session_id 
        normalized_product_name = product_name.strip().lower()
        normalized_products = {key.lower(): key for key in self.product_service.products.keys()}

        if normalized_product_name not in normalized_products:
            return f"Sorry, we don't have {product_name} in our store."

        actual_product_name = normalized_products[normalized_product_name]
        product = self.product_service.products[actual_product_name]
        if product.stock <= 0:
            return f"Sorry, {product_name} is out of stock."

        self.product_service.update_product_stock(actual_product_name, 1)
        purchase_message = self.purchase_service.add_purchase(username, actual_product_name, product.price)

        return purchase_message
