"""
blockchain.py - La classe Blockchain avec vrai minage
"""

# CORRECTION: Utiliser l'import relatif
from .block import Block
import time

class Blockchain:
    def __init__(self):
        """
        Initialise la blockchain
        """
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 3  # Difficulté augmentée à 3 (3 zéros)
        self.mining_reward = 100
        
        self.create_genesis_block()
        print(f"✅ Blockchain initialisée (difficulté: {self.difficulty})")
    
    def create_genesis_block(self):
        """
        Crée le bloc genesis
        """
        genesis_block = Block(
            index=0,
            transactions=["Bloc Genesis - Début de la blockchain"],
            timestamp=time.time(),
            previous_hash="0"
        )
        # Le bloc genesis n'a pas besoin d'être miné
        self.chain.append(genesis_block)
        print(f"   📦 Bloc genesis créé: {genesis_block.hash[:20]}...")
    
    def get_latest_block(self):
        """
        Retourne le dernier bloc
        """
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """
        Ajoute une transaction en attente
        """
        self.pending_transactions.append(transaction)
        print(f"💰 Transaction: {transaction.get('from')} → {transaction.get('to')}: {transaction.get('amount')}")
        return True
    
    def mine_pending_transactions(self, miner_address):
        """
        MINE LES TRANSACTIONS AVEC PROOF OF WORK
        """
        print(f"\n⛏️  MINAGE POUR {miner_address}")
        print("-" * 40)
        
        # 1. Ajouter la récompense de minage
        reward_transaction = {
            'from': 'SYSTEM',
            'to': miner_address,
            'amount': self.mining_reward,
            'type': 'reward',
            'timestamp': time.time()
        }
        self.pending_transactions.append(reward_transaction)
        print(f"   🎁 Récompense ajoutée: {self.mining_reward} tokens")
        
        # 2. Créer le nouveau bloc
        print(f"   📦 Création du bloc {len(self.chain)}...")
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )
        
        # 3. MINER LE BLOC
        start_time = time.time()
        new_block.mine_block(self.difficulty)
        mining_time = time.time() - start_time
        
        # 4. Ajouter le bloc à la chaîne
        self.chain.append(new_block)
        
        # 5. Vider les transactions en attente
        self.pending_transactions = []
        
        print(f"\n✨ BLOC #{new_block.index} MINÉ AVEC SUCCÈS!")
        print(f"   ⏱️  Temps de minage: {mining_time:.2f} secondes")
        print(f"   🔗 Hash du bloc: {new_block.hash}")
        print(f"   🔗 Précédent: {new_block.previous_hash[:20]}...")
        
        return new_block
    
    def get_balance(self, address):
        """
        Calcule le solde d'une adresse
        """
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict):
                    if transaction.get('to') == address:
                        balance += transaction.get('amount', 0)
                    if transaction.get('from') == address:
                        balance -= transaction.get('amount', 0)
        
        return balance
    
    def display_chain(self):
        """
        Affiche toute la blockchain
        """
        print("\n" + "="*60)
        print("📦 BLOCKCHAIN COMPLÈTE")
        print("="*60)
        
        for block in self.chain:
            print(f"\n🔷 BLOC #{block.index}")
            print(f"   📝 Hash: {block.hash}")
            print(f"   🔗 Précédent: {block.previous_hash[:30]}...")
            print(f"   ⏰ Timestamp: {block.timestamp}")
            print(f"   🔢 Nonce: {block.nonce}")
            print(f"   💰 Transactions ({len(block.transactions)}):")
            
            for tx in block.transactions:
                if isinstance(tx, dict):
                    if tx.get('type') == 'reward':
                        print(f"      🎁 RÉCOMPENSE: +{tx['amount']} → {tx['to']}")
                    else:
                        print(f"      💸 {tx.get('from')} → {tx.get('to')}: {tx.get('amount')}")
                else:
                    print(f"      📝 {tx}")
        
        print("\n" + "="*60)
        print(f"✅ TOTAL: {len(self.chain)} blocs | 🔒 VALIDE: {self.is_valid()}")
        print("="*60)
    
    def is_valid(self):
        """
        Vérifie l'intégrité de la blockchain
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Vérifier si le hash est correct
            if current.hash != current.calculate_hash():
                print(f"❌ Bloc {i}: hash invalide")
                return False
            
            # Vérifier le lien avec le bloc précédent
            if current.previous_hash != previous.hash:
                print(f"❌ Bloc {i}: lien invalide")
                return False
            
            # Vérifier si le hash respecte la difficulté
            target = '0' * self.difficulty
            if current.hash[:self.difficulty] != target:
                print(f"❌ Bloc {i}: proof of work invalide (hash: {current.hash[:self.difficulty]})")
                return False
        
        return True