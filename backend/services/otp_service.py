import os
import random
import hashlib
import time
import redis
import sendgrid
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To
import json

load_dotenv()


class OTPService:
    def __init__(self):
        self.from_email = os.getenv("FROM_EMAIL")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.redis_host = os.getenv("REDIS_HOST")
        self.redis_port = int(os.getenv("REDIS_PORT"))
        self.redis_username = os.getenv("REDIS_USERNAME")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.use_ssl = os.getenv("REDIS_USE_SSL").lower() == "true"
        self.sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY must be set in .env")

        # Determine encryption method (AES or Fernet) based on the length of the encryption key
        if len(self.encryption_key) == 32:  # AES 256
            self.cipher_type = "AES"
            self.encryption_key = self.encryption_key.encode()  # Ensure it is in bytes
        elif len(self.encryption_key) == 44:  # Fernet
            self.cipher_type = "Fernet"
            self.encryption_key = self.encryption_key.encode()  # Ensure it is in bytes
        else:
            raise ValueError(
                "ENCRYPTION_KEY must be either 32 bytes (AES) or 44 bytes (Fernet)"
            )

        if self.cipher_type == "Fernet":
            self.cipher = Fernet(self.encryption_key)  # Fernet initialization
        elif self.cipher_type == "AES":
            # Handle AES encryption logic here (you can use libraries such as PyCryptodome)
            raise NotImplementedError("AES encryption logic is not yet implemented.")

        if not self.redis_host or not self.redis_password:
            raise ValueError("❌ Redis host and password must be set in the .env file!")

        # Configure Redis connection
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            username=self.redis_username,
            password=self.redis_password,
            decode_responses=True,
            ssl=self.use_ssl,
        )

        print("✅ Connected to Redis at:", self.redis_host)

    def send_otp_to_email(self, user_email: str, otp: str):
        """Send OTP to the user's email using SendGrid."""
        subject = "Your One-Time Password (OTP)"
        content = f"Your OTP is: {otp}. It will expire in 5 minutes."
        from_email = Email(self.from_email)
        to_email = To(user_email)
        email = Mail(from_email, to_email, subject, content)

        try:
            response = self.sg.send(email)
            if response.status_code == 202:
                print(f"Email sent to {user_email}.")
            else:
                print(
                    f"Failed to send email: {response.status_code} - {response.body.decode('utf-8')}"
                )
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def generate_otp(self, user_email: str, user_encrypted_email: str) -> str:
        """Generates a 6-digit OTP, includes nonce, and stores it in Redis for 5 minutes."""
        otp = str(random.randint(100000, 999999))

        # Generate a nonce to ensure OTP is valid for one-time use
        nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[
            :16
        ]  # Using timestamp-based hash for uniqueness

        # Use otp:{user_encrypted_email}:{nonce} to create a unique key for OTP in Redis
        otp_key = f"otp:{user_encrypted_email}:{nonce}"

        # # Store OTP with 5-minute expiration in Redis (Store OTP and encrypted email as JSON)
        otp_data = json.dumps(
            {
                "otp": otp,
                "user_encrypted_email": user_encrypted_email,
            }
        )
        self.redis_client.setex(otp_key, 300, otp_data)  # TTL = 300 seconds (5 minutes)
        self.send_otp_to_email(user_email, otp)  # Send OTP to user's email

        # Return only the nonce to the client
        return nonce

    def validate_otp(self, otp: str, nonce: str, user_encrypted_email: str) -> bool:
        """Validates the OTP for a given user and nonce."""

        # Retrieve the stored OTP and encrypted email from Redis
        otp_key = f"otp:{user_encrypted_email}:{nonce}"
        stored_value = self.redis_client.get(otp_key)

        if stored_value:
            otp_data = json.loads(stored_value)
            stored_otp = otp_data.get("otp")
            stored_encrypted_email = otp_data.get("user_encrypted_email")

            # Check if the OTP in Redis matches the one provided by the user
            if stored_otp == otp and stored_encrypted_email == user_encrypted_email:
                # If valid, delete the OTP from Redis after successful validation to prevent reuse
                self.redis_client.delete(otp_key)
                return True

        # If the OTP is invalid or expired, return False
        return False
