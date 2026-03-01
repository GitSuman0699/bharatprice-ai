import boto3
import json
import os
from decimal import Decimal

# Helper to print decimals cleanly
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def view_dynamodb_data():
    try:
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
        table = dynamodb.Table('BharatPriceMarketData')
        
        print("Scanning DynamoDB 'BharatPriceMarketData' Table...\n")
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            print("The database is currently empty. Ask the chatbot for a price to fill it!")
            return

        print(f"Found {len(items)} cached records in DynamoDB:\n")
        
        for idx, item in enumerate(items, 1):
            product = item.get('product_id', 'Unknown')
            region = item.get('region', 'Unknown')
            price = item.get('mandi_price', 'N/A')
            expiry = item.get('expiration_time', 'N/A')
            
            print(f"Record #{idx}: {product.upper()} in {region.upper()}")
            print(f"------------------------------------------------")
            # Print the full JSON payload stored
            print(json.dumps(item, indent=2, cls=DecimalEncoder))
            print("\n")
            
    except Exception as e:
        print(f"Failed to read from DynamoDB: {e}")

if __name__ == "__main__":
    view_dynamodb_data()
