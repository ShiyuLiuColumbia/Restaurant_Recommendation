import json
from boto3 import resource

def lambda_handler(event, context):

#=========DynamonDB part=====================#
    user_name = event['comment_info']['user_name']
    dynamodb_resource = resource('dynamodb')
    table = dynamodb_resource.Table('user')
    table_restaurant = dynamodb_resource.Table('restaurant')
    dbResponse = table.get_item(Key={"user_name": user_name})


    order_history_list = dbResponse.get('Item')['order_history'] 
    tag = dbResponse.get('Item')['tag']
    categories = table_restaurant.get_item(Key={"business_name": event['comment_info']['restaurant_name']})['Item']['categories']

    # if this category has already in this user's tags, we will add its score by (grade-3), otherwise we create a new tag. 
    for category in categories:
        if tag.get(category) is not None:
            tag[category] = tag[category] + int(event['comment_info']['score']) - 3
        else:
            tag[category] = int(event['comment_info']['score']) - 3

    #search for the match order_info in order_history, add comment and score in it.
    for i , order_info in enumerate(order_history_list):

        if order_info['restaurant_name'] == event['comment_info']['restaurant_name'] and (order_info['dining_date']+' '+order_info['dining_time']) == event['comment_info']['dining_time']:
            order_history_list.pop(i)
            order_info['score'] = event['comment_info']['score']
            order_info['comment'] = event['comment_info']['review']
            order_history_list.append(order_info)


            response = table.update_item(
            Key = {
                "user_name": user_name
            },
            UpdateExpression = "set order_history = :val,tag = :val2", 
            ExpressionAttributeValues = {
                ':val': order_history_list,
                ':val2': tag
            },
            ReturnValues="UPDATED_NEW"
            )
    return {
                'statusCode': 200,
                'body': order_history_list
            }
