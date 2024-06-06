class UserContext:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conversation_history = []

    def add_message(self, message):
        self.conversation_history.append(message)

    def get_history(self):
        return self.conversation_history
