import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.otp_service import OTPService
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

origins = [
    os.getenv("BASE_API_URL"),
]

app = FastAPI()
otp_service = OTPService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only specified origins (localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Pydantic model for the request body
class OTPRequest(BaseModel):
    user_id: str
    user_email: str


@app.post("/generate-otp/")
def generate_otp(request: OTPRequest):
    """Endpoint to generate and return an OTP for the given user."""
    nonce = otp_service.generate_otp(request.user_id, request.user_email)
    return {"message": "OTP generated and sent to email", "nonce": nonce}


@app.post("/validate-otp/")
def validate_otp(user_id: str, otp: str, nonce: str):
    """Endpoint to validate the OTP for a given user."""
    if otp_service.validate_otp(user_id, otp, nonce):
        return {"message": "OTP is valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
