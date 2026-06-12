"""
app.py - Serveur Flask principal (Version avec mots de passe)
"""
from storage import save_data, load_data
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
from time import time
import uuid
import hashlib

# Ajouter le chemin pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blockchain.blockchain import Blockchain
from models.product import Product
from services.qr_service import QRService

# Créer l'application Flask
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialiser la blockchain
print("🚀 Démarrage du serveur...")
blockchain = Blockchain()

# Stockage des produits
products = []

# Stockage des wallets
wallets = {}

# Charger les données sauvegardées
load_data(wallets, products, blockchain)

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie si le mot de passe correspond au hash"""
    return hash_password(password) == password_hash

# ==================== ROUTES API ====================

@app.route('/')
def serve_frontend():
    """Sert la page d'accueil"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/wallet/register', methods=['POST'])
def register_wallet():
    """
    Crée un nouveau wallet avec nom et mot de passe
    """
    data = request.json
    user_name = data.get('name', '').strip()
    password = data.get('password', '')
    
    if not user_name:
        return jsonify({'error': 'Veuillez entrer votre nom'}), 400
    
    if not password or len(password) < 4:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 4 caractères'}), 400
    
    # Vérifier si le nom existe déjà
    for addr, info in wallets.items():
        if info['name'].lower() == user_name.lower():
            return jsonify({'error': f'Le nom "{user_name}" est déjà utilisé. Choisissez un autre nom.'}), 400
    
    # Créer une adresse unique
    address = f"wallet_{uuid.uuid4().hex[:8]}"
    
    # Hasher le mot de passe
    password_hash = hash_password(password)
    
    # Créer le wallet
    wallets[address] = {
        'name': user_name,
        'password_hash': password_hash,
        'created_at': time()
    }
    
    # Donner 1000 tokens de départ au nouveau wallet
    initial_transaction = {
        'from': 'SYSTEM',
        'to': address,
        'amount': 1000,
        'type': 'initial_balance',
        'timestamp': time(),
        'note': f'Bienvenue {user_name} ! Voici 1000 tokens pour commencer'
    }
    blockchain.add_transaction(initial_transaction)
    
    # Miner automatiquement le premier bloc si nécessaire
    if len(blockchain.chain) == 1:
        blockchain.mine_pending_transactions(address)
        print(f"⛏️ Premier bloc miné pour {user_name}")
    
    print(f"👤 Nouveau wallet créé: {user_name} ({address})")
    
    save_data(wallets, products, blockchain)

    return jsonify({
        'success': True,
        'address': address,
        'name': user_name,
        'balance': 1000,
        'message': f'✅ Compte créé avec succès ! Bienvenue {user_name} !'
    })

@app.route('/api/wallet/login', methods=['POST'])
def login_wallet():
    """
    Connexion avec nom et mot de passe
    """
    data = request.json
    user_name = data.get('name', '').strip()
    password = data.get('password', '')
    
    if not user_name or not password:
        return jsonify({'error': 'Veuillez entrer votre nom et mot de passe'}), 400
    
    # Chercher le wallet par nom
    for address, info in wallets.items():
        if info['name'].lower() == user_name.lower():
            # Vérifier le mot de passe
            if verify_password(password, info['password_hash']):
                balance = blockchain.get_balance(address)
                return jsonify({
                    'success': True,
                    'address': address,
                    'name': info['name'],
                    'balance': balance,
                    'message': f'✅ Bonjour {info["name"]} ! Votre solde est de {balance} tokens.'
                })
            else:
                return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    return jsonify({'error': f'Aucun utilisateur trouvé avec le nom "{user_name}"'}), 404

