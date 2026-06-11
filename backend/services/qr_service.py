"""
qr_service.py - Génération de QR codes (version légère)
"""

import qrcode
import json
from io import BytesIO
import base64

class QRService:
    @staticmethod
    def generate_payment_qr(transaction_data):
        """
        Génère un QR code pour le paiement
        """
        qr_data = {
            'type': 'payment',
            'to': transaction_data['to'],
            'amount': transaction_data['amount'],
            'product_id': transaction_data.get('product_id'),
            'timestamp': transaction_data.get('timestamp')
        }
        
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(json.dumps(qr_data, indent=2))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def generate_certificate_qr(product, transaction_hash):
        """
        Génère un QR code de certification pour le produit
        """
        qr_data = {
            'type': 'certificate',
            'product_name': product.name,
            'product_id': product.id,
            'seller': product.seller_address,
            'transaction_hash': transaction_hash,
            'timestamp': None
        }
        
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(json.dumps(qr_data, indent=2))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str