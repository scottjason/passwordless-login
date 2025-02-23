import os
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.otp_service import OTPService
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

base_api_url = os.getenv("BASE_API_URL")
if not base_api_url:
    raise ValueError("BASE_API_URL environment variable is not set")

origins = [
    base_api_url,
]

app = FastAPI()
otp_service = OTPService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class OTPRequest(BaseModel):
    user_id: str
    user_email: str


@app.post("/generate-otp")
def generate_otp(request: OTPRequest):
    """Endpoint to generate and return an OTP for the given user."""
    nonce = otp_service.generate_otp(request.user_id, request.user_email)
    response = JSONResponse(
        content={"message": "OTP generated and sent to email", "nonce": nonce}
    )
    return response


@app.post("/validate-otp")
def validate_otp(user_id: str, otp: str, nonce: str):
    """Endpoint to validate the OTP for a given user."""
    if otp_service.validate_otp(user_id, otp, nonce):
        response = JSONResponse(content={"message": "OTP is valid"})
    else:
        response = JSONResponse(content={"detail": "Invalid OTP"}, status_code=400)
    return response
