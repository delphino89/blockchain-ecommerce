"""
product.py - Modèle pour les produits
"""

import uuid

class Product:
    def __init__(self, name, price, description, seller_address, stock=1):
        self.id = str(uuid.uuid4())  # Identifiant unique
        self.name = name
        self.price = price
        self.description = description
        self.seller_address = seller_address
        self.stock = stock
        print(f"📦 Nouveau produit créé: {name} (ID: {self.id[:8]}...)")
    
    def to_dict(self):
        """Convertit le produit en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'seller_address': self.seller_address,
            'stock': self.stock
        }
