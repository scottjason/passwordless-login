import os
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from services.otp_service import OTPService
from fastapi.middleware.cors import CORSMiddleware
from services.encryption_service import EncryptionService

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("uvicorn")

base_api_url = os.getenv("BASE_API_URL")
if not base_api_url:
    raise ValueError("BASE_API_URL environment variable is not set")

origins = [
    base_api_url,
]

app = FastAPI()

otp_service: OTPService = None
encryption_service: EncryptionService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global otp_service, encryption_service
    otp_service = OTPService()
    encryption_service = EncryptionService()
    logger.info("Services initialized.")
    yield
    logger.info("App is shutting down.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow the origins of your front-end
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


class OTPRequest(BaseModel):
    user_email: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        logger.info("Health check request received")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/generate-otp")
def generate_otp(request: OTPRequest):
    """Endpoint to generate and return an OTP for the given user."""
    try:
        encrypted_email = encryption_service.encrypt_email(request.user_email)
        nonce = otp_service.generate_otp(request.user_email, encrypted_email)
        response = JSONResponse(
            status_code=201,
            content={
                "message": "OTP generated and sent successfully",
                "nonce": nonce,
                "encrypted_email": encrypted_email,
            },
        )
        return response
    except Exception as e:
        logger.error(f"Error generating OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/validate-otp")
def validate_otp(user_email: str, otp: str, nonce: str):
    """Endpoint to validate the OTP for a given user."""
    try:
        # Decrypt the email before validating the OTP
        decrypted_email = encryption_service.decrypt_email(user_email)

        if otp_service.validate_otp(decrypted_email, otp, nonce):
            response = JSONResponse(content={"message": "OTP is valid"})
        else:
            response = JSONResponse(content={"detail": "Invalid OTP"}, status_code=400)
            logger.warning(f"Invalid OTP for user {decrypted_email}")

        logger.debug(f"Response Headers for /validate-otp: {response.headers}")
        return response
    except Exception as e:
        logger.error(f"Error validating OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
