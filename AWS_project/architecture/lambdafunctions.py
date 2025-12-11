import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ALSNIMITable')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/ALSNIMI':
            return get_ALSNIMI()
        elif http_method == 'POST' and path == '/ALSNIMI':
            return create_ALSNIMI(json.loads(event['body']))
        elif http_method == 'DELETE' and '/ALSNIMI/' in path:
            ALSNIMI_id = path.split('/')[-1]
            return delete_ALSNIMI(ALSNIMI_id)
        else:
            return response(400, {'error': 'Invalid request'})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_ALSNIMI():
    result = table.scan()
    return response(200, {'ALSNIMI': result['Items']})

def create_ALSNIMI(body):
    ALSNIMI_id = str(uuid.uuid4())
    item = {
        'id': ALSNIMI_id,
        'title': body['title'],
        'completed': False,
        'createdAt': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return response(201, item)

def delete_ALSNIMI(ALSNIMI_id):
    table.delete_item(Key={'id': ALSNIMI_id})
    return response(200, {'message': 'ALSNIMI deleted'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }