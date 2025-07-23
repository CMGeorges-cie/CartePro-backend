# app/services.py
import qrcode
from PIL import Image
import io
import os

DEFAULT_LOGO = 'app/static/logo.png'

def generate_qr_code_with_logo(url: str, logo_path: str = DEFAULT_LOGO) -> io.BytesIO:
    """Génère une image de QR code avec un logo au centre."""
    try:
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            # Calcul pour la taille du logo (environ 20% de l'image QR)
            logo_size = int(img.size[0] * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS) # ANTIALIAS est obsolète

            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None
