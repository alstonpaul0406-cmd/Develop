import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TodosTable')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/todos':
            return get_todos()
        elif http_method == 'POST' and path == '/todos':
            return create_todo(json.loads(event['body']))
        elif http_method == 'DELETE' and '/todos/' in path:
            todo_id = path.split('/')[-1]
            return delete_todo(todo_id)
        else:
            return response(400, {'error': 'Invalid request'})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_todos():
    result = table.scan()
    return response(200, {'todos': result['Items']})

def create_todo(body):
    todo_id = str(uuid.uuid4())
    item = {
        'id': todo_id,
        'title': body['title'],
        'completed': False,
        'createdAt': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return response(201, item)

def delete_todo(todo_id):
    table.delete_item(Key={'id': todo_id})
    return response(200, {'message': 'Todo deleted'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
