# backend/app/services/user_service.py

from app.models import User
import csv

class UserService:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        users = {}
        try:
            with open('data/users.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'username' in row and 'password' in row:
                        user = User(row['username'], row['password'])
                        users[user.username] = user
            return users
        except FileNotFoundError:
            return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return users

    def save_user(self, user):
        with open('data/users.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'password'])
            writer.writerow({'username': user.username, 'password': user.password})

    def register_user(self, username, password):
        if username in self.users:
            return False, "Username already exists"
        user = User(username, password)
        self.users[username] = user
        self.save_user(user)
        return True, "User registered successfully"

    def authenticate_user(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return True, "Login successful"
        return False, "Invalid username or password"

    def get_user(self, username):
        return self.users.get(username)
