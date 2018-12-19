import time
import os
import logging
import dateutil.parser
import math
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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
    # location = try_ex(lambda: slots['Location'])
    # checkin_date = try_ex(lambda: slots['CheckInDate'])
    # nights = safe_int(try_ex(lambda: slots['Nights']))
    # room_type = try_ex(lambda: slots['RoomType'])

    # if location and not isvalid_city(location):
    #     return build_validation_result(
    #         False,
    #         'Location',
    #         'We currently do not support {} as a valid destination.  Can you try a different city?'.format(location)
    #     )

    # if checkin_date:
    #     if not isvalid_date(checkin_date):
    #         return build_validation_result(False, 'CheckInDate', 'I did not understand your check in date.  When would you like to check in?')
    #     if datetime.datetime.strptime(checkin_date, '%Y-%m-%d').date() <= datetime.date.today():
    #         return build_validation_result(False, 'CheckInDate', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    # if nights is not None and (nights < 1 or nights > 30):
    #     return build_validation_result(
    #         False,
    #         'Nights',
    #         'You can make a reservations for from one to thirty nights.  How many nights would you like to stay for?'
    #     )

    # if room_type and not isvalid_room_type(room_type):
    #     return build_validation_result(False, 'RoomType', 'I did not recognize that room type.  Would you like to stay in a queen, king, or deluxe room?')

    # return {'isValid': True}



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
    # location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    # checkin_date = try_ex(lambda: intent_request['currentIntent']['slots']['checkin_date'])
    # nights = safe_int(try_ex(lambda: intent_request['currentIntent']['slots']['Nights']))



    # # Load confirmation history and track the current reservation.
    # reservation = json.dumps({
    #     'ReservationType': 'Hotel',
    #     'Location': location,
    #     'RoomType': room_type,
    #     'CheckInDate': checkin_date,
    #     'Nights': nights
    # })

    # session_attributes['currentReservation'] = reservation

    # if intent_request['invocationSource'] == 'DialogCodeHook':
    #     # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
    #     validation_result = validate_hotel(intent_request['currentIntent']['slots'])
    #     if not validation_result['isValid']:
    #         slots = intent_request['currentIntent']['slots']
    #         slots[validation_result['violatedSlot']] = None

    #         return elicit_slot(
    #             session_attributes,
    #             intent_request['currentIntent']['name'],
    #             slots,
    #             validation_result['violatedSlot'],
    #             validation_result['message']
    #         )

    #     # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
    #     # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.
    #     if location and checkin_date and nights and room_type:
    #         # The price of the hotel has yet to be confirmed.
    #         price = generate_hotel_price(location, nights, room_type)
    #         session_attributes['currentReservationPrice'] = price
    #     else:
    #         try_ex(lambda: session_attributes.pop('currentReservationPrice'))

    #     session_attributes['currentReservation'] = reservation
    #     return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # # Booking the hotel.  In a real application, this would likely involve a call to a backend service.
    # logger.debug('bookHotel under={}'.format(reservation))

    # try_ex(lambda: session_attributes.pop('currentReservationPrice'))
    # try_ex(lambda: session_attributes.pop('currentReservation'))
    # session_attributes['lastConfirmedReservation'] = reservation

    # return close(
    #     session_attributes,
    #     'Fulfilled',
    #     {
    #         'contentType': 'PlainText',
    #         'content': 'Thanks, I have placed your reservation.   Please let me know if you would like to book a car '
    #                    'rental, or another hotel.'
    #     }
    # )


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


        # Create SQS client
        sqs = boto3.client('sqs')

        queue_url = 'https://sqs.us-east-1.amazonaws.com/660749920408/cc_hw2q'

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
                'content': 'Thanks, I have placed your reservation. Expect my recommendations shortly! Have a good day.'
            }
        )



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
