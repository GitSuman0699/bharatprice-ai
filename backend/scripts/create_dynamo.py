import boto3
import time

def create_table():
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    
    table_name = 'BharatPriceMarketData'
    
    try:
        print(f"Checking if {table_name} exists...")
        dynamodb.describe_table(TableName=table_name)
        print(f"Table {table_name} already exists.")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Creating table {table_name} (On-Demand Capacity)...")
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'product_id', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'region', 'KeyType': 'RANGE'}      # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'product_id', 'AttributeType': 'S'},
                {'AttributeName': 'region', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'  # 100% Serverless, $0 idle cost
        )
        
        # Wait for table to be active before enabling TTL
        print("Waiting for table to become ACTIVE (usually takes ~10 seconds)...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print(f"Table {table_name} created successfully!")
        
        # Enable TTL on the 'expiration_time' attribute
        print("Enabling TTL on 'expiration_time'...")
        dynamodb.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expiration_time'
            }
        )
        print("TTL enabled successfully. DynamoDB Cache is ready for action!")

if __name__ == "__main__":
    create_table()
