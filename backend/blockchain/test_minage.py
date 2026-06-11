"""
test_minage.py - Test du vrai mécanisme de minage
"""

from blockchain import Blockchain
import time

print("🚀 TEST DU VRAI MINAGE (PROOF OF WORK)")
print("="*60)

# Créer la blockchain
print("\n1. Création de la blockchain...")
blockchain = Blockchain()

# Ajouter des transactions
print("\n2. Ajout de transactions...")
blockchain.add_transaction({'from': 'Alice', 'to': 'Bob', 'amount': 50})
blockchain.add_transaction({'from': 'Bob', 'to': 'Charlie', 'amount': 30})

print(f"\n   📊 Transactions en attente: {len(blockchain.pending_transactions)}")

# Miner le premier bloc
print("\n3. Minage du premier bloc...")
start = time.time()
blockchain.mine_pending_transactions('Miner_1')
mining_time = time.time() - start

# Ajouter plus de transactions
print("\n4. Ajout de plus de transactions...")
time.sleep(1)  # Pour avoir des timestamps différents
blockchain.add_transaction({'from': 'Charlie', 'to': 'Alice', 'amount': 20})
blockchain.add_transaction({'from': 'Alice', 'to': 'David', 'amount': 40})

# Miner le deuxième bloc
print("\n5. Minage du deuxième bloc...")
start = time.time()
blockchain.mine_pending_transactions('Miner_2')
mining_time2 = time.time() - start

# Afficher la blockchain
blockchain.display_chain()

# Afficher les soldes
print("\n📊 SOLDES FINAUX:")
print("-"*40)
print(f"   Alice: {blockchain.get_balance('Alice')} tokens")
print(f"   Bob: {blockchain.get_balance('Bob')} tokens")
print(f"   Charlie: {blockchain.get_balance('Charlie')} tokens")
print(f"   David: {blockchain.get_balance('David')} tokens")
print(f"   Miner_1: {blockchain.get_balance('Miner_1')} tokens")
print(f"   Miner_2: {blockchain.get_balance('Miner_2')} tokens")

print("\n🎉 TEST TERMINÉ!")
print(f"⏱️  Temps total de minage: {mining_time + mining_time2:.2f} secondes")
