from services.otp_service import OTPService

# Instantiate OTPService
otp_service = OTPService()

# Test user ID (this could be any identifier, such as email or phone number)
user_id = "user123"


def test_generate_otp():
    """Test that OTP generation works and returns a 6-digit OTP and a nonce."""
    otp, nonce = otp_service.generate_otp(user_id)

    # Assert that the OTP is 6 digits long
    assert len(otp) == 6

    # Assert that the nonce is 16 characters long
    assert len(nonce) == 16


def test_validate_otp():
    """Test that OTP validation works and returns True for valid OTP."""
    otp, nonce = otp_service.generate_otp(user_id)

    # Simulate user submitting the OTP
    is_valid = otp_service.validate_otp(user_id, otp, nonce)

    # Assert that the OTP is valid
    assert is_valid == True
