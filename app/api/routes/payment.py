import stripe
import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import database
from app.services.franchise_service import get_request_by_id

# Load environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "your-stripe-secret-key")
router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/{request_id}/process/")
async def process_payment(request_id: str, amount: float):
    """Process a franchise fee payment."""
    # Ensure the franchise request exists
    franchise_request = await get_request_by_id(database, request_id)
    if not franchise_request:
        raise HTTPException(status_code=404, detail="Franchise request not found")

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert amount to cents
            currency="usd",
            payment_method_types=["card"]
        )
        return {"payment_intent": payment_intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
