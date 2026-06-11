// script.js - Version avec mots de passe

let currentWallet = null;
let currentWalletName = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔐 Application démarrée');
    
    // Vérifier si un utilisateur est déjà connecté (session)
    const savedWallet = localStorage.getItem('blockchain_wallet');
    const savedName = localStorage.getItem('blockchain_name');
    
    if (savedWallet && savedName) {
        currentWallet = savedWallet;
        currentWalletName = savedName;
        loadMainApp();
    }
});

// Afficher l'onglet actif
function showTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const tabs = document.querySelectorAll('.tab-btn');
    
    if (tab === 'login') {
        loginTab.style.display = 'block';
        registerTab.style.display = 'none';
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        loginTab.style.display = 'none';
        registerTab.style.display = 'block';
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

// Connexion
async function login() {
    const name = document.getElementById('loginName').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!name) {
        alert('Veuillez entrer votre nom');
        return;
    }
    
    if (!password) {
        alert('Veuillez entrer votre mot de passe');
        return;
    }
    
    try {
        const response = await fetch('/api/wallet/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, password: password })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentWallet = result.address;
            currentWalletName = result.name;
            
            // Sauvegarder dans localStorage
            localStorage.setItem('blockchain_wallet', currentWallet);
            localStorage.setItem('blockchain_name', currentWalletName);
            
            alert(result.message);
            loadMainApp();
        } else {
            alert(`❌ ${result.error}`);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur de connexion au serveur');
    }
}

// Inscription
async function register() {
    const name = document.getElementById('registerName').value.trim();
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    
    if (!name) {
        alert('Veuillez choisir un nom');
        return;
    }
    
    if (!password || password.length < 4) {
        alert('Le mot de passe doit contenir au moins 4 caractères');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Les mots de passe ne correspondent pas');
        return;
    }
    
    try {
        const response = await fetch('/api/wallet/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, password: password })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentWallet = result.address;
            currentWalletName = result.name;
            
            // Sauvegarder dans localStorage
            localStorage.setItem('blockchain_wallet', currentWallet);
            localStorage.setItem('blockchain_name', currentWalletName);
            
            alert(result.message);
            loadMainApp();
        } else {
            alert(`❌ ${result.error}`);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur de connexion au serveur');
    }
}

// Déconnexion
function logout() {
    localStorage.removeItem('blockchain_wallet');
    localStorage.removeItem('blockchain_name');
    currentWallet = null;
    currentWalletName = null;
    
    document.getElementById('authScreen').style.display = 'block';
    document.getElementById('mainApp').style.display = 'none';
    document.getElementById('userInfo').style.display = 'none';
    
    // Réinitialiser les formulaires
    document.getElementById('loginName').value = '';
    document.getElementById('loginPassword').value = '';
    document.getElementById('registerName').value = '';
    document.getElementById('registerPassword').value = '';
    document.getElementById('registerConfirmPassword').value = '';
}

// Afficher le modal pour changer le mot de passe
function showPasswordModal() {
    document.getElementById('passwordModal').style.display = 'flex';
    document.getElementById('oldPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmNewPassword').value = '';
}

// Fermer le modal
function closePasswordModal() {
    document.getElementById('passwordModal').style.display = 'none';
}

// Changer le mot de passe
async function changePassword() {
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmNewPassword').value;
    
    if (!oldPassword || !newPassword) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    if (newPassword.length < 4) {
        alert('Le nouveau mot de passe doit contenir au moins 4 caractères');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        alert('Les nouveaux mots de passe ne correspondent pas');
        return;
    }
    
    try {
        const response = await fetch('/api/wallet/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                address: currentWallet,
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ Mot de passe changé avec succès !');
            closePasswordModal();
        } else {
            alert(`❌ ${result.error}`);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur lors du changement de mot de passe');
    }
}

// Charger l'application principale
async function loadMainApp() {
    document.getElementById('authScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    document.getElementById('userInfo').style.display = 'flex';
    
    // Afficher le nom de l'utilisateur
    document.getElementById('userName').textContent = `👤 ${currentWalletName}`;
    
    // Événements
    document.getElementById('addProductForm').addEventListener('submit', addProduct);
    document.getElementById('mineBtn').addEventListener('click', mineBlock);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('changePasswordBtn').addEventListener('click', showPasswordModal);
    
    // Charger les données
    await updateBalance();
    await loadProducts();
    await updateBlockchainInfo();
    await loadTransactions();
    await loadUsers();
    await updateDashboard();
    
    // Rafraîchir périodiquement
    setInterval(() => {
        if (currentWallet) {
            updateBalance();
            updateBlockchainInfo();
            loadUsers();
            updateDashboard();
        }
    }, 5000);
}

// Mettre à jour le solde
async function updateBalance() {
    if (!currentWallet) return;
    
    try {
        const response = await fetch(`/api/balance/${currentWallet}`);
        const data = await response.json();
        document.getElementById('balance').textContent = data.balance;
    } catch (error) {
        console.error('Erreur solde:', error);
    }
}

// Charger les produits
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Erreur chargement produits:', error);
        document.getElementById('productsList').innerHTML = '<div class="loading">❌ Erreur de connexion au serveur</div>';
    }
}

// Afficher les produits
function displayProducts(products) {
    const container = document.getElementById('productsList');
    
    if (products.length === 0) {
        container.innerHTML = '<div class="loading">📦 Aucun produit disponible. Ajoutez-en un !</div>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="product-card">
            <h3>${escapeHtml(product.name)}</h3>
            <p>${escapeHtml(product.description)}</p>
            <div class="product-price">💰 ${product.price} tokens</div>
            <div class="product-stock">📦 Stock: ${product.stock}</div>
            <div class="product-seller">👤 Vendeur: ${product.seller_name || product.seller_address.slice(0, 12)}</div>
            <button class="buy-btn" onclick="buyProduct('${product.id}')" ${product.stock <= 0 ? 'disabled' : ''}>
                🛒 Acheter
            </button>
        </div>
    `).join('');
}

// Acheter un produit - AVEC CONFIRMATION
async function buyProduct(productId) {
    if (!currentWallet) {
        alert('⚠️ Veuillez vous connecter');
        return;
    }
    
    // Trouver le produit dans la liste
    const productsResponse = await fetch('/api/products');
    const allProducts = await productsResponse.json();
    const product = allProducts.find(p => p.id === productId);
    
    if (!product) {
        alert('❌ Produit non trouvé');
        return;
    }
    
    // ✅ DEMANDER CONFIRMATION
    const confirmation = confirm(
        `🛒 Confirmation d'achat\n\n` +
        `Produit : ${product.name}\n` +
        `Prix : ${product.price} tokens\n` +
        `Vendeur : ${product.seller_name || product.seller_address.slice(0, 12)}\n\n` +
        `Souhaitez-vous confirmer cet achat ?`
    );
    
    if (!confirmation) {
        alert('❌ Achat annulé');
        return;
    }
    
    try {
        const response = await fetch('/api/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                buyer_address: currentWallet
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Afficher les QR codes
            document.getElementById('qrSection').style.display = 'block';
            document.getElementById('paymentQR').src = `data:image/png;base64,${result.qr_payment}`;
            document.getElementById('certificateQR').src = `data:image/png;base64,${result.qr_certificate}`;
            
            alert(`✅ ${result.message}`);
            
            // Rafraîchir
            loadProducts();
            updateBalance();
            updateBlockchainInfo();
            loadTransactions();
            loadUsers();
        } else {
            alert(`❌ ${result.error}`);
        }
    } catch (error) {
        console.error('Erreur achat:', error);
        alert('❌ Erreur lors de l\'achat');
    }
}

// Miner un bloc - Version améliorée
async function mineBlock() {
    if (!currentWallet) {
        alert('⚠️ Veuillez vous connecter');
        return;
    }
    
    // Afficher un message de chargement
    const mineBtn = document.getElementById('mineBtn');
    const originalText = mineBtn.textContent;
    mineBtn.textContent = '⏳ Minage en cours...';
    mineBtn.disabled = true;
    
    try {
        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                miner_address: currentWallet
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Afficher les détails des transactions minées
            alert(`✅ ${result.message}`);
            
            // Rafraîchir l'affichage
            updateBalance();
            updateBlockchainInfo();
            loadTransactions();
            loadUsers();
        } else {
            alert(`ℹ️ ${result.error}`);
        }
    } catch (error) {
        console.error('Erreur minage:', error);
        alert('❌ Erreur lors du minage');
    } finally {
        // Restaurer le bouton
        mineBtn.textContent = originalText;
        mineBtn.disabled = false;
    }
}

// Mettre à jour les infos blockchain
async function updateBlockchainInfo() {
    try {
        const response = await fetch('/api/blockchain/info');
        const info = await response.json();
        
        document.getElementById('blockCount').textContent = info.length;
        document.getElementById('pendingCount').textContent = info.pending_transactions;
        document.getElementById('difficulty').textContent = info.difficulty;
        
        const validitySpan = document.getElementById('validity');
        if (info.is_valid) {
            validitySpan.innerHTML = '✅ Valide';
            validitySpan.style.color = '#4CAF50';
        } else {
            validitySpan.innerHTML = '❌ Invalide';
            validitySpan.style.color = '#f44336';
        }
    } catch (error) {
        console.error('Erreur info blockchain:', error);
    }
}

// Charger l'historique des transactions
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        
        const container = document.getElementById('transactionsList');
        
        if (transactions.length === 0) {
            container.innerHTML = '<div class="loading">📜 Aucune transaction pour le moment</div>';
            return;
        }
        
        container.innerHTML = transactions.map(tx => {
            const isReward = tx.type === 'reward';
            const isInitial = tx.type === 'initial_balance';
            const fromName = tx.from_name || tx.from || 'SYSTEM';
            const toName = tx.to_name || tx.to;
            
            let icon = '💸';
            let color = '#4CAF50';
            
            if (isReward) {
                icon = '🎁';
                color = '#ff9800';
            } else if (isInitial) {
                icon = '🎉';
                color = '#2196F3';
            }
            
            return `
                <div class="transaction-item" style="border-left-color: ${color}">
                    <strong>🔷 Bloc #${tx.block_index}</strong><br>
                    ${icon} ${fromName} → ${toName}: ${tx.amount} tokens
                    ${tx.product_name ? `<br>📦 ${tx.product_name}` : ''}
                    ${tx.note ? `<br>💬 ${tx.note}` : ''}
                    <br><span style="font-size: 0.7rem; color: #999;">${new Date(tx.timestamp * 1000).toLocaleString()}</span>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erreur chargement transactions:', error);
    }
}

// Charger la liste des utilisateurs
async function loadUsers() {
    try {
        const response = await fetch('/api/wallet/list');
        const users = await response.json();
        
        const container = document.getElementById('usersList');
        
        if (users.length === 0) {
            container.innerHTML = '<div class="loading">👤 Aucun utilisateur inscrit</div>';
            return;
        }
        
        container.innerHTML = users.map(user => `
            <div class="user-item">
                <span class="user-name">👤 ${escapeHtml(user.name)}</span>
                <span class="user-balance">💰 ${user.balance} tokens</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erreur chargement utilisateurs:', error);
    }
}
// Mettre à jour le tableau de bord
async function updateDashboard() {
    try {
        // Récupérer les transactions
        const txResponse = await fetch('/api/transactions');
        const transactions = await txResponse.json();
        
        // Récupérer les utilisateurs
        const usersResponse = await fetch('/api/wallet/list');
        const users = await usersResponse.json();
        
        // Récupérer les produits
        const productsResponse = await fetch('/api/products');
        const products = await productsResponse.json();
        
        // Récupérer les infos blockchain
        const blockchainResponse = await fetch('/api/blockchain/info');
        const blockchain = await blockchainResponse.json();
        
        // Mettre à jour les chiffres
        const totalTxElem = document.getElementById('totalTransactions');
        const totalUsersElem = document.getElementById('totalUsers');
        const totalProductsElem = document.getElementById('totalProducts');
        const totalBlocksElem = document.getElementById('totalBlocks');
        
        if (totalTxElem) totalTxElem.textContent = transactions.length;
        if (totalUsersElem) totalUsersElem.textContent = users.length;
        if (totalProductsElem) totalProductsElem.textContent = products.length;
        if (totalBlocksElem) totalBlocksElem.textContent = blockchain.length;
        
        // Top 5 des plus riches
        const topUsers = [...users].sort((a, b) => b.balance - a.balance).slice(0, 5);
        const topUsersList = document.getElementById('topUsersList');
        
        if (topUsersList) {
            if (topUsers.length === 0) {
                topUsersList.innerHTML = '<div class="loading">Aucun utilisateur pour le moment</div>';
            } else {
                topUsersList.innerHTML = topUsers.map((user, index) => {
                    let medal = '';
                    if (index === 0) medal = '🥇 ';
                    else if (index === 1) medal = '🥈 ';
                    else if (index === 2) medal = '🥉 ';
                    else medal = `${index + 1}. `;
                    return `<div class="user-item"><span>${medal} ${user.name}</span><span class="user-balance">💰 ${user.balance} tokens</span></div>`;
                }).join('');
            }
        }
        
    } catch (error) {
        console.error('Erreur dashboard:', error);
    }
}
// Ajouter un produit
async function addProduct(event) {
    event.preventDefault();
    
    if (!currentWallet) {
        alert('⚠️ Veuillez vous connecter');
        return;
    }
    
    const product = {
        name: document.getElementById('productName').value,
        price: parseFloat(document.getElementById('productPrice').value),
        description: document.getElementById('productDescription').value,
        seller_address: currentWallet,
        stock: parseInt(document.getElementById('productStock').value) || 1
    };
    
    if (!product.name || isNaN(product.price) || product.price <= 0) {
        alert('Veuillez remplir tous les champs correctement');
        return;
    }
    
    try {
        const response = await fetch('/api/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(product)
        });
        
        if (response.ok) {
            alert(`✅ Produit "${product.name}" ajouté avec succès !`);
            document.getElementById('addProductForm').reset();
            loadProducts();
        } else {
            const error = await response.json();
            alert(`❌ Erreur: ${error.error}`);
        }
    } catch (error) {
        console.error('Erreur ajout produit:', error);
        alert('❌ Erreur lors de l\'ajout');
    }
}

// Fermer les QR codes
function closeQR() {
    document.getElementById('qrSection').style.display = 'none';
}

// Fonction utilitaire pour échapper le HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
// Afficher une notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'warning') icon = '⚠️';
    if (type === 'error') icon = '❌';
    
    notification.innerHTML = `
        <span style="font-size: 1.5rem;">${icon}</span>
        <span style="flex: 1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">✖</button>
    `;
    
    document.body.appendChild(notification);
    
    // Disparaît après 5 secondes
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Surcharger alert() avec notifications
const originalAlert = window.alert;
window.alert = function(message) {
    showNotification(message, 'info');
    originalAlert(message);
};