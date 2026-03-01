import boto3
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("BharatPriceMarketData")
scan = table.scan()
with table.batch_writer() as batch:
    for each in scan.get("Items", []):
        batch.delete_item(Key={"product_id": each["product_id"], "region": each["region"]})
print("DynamoDB cache successfully flushed!")
