"""
storage.py - Sauvegarde dans GitHub
"""

import json
import os
import base64
import requests
from time import time

# Configuration GitHub
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = 'delphino89/blockchain-ecommerce'
GITHUB_PATH = 'blockchain_data.json'

def save_to_github(data):
    """Sauvegarde les données sur GitHub"""
    if not GITHUB_TOKEN:
        print("⚠️ Pas de token GitHub - sauvegarde locale uniquement")
        return False
    
    try:
        # Convertir en JSON
        content = json.dumps(data, indent=2, ensure_ascii=False)
        content_bytes = content.encode('utf-8')
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')
        
        # Vérifier si le fichier existe déjà
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        sha = None
        
        if response.status_code == 200:
            sha = response.json().get('sha')
        
        # Créer ou mettre à jour le fichier
        data_to_send = {
            'message': f'Sauvegarde auto du {time()}',
            'content': content_b64,
            'branch': 'main'
        }
        
        if sha:
            data_to_send['sha'] = sha
        
        response = requests.put(url, headers=headers, json=data_to_send)
        
        if response.status_code in [200, 201]:
            print("✅ Données sauvegardées sur GitHub")
            return True
        else:
            print(f"❌ Erreur GitHub: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur sauvegarde GitHub: {e}")
        return False

def load_from_github():
    """Charge les données depuis GitHub"""
    if not GITHUB_TOKEN:
        print("⚠️ Pas de token GitHub - chargement local uniquement")
        return None
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            content_b64 = response.json().get('content', '')
            content = base64.b64decode(content_b64).decode('utf-8')
            data = json.loads(content)
            print("✅ Données chargées depuis GitHub")
            return data
        else:
            print("📭 Aucune donnée sur GitHub")
            return None
            
    except Exception as e:
        print(f"❌ Erreur chargement GitHub: {e}")
        return None

def save_data(wallets, products, blockchain):
    """Sauvegarde complète des données"""
    try:
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
        
        # Sauvegarde locale
        with open('local_backup.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Sauvegarde GitHub
        save_to_github(data)
        
        print(f"💾 Données sauvegardées: {len(wallets)} utilisateurs")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def load_data(wallets, products, blockchain):
    """Charge les données depuis GitHub ou local"""
    data = None
    
    # Essayer GitHub d'abord
    data = load_from_github()
    
    # Si GitHub échoue, essayer local
    if not data and os.path.exists('local_backup.json'):
        with open('local_backup.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("📀 Chargement depuis sauvegarde locale")
    
    if not data:
        print("📭 Démarrage sans données")
        return False
    
    try:
        wallets.clear()
        wallets.update(data.get('wallets', {}))
        
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
        
        blockchain.difficulty = data.get('blockchain', {}).get('difficulty', 3)
        blockchain.mining_reward = data.get('blockchain', {}).get('mining_reward', 100)
        blockchain.pending_transactions = data.get('blockchain', {}).get('pending_transactions', [])
        
        print(f"📀 Données chargées: {len(wallets)} utilisateurs")
        return True
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return False