#1.s3-read-only-policy 2.dynamonDB-full-access

import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    
    s3 = boto3.client('s3')   
    dynamodb_resource = boto3.resource('dynamodb')
    table = dynamodb_resource.Table('restaurant')
    s3Response = s3.get_object(Bucket='restaurant-for-you', Key='restaurants/scraped_yelp_results_for_New York.json')
    restaurants = json.loads(s3Response['Body'].read().decode('utf-8'))
    for restaurant in restaurants:
        restaurant['rating'] = str(restaurant['rating'])
        restaurant['categories'] = restaurant['categories'].lower().split(",")
        dbResponse = table.put_item(Item=restaurant)
    # temp = restaurants[0]
    # temp['rating'] = str(temp['rating'])
    # temp['categories'] = temp['categories'].lower().split(",")
    # dbResponse = table.put_item(Item=temp)
    print(restaurants[0])
    return {
        'statusCode': 200,
        'body': json.dumps(restaurants)
    }