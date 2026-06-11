"""
test_block.py - Test de la classe Block
"""

from block import Block
import time

print("🧪 TEST DU BLOCK")
print("-" * 40)

# Test 1 : Création d'un bloc
print("\n1. Création d'un bloc...")
bloc1 = Block(
    index=0,
    transactions=["Achat de produit X"],
    timestamp=time.time(),
    previous_hash="0"
)

print(f"   ✅ Bloc créé !")
print(f"   Index: {bloc1.index}")
print(f"   Début du hash: {bloc1.hash[:15]}...")
print(f"   Hash du bloc précédent: {bloc1.previous_hash}")

# Test 2 : Unicité du hash
print("\n2. Test d'unicité du hash...")
time.sleep(1)
bloc2 = Block(
    index=0,
    transactions=["Achat de produit X"],
    timestamp=time.time(),
    previous_hash="0"
)

print(f"   Hash du bloc 1: {bloc1.hash[:20]}...")
print(f"   Hash du bloc 2: {bloc2.hash[:20]}...")

if bloc1.hash != bloc2.hash:
    print("   ✅ Les hashs sont différents (chaque bloc est unique)")
else:
    print("   ❌ Problème : les hashs sont identiques")

# Test 3 : Affichage
print("\n3. Test d'affichage...")
print(f"   {bloc1}")

print("\n🎉 Test terminé !")
