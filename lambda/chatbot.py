import json
import boto3

client = boto3.client('lex-runtime')


def lambda_handler(event, context):
    # # TODO implement
    # if event["input"] == "hello":
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps('Hello from Lambda!')
    #     }
    
    # elif event["input"] == "can you hear me":
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps('of course')
    #     }

    # elif event["input"] == "are you there":
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps('always')
    #     }
    # else:
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps("Sorry, I do not understand you")
    #     }
        
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