import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
""" --- Recommendation --- """
def recommendate(user_name):
    dynamodb_resource = boto3.resource('dynamodb')
    table = dynamodb_resource.Table('user')
    response = table.get_item(Key={
        "user_name" : user_name
    })
    if response.get("Item") is None:
        return []
    tags = response["Item"]["tag"]
    sortedTags =  sorted(tags.items(), key=lambda x:-x[1])[:3]
    size = 6
    response = []
    nameSet = set()
    for tag in sortedTags:
        restaurantTable = dynamodb_resource.Table('restaurant')
        filtering_exp = Attr('categories').contains(tag[0]) & Attr('rating').gt("4.2")
        findRestaurant = restaurantTable.scan(FilterExpression=filtering_exp)["Items"][:size]
        for restaurant in findRestaurant:
            if restaurant["business_name"] not in nameSet:
                nameSet.add(restaurant["business_name"])
                response.append(restaurant)
        size -= 2;
    return response

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': recommendate(event["user_name"])
    }
