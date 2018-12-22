import json
import boto3

client = boto3.client('lex-runtime')


def lambda_handler(event, context):

        
    response = client.post_text(
        botName='Dining_Concierge_Chatbot',
        botAlias='shiyuliu',
        userId='10',
        sessionAttributes={
            },
        requestAttributes={
            
        },
        inputText = event["messages"][0]["unstructured"]["text"]
    )

    return {
            'statusCode': 200,
            'body': json.dumps(response["message"])
        }