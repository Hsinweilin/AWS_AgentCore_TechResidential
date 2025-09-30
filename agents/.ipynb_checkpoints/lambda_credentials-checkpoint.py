import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """Lambda function to retrieve all credentials for a client website
    Args:
        event: Contains client_name for which to retrieve credentials
    Returns:
        Dictionary with all credentials for the requested site
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

    ssm = boto3.client('ssm')

    def get_secret(parameter_name):
        try:
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
            return response['Parameter']['Value']
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ParameterNotFound':
                raise Exception(f"Parameter '{parameter_name}' not found")
            elif error_code == 'AccessDenied':
                raise Exception(f"Access denied to parameter '{parameter_name}' - check IAM permissions")
            else:
                raise Exception(f"Error retrieving '{parameter_name}': {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error retrieving '{parameter_name}': {str(e)}")

    # Construct parameter names dynamically
    login_param = f"{client_name}_Login"
    password_param = f"{client_name}_Password"
    weburl_param = f"{client_name}_WebURL"

    parameter_names = [login_param, password_param, weburl_param]

    try:
        login_credentials = get_secret(login_param)
        password_credentials = get_secret(password_param)
        web_url = get_secret(weburl_param)

        if not all([login_credentials, password_credentials, web_url]):
            missing = []
            if not login_credentials: missing.append(login_param)
            if not password_credentials: missing.append(password_param)
            if not web_url: missing.append(weburl_param)
            raise Exception(f"Missing required parameters: {', '.join(missing)}")

        credentials_response = {
            'starting_url': web_url,
            'login_credentials': login_credentials,
            'login_password': password_credentials,
            'file_info': {
                'upload_path': '/uploads',
                'allowed_extensions': ['.pdf', '.docx', '.txt'],
                'max_file_size': '10MB'
            },
            'retrieved_from': 'AWS_SSM_Parameter_Store',
            'parameters_used': parameter_names
        }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'client_name': client_name,
                'credentials': credentials_response,
                'message': f'Successfully retrieved {client_name} credentials from SSM'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve {formatted_client_name} credentials from SSM Parameter Store'
            })
        }
