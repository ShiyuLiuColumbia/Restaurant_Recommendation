import time
import os
import logging
import dateutil.parser
import math
import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#Three basic helper function for lex
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---
def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n

def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def Greeting(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hi, there. How can I help you?'
        }
    )

def Thank_You(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You are welcome! See you next time!'
        }
    )

def validate_dining(slots):

    location = try_ex(lambda: slots['Location'])
    cuisine = try_ex(lambda: slots['Cuisine'])
    dining_date = (try_ex(lambda: slots['Dining_Date']))
    dining_time = (try_ex(lambda: slots['Dining_Time']))
    num_people = safe_int(try_ex(lambda: slots['Num_People']))
    phone_number = try_ex(lambda: slots['Phone_Number'])

    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(location)
        )


    if num_people is not None and (num_people < 1):
        return build_validation_result(
            False,
            'Num_People',
            'The minimum number of people must be 1. How many people do you have?'
        )





    if dining_date is not None:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'Dining_Data', 'I did not understand that, what date would you like to have the meal?')

    if dining_time is not None:
        if len(dining_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Dining_Time', 'It is not a valid time. Please type in a valid time')

        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Dining_Time', 'It is not a valid time. Please type in a valid time')

        if hour < 0 or hour > 24:
            # Outside of business hours
            return build_validation_result(False, 'Dining_Time', 'It is not a valid time. Please type in a valid time')

    if phone_number is not None and (len(phone_number)!= 10):
        return build_validation_result(
            False,
            'Phone_Number',
            'We only accept 10 digits phone number. Please type in correct phone number!'
        )

    return {'isValid': True}




""" --- Functions that control the bot's behavior --- """

def Dining_Suggestions(intent_request):

    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    dining_date =  try_ex(lambda: intent_request['currentIntent']['slots']['Dining_Date'])    
    dining_time = try_ex(lambda: intent_request['currentIntent']['slots']['Dining_Time'])
    num_people = safe_int(try_ex(lambda: intent_request['currentIntent']['slots']['Num_People']))
    phone_number = try_ex(lambda: intent_request['currentIntent']['slots']['Phone_Number'])

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_dining(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    elif intent_request['invocationSource'] == 'FulfillmentCodeHook':
        query_string = {"query": {"match": { "categories":{"query": intent_request['currentIntent']['slots']['Cuisine'], "operator":"or"}}}, "size": 6}
                #elastic search
        host = 'search-restaurants-buvleh232qlbvncw6b3dqxcfv4.us-east-1.es.amazonaws.com' # The domain with https:// and trailing slash. For example, https://my-test-domain.us-east-1.es.amazonaws.com/
        region = 'us-east-1' # For example, us-west-1
        
        service = 'es'
        # credentials = boto3.Session().get_credentials()
        # awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)
        awsauth = AWS4Auth('###', '###', region, service)
        es = Elasticsearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
        ) 
        response = es.search(index="restaurants", body= query_string)['hits']['hits']




        #dynamonDB
        dynamodb_resource = boto3.resource('dynamodb')
        table = dynamodb_resource.Table('restaurant')
        recommendation_restaurants = []
        for item in response:
            dbResponse = table.query(
            KeyConditionExpression=Key('business_name').eq(item['_source']['business_name'])
    )
            recommendation_restaurants.append(dbResponse['Items'][0])

        # Create SQS client
        sqs = boto3.client('sqs')

        queue_url = 'https://sqs.us-east-1.amazonaws.com/660749920408/finalPJ'

        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=1,
            MessageAttributes={

            },
            MessageBody=(
                
                json.dumps(intent_request['currentIntent']['slots'])
                
            )
        )

        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                # 'content': 'Thanks, I have placed your reservation. Expect my recommendations shortly! Have a good day.'
                'content': str(recommendation_restaurants)
            }
        )
        # return recommendation_restaurants



""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'Greeting':
        return Greeting(intent_request)
    elif intent_name == "Thankyou":
        return Thank_You(intent_request)
    elif intent_name == "DiningSuggestions":
        return Dining_Suggestions(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

        

""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
    

