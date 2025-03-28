# banjos_restaurant\app\core\database.py
import boto3
from app.core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, DYNAMODB_TABLE

class DynamoDB:
    def __init__(self):
        self.client = boto3.client(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.table_name = DYNAMODB_TABLE

    async def put_item(self, item):
        """Insert an item into DynamoDB."""
        response = self.client.put_item(
            TableName=self.table_name,
            Item=item
        )
        return response

    async def get_item(self, key):
        """Retrieve an item from DynamoDB using its primary key."""
        response = self.client.get_item(
            TableName=self.table_name,
            Key=key
        )
        return response.get('Item')

    async def update_item(self, key, update_expression, expression_attribute_names, expression_attribute_values):
        """Update an item in DynamoDB."""
        response = self.client.update_item(
            TableName=self.table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        return response

    async def delete_item(self, key):
        """Delete an item from DynamoDB."""
        response = self.client.delete_item(
            TableName=self.table_name,
            Key=key
        )
        return response

    async def scan(self):
        """Scan the entire DynamoDB table."""
        response = self.client.scan(
            TableName=self.table_name
        )
        return response.get('Items', [])

# Create a global DynamoDB instance
dynamodb = DynamoDB()