@app.route('/api/wallet/list', methods=['GET'])
def list_wallets():
    """Liste tous les wallets (SANS les soldes pour la confidentialité)"""
    wallet_list = []
    for addr, data in wallets.items():
        wallet_list.append({
            'address': addr,
            'name': data['name'],
            'created_at': data['created_at']
            # NE PAS inclure 'balance' ici
        })
    # Trier par nom
    wallet_list.sort(key=lambda x: x['name'])
    return jsonify(wallet_list)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Classement anonyme des plus riches"""
    leaderboard = []
    for addr, data in wallets.items():
        balance = blockchain.get_balance(addr)
        # Anonymiser le nom (ex: "Jean" → "J***")
        name = data['name']
        if len(name) > 1:
            anon_name = name[0] + '*' * (len(name) - 1)
        else:
            anon_name = name[0] + '*'
        leaderboard.append({
            'name': anon_name,
            'balance': balance
        })
    leaderboard.sort(key=lambda x: x['balance'], reverse=True)
    return jsonify(leaderboard[:10])

@app.route('/api/wallet/change-password', methods=['POST'])
def change_password():
    """
    Change le mot de passe d'un utilisateur
    """
    data = request.json
    address = data.get('address')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not address or not old_password or not new_password:
        return jsonify({'error': 'Données manquantes'}), 400
    
    if address not in wallets:
        return jsonify({'error': 'Wallet inconnu'}), 404
    
    if len(new_password) < 4:
        return jsonify({'error': 'Le nouveau mot de passe doit contenir au moins 4 caractères'}), 400
    
    # Vérifier l'ancien mot de passe
    if not verify_password(old_password, wallets[address]['password_hash']):
        return jsonify({'error': 'Ancien mot de passe incorrect'}), 401
    
    # Changer le mot de passe
    wallets[address]['password_hash'] = hash_password(new_password)
    
    save_data(wallets, products, blockchain)

    return jsonify({
        'success': True,
        'message': 'Mot de passe changé avec succès !'
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Retourne tous les produits avec le nom du vendeur"""
    products_with_names = []
    for p in products:
        product_dict = p.to_dict()
        # Ajouter le nom du vendeur
        seller_name = wallets.get(p.seller_address, {}).get('name', p.seller_address[:8])
        product_dict['seller_name'] = seller_name
        products_with_names.append(product_dict)
    return jsonify(products_with_names)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Ajoute un nouveau produit"""
    data = request.json
    seller_address = data.get('seller_address')
    
    if seller_address not in wallets:
        return jsonify({'error': 'Wallet inconnu. Veuillez vous reconnecter.'}), 400
    
    product = Product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        seller_address=seller_address,
        stock=data.get('stock', 1)
    )
    products.append(product)
    seller_name = wallets[seller_address]['name']
    print(f"📦 Produit ajouté: {product.name} par {seller_name} (prix: {product.price} tokens)")
    save_data(wallets, products, blockchain)
    return jsonify(product.to_dict())

@app.route('/api/purchase', methods=['POST'])
def purchase_product():
    """Effectue un achat"""
    data = request.json
    product_id = data['product_id']
    buyer_address = data['buyer_address']
    
    if buyer_address not in wallets:
        return jsonify({'error': 'Wallet inconnu. Veuillez vous reconnecter.'}), 400
    
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        return jsonify({'error': 'Produit non trouvé'}), 404
    
    if product.stock <= 0:
        return jsonify({'error': 'Stock épuisé'}), 400
    
    # ✅ NOUVEAU : Empêcher l'auto-achat
    if buyer_address == product.seller_address:
        seller_name = wallets[product.seller_address]['name']
        return jsonify({'error': f'❌ {seller_name}, vous ne pouvez pas acheter votre propre produit !'}), 400
    
    buyer_balance = blockchain.get_balance(buyer_address)
    if buyer_balance < product.price:
        return jsonify({
            'error': f'Solde insuffisant. Vous avez {buyer_balance} tokens, besoin de {product.price} tokens.\n\n💡 Astuce: Minez des blocs pour gagner des tokens !'
        }), 400
    
    transaction = {
        'from': buyer_address,
        'to': product.seller_address,
        'amount': product.price,
        'product_id': product_id,
        'product_name': product.name,
        'buyer_name': wallets[buyer_address]['name'],
        'seller_name': wallets[product.seller_address]['name'],
        'type': 'purchase',
        'timestamp': time()
    }
    
    blockchain.add_transaction(transaction)
    product.stock -= 1
    
    qr_payment = QRService.generate_payment_qr(transaction)
    qr_certificate = QRService.generate_certificate_qr(product, f"tx_{len(blockchain.chain)}")
    save_data(wallets, products, blockchain)
    return jsonify({
        'success': True,
        'message': f'✅ {transaction["buyer_name"]} a acheté {product.name} pour {product.price} tokens!',
        'qr_payment': qr_payment,
        'qr_certificate': qr_certificate,
        'product': product.to_dict(),
        'transaction': transaction
    })

@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    """Retourne le solde d'une adresse"""
    balance = blockchain.get_balance(address)
    name = wallets.get(address, {}).get('name', address[:8])
    return jsonify({
        'address': address,
        'name': name,
        'balance': balance,
        'pending_transactions': len(blockchain.pending_transactions)
    })

