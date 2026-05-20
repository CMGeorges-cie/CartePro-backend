# app/services.py
import qrcode
from PIL import Image
import io
import os
import requests
from loguru import logger

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
            logo_size = int(img.size[0] * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception:
        logger.exception("Erreur lors de la génération du QR code")
        return None


def send_email(to_email: str, subject: str, body: str, from_email: str, api_key: str | None) -> None:
    """Envoie un email via l'API SendGrid. Logue seulement si la clé est absente (dev)."""
    if not api_key:
        logger.info(
            "Email non envoyé (SENDGRID_API_KEY absent) — à: {}, sujet: {}",
            to_email, subject,
        )
        return
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'personalizations': [{'to': [{'email': to_email}]}],
                'from': {'email': from_email, 'name': 'CartePro'},
                'subject': subject,
                'content': [{'type': 'text/plain', 'value': body}],
            },
            timeout=10,
        )
        response.raise_for_status()
        logger.info("Email envoyé à {}", to_email)
    except Exception:
        logger.exception("Erreur lors de l'envoi de l'email à {}", to_email)


def send_quote_notification_email(
    to_email: str,
    pro_name: str,
    requester_name: str,
    requester_email: str,
    requester_phone: str,
    message: str,
    api_key: str | None,
    from_email: str,
) -> None:
    subject = f"Nouvelle demande de soumission de {requester_name}"
    body = (
        f"Bonjour {pro_name},\n\n"
        f"Vous avez reçu une nouvelle demande de soumission via CartePro.\n\n"
        f"Nom : {requester_name}\n"
        f"Courriel : {requester_email}\n"
        f"Téléphone : {requester_phone or 'Non fourni'}\n"
        f"Message : {message or 'Aucun message'}\n\n"
        f"Connectez-vous à votre tableau de bord CartePro pour voir les détails.\n\n"
        f"— L'équipe CartePro"
    )
    send_email(to_email, subject, body, from_email, api_key)


def send_scan_followup_email(
    to_email: str,
    pro_name: str,
    scan_count: int,
    api_key: str | None,
    from_email: str,
) -> None:
    subject = f"Votre carte CartePro a été scannée {scan_count} fois cette semaine"
    body = (
        f"Bonjour {pro_name},\n\n"
        f"Votre carte de visite numérique CartePro a été consultée {scan_count} fois "
        f"au cours des 7 derniers jours.\n\n"
        f"Connectez-vous à votre tableau de bord pour voir les détails et relancer "
        f"vos prospects.\n\n"
        f"— L'équipe CartePro"
    )
    send_email(to_email, subject, body, from_email, api_key)
