from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    menu_item: str
    quantity: int

class Order(BaseModel):
    customer_name: str
    items: List[OrderItem]
    total_price: float
