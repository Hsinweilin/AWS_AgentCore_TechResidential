import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function to retrieve a prompt file from S3 based on client_name.
    Args:
        event: Contains client_name for which to retrieve the file
    Returns:
        Dictionary with file content or error message
    """
    client_name = event.get('client_name')
    if not client_name:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'error': 'Missing required parameter: client_name',
                'message': 'Please provide a client_name in the event'
            })
        }

    bucket_name = 'bedrock-web-automation-dev-storage'
    file_key = f'prompt-files/{client_name}/prompt.txt'

    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'client_name': client_name,
                'file_key': file_key,
                'file_content': file_content,
                'message': f'Successfully retrieved file for {client_name} from S3'
            })
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            error_msg = f"File '{file_key}' not found in bucket '{bucket_name}'"
        elif error_code == 'AccessDenied':
            error_msg = f"Access denied to file '{file_key}' - check IAM permissions"
        else:
            error_msg = f"Error retrieving file '{file_key}': {str(e)}"
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': error_msg,
                'message': f'Failed to retrieve file for {client_name} from S3'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': f'Unexpected error retrieving file for {client_name} from S3'
            })
        }