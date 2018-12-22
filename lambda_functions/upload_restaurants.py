#==========1.s3-read-only-policy 2.dynamonDB-full-access


from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
def lambda_handler(event, context):

    #initialize dynamondb
    s3 = boto3.client('s3')   
    dynamodb_resource = boto3.resource('dynamodb')
    table = dynamodb_resource.Table('restaurant')

    #initialize elastic search
    host = 'search-restaurants-buvleh232qlbvncw6b3dqxcfv4.us-east-1.es.amazonaws.com' # The domain with https:// and trailing slash. For example, https://my-test-domain.us-east-1.es.amazonaws.com/
    region = 'us-east-1' # For example, us-west-1
    service = 'es'
    awsauth = AWS4Auth('#####', '###', region, service)
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    ) 

    #get crawled yelp data from s3, then insert them into dynamondb
    s3Response = s3.get_object(Bucket='restaurant-for-you', Key='restaurants/scraped_yelp_results_for_New York.json')
    restaurants = json.loads(s3Response['Body'].read().decode('utf-8'))
    for restaurant in restaurants:
        restaurant['review_count'] = str(restaurant['review_count'])
        restaurant['rating'] = str(restaurant['rating'])
        restaurant['categories'] = restaurant['categories'].lower().split(",")
        dbResponse = table.put_item(Item=restaurant)
        


        #elastic search
        #index (restaurant_name:restaurant_category) in elastic search.
        document = {'business_name': restaurant['business_name'], 'categories': restaurant['categories']}
        es.index(index="restaurants", doc_type="_doc", body=document)

    return {
        'statusCode': 200,
        'body': dbResponse
    }
