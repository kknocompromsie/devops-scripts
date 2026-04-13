
import json

def lambda_handler(event, context):
    name = event.get('name', 'DevOps Engineer')
    message = f"Hello {name}! Lambda is working!"
    print(f"Executed: {message}")
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message,
            'event': event
        })
    }
