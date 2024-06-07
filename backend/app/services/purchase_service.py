# backend/app/services/purchase_service.py

from app.models import Purchase
import csv
from datetime import datetime

class PurchaseService:
    def __init__(self):
        self.purchases = self.load_purchases()

    def load_purchases(self):
        purchases = []
        try:
            with open('data/purchases.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'username' in row and 'date' in row and 'product' in row and 'price' in row:
                        purchase = Purchase(row['username'], row['date'], row['product'], row['price'])
                        purchases.append(purchase)
            return purchases
        except FileNotFoundError:
            return purchases
        except Exception as e:
            print(f"Error loading purchases: {e}")
            return purchases

    def save_purchase(self, purchase):
        with open('data/purchases.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'date', 'product', 'price'])
            writer.writerow({'username': purchase.username, 'date': purchase.date, 'product': purchase.product, 'price': purchase.price})

    def add_purchase(self, username, product_name, price):
        purchase = Purchase(username, datetime.now().strftime("%Y-%m-%d"), product_name, price)
        self.purchases.append(purchase)
        self.save_purchase(purchase)
        return f"Purchase of {product_name} for {price} has been successfully recorded. You can pay using this link: http://example.com/pay"
