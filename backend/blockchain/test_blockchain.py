"""
test_blockchain.py - Test de la classe Blockchain
"""

from blockchain import Blockchain
import time

print("🧪 TEST DE LA BLOCKCHAIN")
print("="*50)

# 1. Créer une blockchain
print("\n1. Création de la blockchain...")
blockchain = Blockchain()

# 2. Afficher le bloc genesis
print("\n2. Bloc genesis créé :")
blockchain.display_chain()

# 3. Ajouter des transactions
print("\n3. Ajout de transactions...")
blockchain.add_transaction({
    'from': 'Alice',
    'to': 'Bob',
    'amount': 50,
    'type': 'transfer'
})

blockchain.add_transaction({
    'from': 'Bob',
    'to': 'Charlie',
    'amount': 30,
    'type': 'transfer'
})

print(f"   Transactions en attente : {len(blockchain.pending_transactions)}")

# 4. Miner un bloc
print("\n4. Minage d'un bloc...")
blockchain.mine_pending_transactions('Miner_1')

# 5. Afficher la blockchain après minage
print("\n5. Blockchain après minage :")
blockchain.display_chain()

# 6. Ajouter plus de transactions et miner un autre bloc
print("\n6. Ajout de plus de transactions...")
blockchain.add_transaction({
    'from': 'Charlie',
    'to': 'Alice',
    'amount': 20,
    'type': 'transfer'
})

print("\n7. Minage d'un second bloc...")
blockchain.mine_pending_transactions('Miner_2')

# 8. Afficher la blockchain complète
print("\n8. Blockchain complète :")
blockchain.display_chain()

# 9. Vérifier les soldes
print("\n9. Vérification des soldes :")
print(f"   Solde de Alice: {blockchain.get_balance('Alice')}")
print(f"   Solde de Bob: {blockchain.get_balance('Bob')}")
print(f"   Solde de Charlie: {blockchain.get_balance('Charlie')}")
print(f"   Solde de Miner_1: {blockchain.get_balance('Miner_1')}")
print(f"   Solde de Miner_2: {blockchain.get_balance('Miner_2')}")

# 10. Vérifier la validité
print("\n10. Validation de la blockchain :")
blockchain.is_valid()

print("\n🎉 Test de la blockchain terminé !")
