from services.otp_service import OTPService

# Instantiate OTPService
otp_service = OTPService()

# Test user ID & Email
user_id = "user123"
user_email = "test@example.com"  # Add a valid email for OTP generation


def test_generate_otp():
    """Test that OTP generation works and returns a nonce."""
    nonce = otp_service.generate_otp(user_id, user_email)  # Fix: Add user_email

    # Assert that the nonce is 16 characters long
    assert isinstance(nonce, str)
    assert len(nonce) == 16


def test_validate_otp():
    """Test that OTP validation works and returns True for valid OTP."""
    nonce = otp_service.generate_otp(user_id, user_email)  # Fix: Add user_email

    # Simulate retrieving the OTP from Redis (this requires a real Redis connection)
    stored_otp = otp_service.redis_client.get(f"otp:{user_id}:{nonce}")

    # Ensure OTP exists before validating
    assert stored_otp is not None

    # Simulate user submitting the OTP
    is_valid = otp_service.validate_otp(user_id, stored_otp, nonce)

    # Assert that the OTP is valid
    assert is_valid == True
