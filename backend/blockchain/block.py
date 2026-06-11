"""
block.py - La classe Block avec Proof of Work
"""

import hashlib
import json

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        target = '0' * difficulty
        
        print(f"   🔍 Minage du bloc {self.index}...")
        print(f"   🎯 Difficulté : trouver un hash commençant par {target}")
        
        attempts = 0
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            attempts += 1
            
            if attempts % 1000 == 0:
                print(f"   ⏳ {attempts} tentatives... hash actuel: {self.hash[:15]}...")
        
        print(f"   ✅ Bloc miné en {attempts} tentatives!")
        print(f"   🔑 Hash trouvé: {self.hash}")
        print(f"   🔢 Nonce final: {self.nonce}")
        
        return True
    
    def __str__(self):
        return f"Bloc {self.index} - Hash: {self.hash[:15]}... (Nonce: {self.nonce})"