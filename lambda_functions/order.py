from __future__ import print_function
import boto3
import json
import argparse
import pprint
from botocore.vendored import requests #lambda do not have requests module
import sys
import urllib
import ast
import time
from boto3 import resource






def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()







def lambda_handler(event, context):

#=============Get reservation info from sqs ====
    # Create SQS client
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-east-1.amazonaws.com/660749920408/finalPJ'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)
#==============================================



    # reservation message got from chatbot
    DEFAULT_TERM = ast.literal_eval(message[unicode('Body')])['Cuisine']#message is a dict, message[unicode('Body')] is a String of dict.
    DEFAULT_LOCATION = ast.literal_eval(message[unicode('Body')])['Location']
    user_phone_number = ast.literal_eval(message[unicode('Body')])['Phone_Number']
    dining_date = ast.literal_eval(message[unicode('Body')])['Dining_Date']
    dining_time = ast.literal_eval(message[unicode('Body')])['Dining_Time']
    number_people = ast.literal_eval(message[unicode('Body')])['Num_People']
    #restaurant info got after user clicking 'order it' button
    restaurant_name = event['business_name']
    restaurant_location = event['address']
    restaurant_url = event['url']
    img = event['img']
    user_name = event['user_name']
    # user_name = "Yi zhi zhu"



#=========DynamonDB part=====================#

    dynamodb_resource = resource('dynamodb')
    table = dynamodb_resource.Table('user')
    dbResponse = table.get_item(Key={"user_name": user_name})
    reserve_info = {
        'order_time':time.asctime( time.localtime(time.time()) ),
        'restaurant_name': restaurant_name,
        'location':restaurant_location,
        'url':restaurant_url,
        'dining_date': dining_date,
        'dining_time': dining_time,
        'number_people': number_people,
        'search_for': DEFAULT_TERM,
        'user_phone_number': user_phone_number,
        'img': img

        }
    #If we do not have this user in our database before, we will creative the initial info for him, including tag and order_history
    if dbResponse.get('Item') is  None:
        response = table.put_item(Item={
            'user_name': user_name,
            'tag':{},
            'order_history':[reserve_info,]
            
        })

    #if we do have this user in database before , we will record this order without comments in database
    else:
        dbResponse['Item']['order_history'].append(reserve_info)
        response = table.update_item(
        Key = {
            "user_name": user_name
        },
        UpdateExpression = "set order_history = :val",
        ExpressionAttributeValues = {
            ':val': dbResponse['Item']['order_history']
        },
        ReturnValues="UPDATED_NEW"
        )
        
#============================================#



#=========send message from aws SMS============#
    sendMessage = 'Here is the {} restaurant we recommend for {} people, for {} at {}: Name: {}; Location: {}; Yelp_Link: {}.'.format(DEFAULT_TERM, number_people, dining_date, dining_time, restaurant_name, restaurant_location , restaurant_url)
 
    print('sent message: '+ sendMessage)

    
    sns = boto3.client('sns')
    # Create SQS client
    sns.publish(
    PhoneNumber = '+1'+user_phone_number,
    Message = sendMessage    )

#==============================================#


    return {
        'statusCode': 200,
        'body': json.dumps('SUCCESS! THE ORDER PART HAS NO ERROR')
        
    }
