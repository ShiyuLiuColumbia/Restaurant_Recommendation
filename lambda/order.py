from __future__ import print_function
import boto3
import json
import argparse
import pprint
from botocore.vendored import requests #lambda do not have requests module
import sys
import urllib
import ast
from boto3 import resource

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= "ayzf13OTYgKpqlpN9g_Umo9PuHK-dg8CotRVLJzZrpse8vNrXdKegwFm-pFfChG1qDxnwgFhv0psye8Si_EgaROKYApGNF4k1pUULrrS-Er1x8Ftbn0j_3xU8qDnW3Yx"


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
SEARCH_LIMIT = 3




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


def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)

def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(API_KEY, term, location)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return None

    business_id = businesses[0]['id']

    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(
            len(businesses), business_id))
    response = get_business(API_KEY, business_id)

    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)
    return response





def lambda_handler(event, context):
    # Create SQS client
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-east-1.amazonaws.com/660749920408/cc_hw2q'

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




    # Defaults for our simple example.
    DEFAULT_TERM = ast.literal_eval(message[unicode('Body')])['Cuisine']#message is a dict, message[unicode('Body')] is a String of dict.
    DEFAULT_LOCATION = ast.literal_eval(message[unicode('Body')])['Location']
    user_phone_number = ast.literal_eval(message[unicode('Body')])['Phone_Number']
    dining_date = ast.literal_eval(message[unicode('Body')])['Dining_Date']
    dining_time = ast.literal_eval(message[unicode('Body')])['Dining_Time']
    number_people = ast.literal_eval(message[unicode('Body')])['Num_People']



    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        #query_result is the restaurant result from yelp api
        query_result = query_api(input_values.term, input_values.location)
        print('queryMessage from sqs:')
        pprint.pprint(query_result, indent=2)

    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

    restaurant_id = query_result[unicode('id')]
    restaurant_name = query_result[unicode('name')]
    restaurant_phone_num = query_result[unicode('display_phone')]
    restaurant_location = query_result[unicode('location')][unicode('display_address')][0]+unicode(', ')+query_result[unicode('location')][unicode('display_address')][1]

    restaurant_url = query_result[unicode('url')]

#=========DynamonDB part=====================#

    dynamodb_resource = resource('dynamodb')
    table = dynamodb_resource.Table('restaurants')
    response = table.put_item(Item={
        'id':restaurant_id,
        'name':restaurant_name,
        'location':restaurant_location,
        'phone_number':restaurant_phone_num,
        'url':restaurant_url

        })
        
#============================================#



#=========send message from aws SMS============#
    sendMessage = 'Here is the {} restaurant we recommend for {} people, for {} at {}: Name: {}; Location: {}; Phone Number: {}; Yelp_Link: {}.'.format(DEFAULT_TERM, number_people, dining_date, dining_time, restaurant_name, restaurant_location,restaurant_phone_num , restaurant_url)
 
    print('sent message: '+ sendMessage)

    
    sns = boto3.client('sns')
    # Create SQS client
    sns.publish(
    PhoneNumber = '+1'+user_phone_number,
    # PhoneNumber = '+16462295280',
    Message = sendMessage    )

#==============================================#






    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
        
    }
