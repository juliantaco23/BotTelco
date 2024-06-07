# backend/app/services/product_service.py

import csv
from app.models import Product

class ProductService:
    def __init__(self):
        self.products = self.load_products()

    def load_products(self):
        products = {}
        try:
            with open('data/store_data.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'product' in row and 'price' in row and 'stock' in row and 'description' in row:
                        product = Product(row['product'], row['price'], int(row['stock']), row['description'])
                        products[product.product] = product
            return products
        except FileNotFoundError:
            return products
        except Exception as e:
            print(f"Error loading products: {e}")
            return products

    def update_product_stock(self, product_name, quantity):
        if product_name in self.products:
            self.products[product_name].stock -= quantity
            self.save_products()

    def save_products(self):
        with open('data/store_data.csv', mode='w', newline='') as file:
            fieldnames = ['product', 'price', 'stock', 'description']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for product in self.products.values():
                writer.writerow({
                    'product': product.product,
                    'price': product.price,
                    'stock': product.stock,
                    'description': product.description
                })