@app.route('/api/mine', methods=['POST'])
def mine_block():
    """Mine un nouveau bloc avec affichage détaillé des transactions"""
    data = request.json
    miner_address = data.get('miner_address')
    
    if not miner_address or miner_address not in wallets:
        return jsonify({'error': 'Wallet invalide. Veuillez vous reconnecter.'}), 400
    
    if len(blockchain.pending_transactions) == 0:
        return jsonify({'error': '📭 Aucune transaction à miner.\n\n💡 Pour créer des transactions:\n- Ajoutez des produits\n- Achetez des produits\n- Inscrivez un nouvel utilisateur'}), 400
    
    # ✅ AMÉLIORÉ : Compter et afficher les détails des transactions
    tx_count = len(blockchain.pending_transactions)
    purchase_count = sum(1 for tx in blockchain.pending_transactions if tx.get('type') == 'purchase')
    reward_count = sum(1 for tx in blockchain.pending_transactions if tx.get('type') == 'reward')
    initial_count = sum(1 for tx in blockchain.pending_transactions if tx.get('type') == 'initial_balance')
    
    # Construire un message détaillé
    tx_details = []
    for tx in blockchain.pending_transactions:
        if tx.get('type') == 'purchase':
            buyer = wallets.get(tx['from'], {}).get('name', tx['from'][:8])
            seller = wallets.get(tx['to'], {}).get('name', tx['to'][:8])
            tx_details.append(f"   💸 {buyer} → {seller}: {tx['amount']} tokens ({tx['product_name']})")
        elif tx.get('type') == 'initial_balance':
            new_user = wallets.get(tx['to'], {}).get('name', tx['to'][:8])
            tx_details.append(f"   🎉 {new_user} (nouveau compte: +1000 tokens)")
        elif tx.get('type') == 'reward':
            miner = wallets.get(tx['to'], {}).get('name', tx['to'][:8])
            tx_details.append(f"   🎁 Récompense: +{tx['amount']} tokens pour {miner}")
    
    # Afficher dans la console du serveur
    print(f"\n📋 {'='*50}")
    print(f"⛏️  MINAGE EN COURS par {wallets[miner_address]['name']}")
    print(f"📊 {tx_count} transaction(s) à valider:")
    for detail in tx_details:
        print(detail)
    print(f"{'='*50}")
    
    # Miner le bloc
    blockchain.mine_pending_transactions(miner_address)
    
    miner_name = wallets[miner_address]['name']
    
    # Retourner un message détaillé au frontend
    tx_summary = "\n".join(tx_details[:5])  # Limiter à 5 pour l'affichage
    if len(tx_details) > 5:
        tx_summary += f"\n   ... et {len(tx_details)-5} autre(s) transaction(s)"
    
    save_data(wallets, products, blockchain)

    return jsonify({
        'success': True,
        'message': f'⛏️ {miner_name} a miné un bloc !\n\n📦 {tx_count} transaction(s) validée(s):\n{tx_summary}\n\n💰 Récompense: +100 tokens !',
        'block_index': len(blockchain.chain) - 1,
        'pending_transactions': len(blockchain.pending_transactions),
        'miner': miner_name,
        'transactions_mined': tx_count,
        'transaction_details': tx_details
    })

