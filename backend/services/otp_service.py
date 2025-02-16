import os
import random
import redis
import time
import hashlib
import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content

load_dotenv()


class OTPService:
    def __init__(self):
        self.from_email = os.getenv("FROM_EMAIL")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        # Replace with your SendGrid API key
        # Connect to Redis (you can replace this with a more secure Redis configuration in production)
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)

    def send_otp_to_email(self, user_email: str, otp: str):
        """Send OTP to the user's email using SendGrid."""
        subject = "Your One-Time Password (OTP)"
        text = f"Your OTP is: {otp}. It will expire in 5 minutes."

        # Create a SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

        # Create the email
        from_email = Email(self.from_email)  # Replace with your sender email
        to_email = To(user_email)  # Recipient's email
        content = Content("text/plain", text)

        # Build the email
        mail = Mail(from_email, to_email, subject, content)

        # Send the email
        try:
            response = sg.send(mail)
            if (
                response.status_code == 202
            ):  # HTTP 202 means email accepted for delivery
                print(f"Email sent to {user_email}.")
            else:
                print(
                    f"Failed to send email: {response.status_code} - {response.body.decode('utf-8')}"
                )
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def generate_otp(self, user_id: str, user_email: str) -> str:
        """Generates a 6-digit OTP, includes nonce, and stores it in Redis for 5 minutes."""

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Generate a nonce to ensure OTP is valid for one-time use
        nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[
            :16
        ]  # Using timestamp-based hash for uniqueness

        # Generate a Redis key for storing OTP with nonce
        otp_key = f"otp:{user_id}:{nonce}"

        # Store OTP with 5-minute expiration in Redis
        self.redis_client.setex(otp_key, 300, otp)  # TTL = 300 seconds (5 minutes)
        self.send_otp_to_email(user_email, otp)
        # Return OTP and nonce to the frontend (nonce is used to validate OTP on the client)
        return nonce

    def validate_otp(self, user_id: str, otp: str, nonce: str) -> bool:
        """Validates the OTP for a given user and nonce."""

        # Construct the Redis key using user_id and nonce
        otp_key = f"otp:{user_id}:{nonce}"

        # Retrieve the stored OTP from Redis
        stored_otp = self.redis_client.get(otp_key)

        # Check if the OTP in Redis matches the one provided by the user
        if stored_otp and stored_otp.decode() == otp:
            # If valid, delete the OTP from Redis after successful validation to prevent reuse
            self.redis_client.delete(otp_key)
            return True

        # If the OTP is invalid or expired, return False
        return False
