import string
import random

import requests


import qrcode
from tempfile import NamedTemporaryFile

from passlib.context import CryptContext

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def generate_qr_code(url: str) -> str:
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=8,
    )
    # Add the URL to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create a temporary file to save the QR code image
    with NamedTemporaryFile(delete=False) as tmp_file:
        # Generate the QR code image
        qr.make_image().save(tmp_file.name)
        return tmp_file.name


def get_ip_address():
    try:
        url = 'https://api.ipify.org'
        response = requests.get(url)
        response.raise_for_status()

        ip_address = response.text
        return ip_address
    except requests.RequestException as e:
        print(f"Error fetching IP information: {e}")
        return None


def get_ip_info(ip_address: str) -> dict:
    ip_info = {}
    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/")
        response.raise_for_status()
        if response.status_code == 200:
            ip_info = response.json()
    except requests.RequestException as e:
        print(f"Error fetching IP information: {e}")
    return ip_info
