from fastapi import APIRouter, Depends
from app.core.database import mongodb
from app.models.order import Order

router = APIRouter()

async def get_database():
    """Ensure the database is connected before returning the database instance."""
    if not mongodb.database:
        await mongodb.connect()
    return mongodb.get_database()

@router.post("/place")
async def place_order(order: Order, db=Depends(get_database)):
    """Place a new order."""
    orders_collection = db["orders"]
    result = await orders_collection.insert_one(order.dict())
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_orders(db=Depends(get_database)):
    """Retrieve all orders."""
    orders_collection = db["orders"]
    orders = await orders_collection.find().to_list(100)
    return orders