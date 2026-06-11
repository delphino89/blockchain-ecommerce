"""
storage.py - Gestion de la persistance des données (version GitHub)
"""

import json
import os
import base64
from time import time

DATA_FILE = 'blockchain_data.json'
BACKUP_FILE = 'blockchain_data_backup.json'

def save_data(wallets, products, blockchain):
    """Sauvegarde toutes les données dans un fichier JSON"""
    try:
        # Convertir les données en format sérialisable
        data = {
            'wallets': wallets,
            'products': [],
            'blockchain': {
                'chain': [],
                'difficulty': blockchain.difficulty,
                'mining_reward': blockchain.mining_reward,
                'pending_transactions': blockchain.pending_transactions
            },
            'last_save': time()
        }
        
        # Sauvegarder les produits
        for product in products:
            data['products'].append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'seller_address': product.seller_address,
                'stock': product.stock
            })
        
        # Sauvegarder la blockchain
        for block in blockchain.chain:
            block_data = {
                'index': block.index,
                'transactions': block.transactions,
                'timestamp': block.timestamp,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce,
                'hash': block.hash
            }
            data['blockchain']['chain'].append(block_data)
        
        # Écrire dans le fichier local
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données sauvegardées: {len(wallets)} utilisateurs, {len(products)} produits, {len(blockchain.chain)} blocs")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def load_data(wallets, products, blockchain):
    """Charge les données depuis le fichier JSON"""
    if not os.path.exists(DATA_FILE):
        print("📭 Aucune donnée sauvegardée trouvée. Démarrage avec données par défaut.")
        return False
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Restaurer les wallets
        wallets.clear()
        wallets.update(data.get('wallets', {}))
        
        # Restaurer les produits
        from models.product import Product
        products.clear()
        for p_data in data.get('products', []):
            product = Product(
                name=p_data['name'],
                price=p_data['price'],
                description=p_data['description'],
                seller_address=p_data['seller_address'],
                stock=p_data['stock']
            )
            product.id = p_data['id']
            products.append(product)
        
        # Restaurer la blockchain
        from blockchain.block import Block
        blockchain.chain = []
        for b_data in data.get('blockchain', {}).get('chain', []):
            block = Block(
                index=b_data['index'],
                transactions=b_data['transactions'],
                timestamp=b_data['timestamp'],
                previous_hash=b_data['previous_hash']
            )
            block.nonce = b_data.get('nonce', 0)
            block.hash = b_data['hash']
            blockchain.chain.append(block)
        
        # Restaurer les paramètres
        blockchain.difficulty = data.get('blockchain', {}).get('difficulty', 3)
        blockchain.mining_reward = data.get('blockchain', {}).get('mining_reward', 100)
        blockchain.pending_transactions = data.get('blockchain', {}).get('pending_transactions', [])
        
        last_save = data.get('last_save', 0)
        print(f"📀 Données chargées: {len(wallets)} utilisateurs, {len(products)} produits, {len(blockchain.chain)} blocs")
        if last_save:
            from datetime import datetime
            print(f"🕐 Dernière sauvegarde: {datetime.fromtimestamp(last_save).strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return False