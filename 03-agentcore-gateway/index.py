import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
customer_table = dynamodb.Table('CustomerProfileTable')
warranty_table = dynamodb.Table('WarrantyTable')

def lambda_handler(event, context):
    operation = event.get('operation')
    
    if operation == 'get_customer_profile':
        return get_customer_profile(event)
    elif operation == 'check_warranty_status':
        return check_warranty_status(event)
    else:
        return {'error': 'Unknown operation'}

def get_customer_profile(event):
    customer_id = event.get('customer_id')
    email = event.get('email')
    phone = event.get('phone')
    
    try:
        if customer_id:
            response = customer_table.get_item(Key={'customer_id': customer_id})
        elif email:
            response = customer_table.query(
                IndexName='email-index',
                KeyConditionExpression=Key('email').eq(email)
            )
            if response['Items']:
                return response['Items'][0]
        elif phone:
            response = customer_table.query(
                IndexName='phone-index',
                KeyConditionExpression=Key('phone').eq(phone)
            )
            if response['Items']:
                return response['Items'][0]
        else:
            return {'error': 'Customer ID, email, or phone required'}
            
        return response.get('Item', {'error': 'Customer not found'})
    except Exception as e:
        return {'error': str(e)}

def check_warranty_status(event):
    serial_number = event.get('serial_number')
    customer_email = event.get('customer_email')
    
    try:
        response = warranty_table.get_item(Key={'serial_number': serial_number})
        warranty = response.get('Item')
        
        if not warranty:
            return {'error': 'Product not found'}
            
        if customer_email and warranty.get('customer_email') != customer_email:
            return {'error': 'Email does not match warranty record'}
            
        return warranty
    except Exception as e:
        return {'error': str(e)}