@app.route('/api/blockchain/info', methods=['GET'])
def get_blockchain_info():
    """Retourne les informations de la blockchain"""
    return jsonify({
        'length': len(blockchain.chain),
        'difficulty': blockchain.difficulty,
        'pending_transactions': len(blockchain.pending_transactions),
        'is_valid': blockchain.is_valid(),
        'latest_block': {
            'index': blockchain.get_latest_block().index,
            'hash': blockchain.get_latest_block().hash[:20] + '...',
            'transactions_count': len(blockchain.get_latest_block().transactions)
        }
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Retourne toutes les transactions"""
    all_transactions = []
    for block in blockchain.chain:
        for tx in block.transactions:
            if isinstance(tx, dict):
                tx_display = tx.copy()
                if tx.get('from') and tx.get('from') in wallets:
                    tx_display['from_name'] = wallets[tx['from']]['name']
                if tx.get('to') and tx.get('to') in wallets:
                    tx_display['to_name'] = wallets[tx['to']]['name']
                tx_display['block_index'] = block.index
                all_transactions.append(tx_display)
    
    return jsonify(all_transactions[-30:])

@app.route('/api/test', methods=['GET'])
def test():
    """Route de test"""
    return jsonify({
        'status': 'OK',
        'blockchain_length': len(blockchain.chain),
        'products_count': len(products),
        'wallets_count': len(wallets),
        'pending_transactions': len(blockchain.pending_transactions)
    })
# Ajouter après les produits
ratings = {}  # Format: {product_id: [{'user': name, 'rating': 1-5, 'comment': ''}]}

@app.route('/api/rating', methods=['POST'])
def add_rating():
    """Ajoute une évaluation pour un produit"""
    data = request.json
    product_id = data.get('product_id')
    buyer_address = data.get('buyer_address')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not product_id or not buyer_address or not rating:
        return jsonify({'error': 'Données manquantes'}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Note doit être entre 1 et 5'}), 400
    
    # Vérifier que l'acheteur a bien acheté ce produit
    has_purchased = False
    for block in blockchain.chain:
        for tx in block.transactions:
            if (isinstance(tx, dict) and 
                tx.get('type') == 'purchase' and 
                tx.get('product_id') == product_id and 
                tx.get('from') == buyer_address):
                has_purchased = True
                break
    
    if not has_purchased:
        return jsonify({'error': 'Vous n\'avez pas acheté ce produit'}), 400
    
    if product_id not in ratings:
        ratings[product_id] = []
    
    ratings[product_id].append({
        'user': wallets[buyer_address]['name'],
        'rating': rating,
        'comment': comment,
        'timestamp': time()
    })
    
    return jsonify({'success': True, 'message': 'Évaluation ajoutée !'})

@app.route('/api/rating/<product_id>', methods=['GET'])
def get_ratings(product_id):
    """Récupère les évaluations d'un produit"""
    product_ratings = ratings.get(product_id, [])
    avg_rating = 0
    if product_ratings:
        avg_rating = sum(r['rating'] for r in product_ratings) / len(product_ratings)
    
    return jsonify({
        'ratings': product_ratings,
        'average': avg_rating,
        'count': len(product_ratings)
    })

@app.route('/api/save', methods=['POST'])
def manual_save():
    """Sauvegarde manuelle des données"""
    if save_data(wallets, products, blockchain):
        return jsonify({'success': True, 'message': 'Données sauvegardées'})
    else:
        return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500
    
@app.route('/api/save', methods=['POST', 'GET'])
def force_save():
    """Sauvegarde forcée des données"""
    if save_data(wallets, products, blockchain):
        return jsonify({'success': True, 'message': 'Sauvegarde effectuée'})
    return jsonify({'error': 'Erreur sauvegarde'}), 500
    
if __name__ == '__main__':
    print("="*60)
    print("🔐 SERVEUR BLOCKCHAIN AVEC MOTS DE PASSE")
    print("="*60)
    print(f"📱 Interface: http://localhost:5000")
    print(f"🔗 API test: http://localhost:5000/api/test")
    print("\n💡 INSTRUCTIONS:")
    print("   1. Créez un compte avec votre nom et un mot de passe")
    print("   2. Connectez-vous avec vos identifiants")
    print("   3. Minez des blocs pour gagner des tokens")
    print("   4. Ajoutez des produits à vendre")
    print("   5. Achetez des produits avec d'autres comptes")
    print("\n🔒 Sécurité: Les mots de passe sont hachés (SHA-256)")
    print("="*60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')