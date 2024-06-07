# backend/app/models.py

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Purchase:
    def __init__(self, username, date, product, price):
        self.username = username
        self.date = date
        self.product = product
        self.price = price

class Product:
    def __init__(self, product, price, stock, description):
        self.product = product
        self.price = price
        self.stock = stock
        self.description = description