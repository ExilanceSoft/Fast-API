import uuid
from app.core.database import dynamodb
from app.schemas.online_order_link import OnlineOrderLinkCreate, OnlineOrderLinkUpdate
from fastapi import HTTPException

class OnlineOrderLinkService:

    @staticmethod
    async def get_all_links():
        """Retrieve all online order links."""
        try:
            items = await dynamodb.scan()
            links = []
            for item in items:
                if item.get("Home", {}).get("S") == "OnlineOrderLinks":  # Filter by partition key
                    link_data = {
                        "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                        "platform": item.get("platform", {}).get("S", ""),
                        "url": item.get("url", {}).get("S", ""),
                        "logo": item.get("logo", {}).get("S", ""),
                        "branch_id": item.get("branch_id", {}).get("S", "")
                    }
                    links.append(link_data)
            return links
        except Exception as e:
            print(f"Error retrieving links: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve links")

    @staticmethod
    async def create_link(link_data: OnlineOrderLinkCreate):
        """Create a new online order link."""
        try:
            # Generate a unique ID for the link
            link_id = str(uuid.uuid4())

            # Insert into DynamoDB
            item = {
                "Home": {"S": "OnlineOrderLinks"},  # Partition key
                "1": {"S": link_id},               # Sort key
                "platform": {"S": link_data.platform},
                "url": {"S": link_data.url},
                "logo": {"S": link_data.logo},
                "branch_id": {"S": link_data.branch_id}
            }

            await dynamodb.put_item(item)
            return link_id
        except Exception as e:
            print(f"Error creating link: {e}")
            raise HTTPException(status_code=500, detail="Failed to create link")

    @staticmethod
    async def get_link_by_id(link_id: str):
        """Retrieve an online order link by ID."""
        try:
            key = {
                "Home": {"S": "OnlineOrderLinks"},  # Partition key
                "1": {"S": link_id}                # Sort key
            }
            item = await dynamodb.get_item(key)
            if item:
                link_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "platform": item.get("platform", {}).get("S", ""),
                    "url": item.get("url", {}).get("S", ""),
                    "logo": item.get("logo", {}).get("S", ""),
                    "branch_id": item.get("branch_id", {}).get("S", "")
                }
                return link_data
            else:
                raise HTTPException(status_code=404, detail="Link not found")
        except Exception as e:
            print(f"Error retrieving link: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve link")

    @staticmethod
    async def update_link(link_id: str, update_data: OnlineOrderLinkUpdate):
        """Update an online order link."""
        try:
            key = {
                "Home": {"S": "OnlineOrderLinks"},  # Partition key
                "1": {"S": link_id}                # Sort key
            }

            update_expression = "SET "
            expression_attribute_names = {}
            expression_attribute_values = {}

            for field, value in update_data.dict().items():
                if value is not None:  # Only update fields that are provided
                    expression_attribute_names[f"#{field}"] = field
                    update_expression += f"#{field} = :{field}, "
                    expression_attribute_values[f":{field}"] = {"S": str(value)}

            update_expression = update_expression.rstrip(", ")

            await dynamodb.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_names=expression_attribute_names,
                expression_attribute_values=expression_attribute_values
            )
        except Exception as e:
            print(f"Error updating link: {e}")
            raise HTTPException(status_code=500, detail="Failed to update link")

    @staticmethod
    async def delete_link(link_id: str):
        """Delete an online order link."""
        try:
            key = {
                "Home": {"S": "OnlineOrderLinks"},  # Partition key
                "1": {"S": link_id}                # Sort key
            }
            await dynamodb.delete_item(key)
        except Exception as e:
            print(f"Error deleting link: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete link")