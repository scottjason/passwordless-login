import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class EncryptionService:
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY must be set in .env")

        # Should be 32 bytes for AES or 44 for Fernet
        if len(self.encryption_key) == 32:
            self.cipher_type = "AES"
            self.encryption_key = self.encryption_key.encode()
        elif len(self.encryption_key) == 44:
            self.cipher_type = "Fernet"
            self.encryption_key = self.encryption_key.encode()
        else:
            raise ValueError(
                "ENCRYPTION_KEY must be either 32 bytes (AES) or 44 bytes (Fernet)"
            )

        # Initialize the encryption method
        if self.cipher_type == "Fernet":
            self.cipher = Fernet(self.encryption_key)  # Fernet initialization
        elif self.cipher_type == "AES":
            self.cipher = None  # AES initialization happens in the encrypt_email method

    def encrypt_email(self, user_email: str) -> str:
        """Encrypts the user's email address using AES-256 or Fernet"""
        if self.cipher_type == "Fernet":
            # Use Fernet encryption if the key is 44 bytes
            encrypted_email = self.cipher.encrypt(user_email.encode())
            return encrypted_email.decode()

        elif self.cipher_type == "AES":
            # Generate a random 16-byte IV (Initialization Vector)
            iv = os.urandom(16)

            # Create AES cipher using the encryption key
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            # Pad the email to be a multiple of 16 bytes
            pad_len = 16 - (len(user_email) % 16)
            padded_email = user_email.encode() + bytes([pad_len]) * pad_len

            encrypted_email = encryptor.update(padded_email) + encryptor.finalize()

            # Return IV + encrypted email (so we can use the IV for decryption)
            return iv + encrypted_email

        else:
            raise ValueError("Unsupported encryption method")

    def decrypt_email(self, encrypted_email: str) -> str:
        """Decrypts the user's email address using AES-256 or Fernet"""
        if self.cipher_type == "Fernet":
            # Use Fernet decryption if the key is 44 bytes
            encrypted_email = (
                encrypted_email.encode()
            )  # Convert to bytes before decrypting
            decrypted_email = self.cipher.decrypt(encrypted_email)
            return decrypted_email.decode()

        elif self.cipher_type == "AES":
            # Extract the IV (first 16 bytes) from the encrypted data
            iv = encrypted_email[:16]
            cipher_data = encrypted_email[16:]

            # Create AES cipher using the encryption key
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            # Decrypt the email
            decrypted_email = decryptor.update(cipher_data) + decryptor.finalize()

            # Remove padding
            pad_len = decrypted_email[-1]
            return decrypted_email[:-pad_len].decode()

        else:
            raise ValueError("Unsupported decryption method")
