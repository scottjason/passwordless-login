import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.otp_service import OTPService
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("uvicorn")

base_api_url = os.getenv("BASE_API_URL")
if not base_api_url:
    raise ValueError("BASE_API_URL environment variable is not set")

logging.debug(f"Base API URL: {base_api_url}")

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App is starting")
    yield
    logger.info("App is shutting down")


app.state.lifespan = lifespan


class OTPRequest(BaseModel):
    user_id: str
    user_email: str


@app.get("/")
def read_root():
    logger.info("Accessing the root endpoint")
    return {"message": "Accessing the root endpoint"}


@app.post("/generate-otp")
def generate_otp(request: OTPRequest):
    """Endpoint to generate and return an OTP for the given user."""
    try:
        nonce = otp_service.generate_otp(request.user_id, request.user_email)
        response = JSONResponse(
            content={"message": "OTP generated and sent to email", "nonce": nonce}
        )
        logger.debug(f"Response Headers for /generate-otp: {response.headers}")
        return response
    except Exception as e:
        logger.error(f"Error generating OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/validate-otp")
def validate_otp(user_id: str, otp: str, nonce: str):
    """Endpoint to validate the OTP for a given user."""
    try:
        if otp_service.validate_otp(user_id, otp, nonce):
            response = JSONResponse(content={"message": "OTP is valid"})
        else:
            response = JSONResponse(content={"detail": "Invalid OTP"}, status_code=400)
            logger.warning(f"Invalid OTP for user {user_id}")
        logger.debug(f"Response Headers for /validate-otp: {response.headers}")
        return response
    except Exception as e:
        logger.error(f"Error validating OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        logger.info("Health check request received")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
