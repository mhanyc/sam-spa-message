import json
import boto3
import base64
import uuid
import sentry_sdk
from sentry_sdk import capture_exception
from botocore.exceptions import ClientError
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn="https://ed7b0d39a2b64968b5c6635650d71086@o301017.ingest.sentry.io/5582810",
    integrations=[AwsLambdaIntegration()]
)

s3 = boto3.resource('s3')
bucket_name = 'safety-plan-artifacts'


def upload_file(data):
    obj_id = uuid.uuid4()
    obj_name = '{}.pdf'.format(obj_id)

    obj = s3.Object(bucket_name, obj_name)
    obj.put(Body=base64.b64decode(data), ACL='public-read')
    object_url = "https://%s.s3.amazonaws.com/%s" % (bucket_name, obj_name)
    return object_url


def publish_to_phone(msg, email='noreply@vibrant.org'):
    ses = boto3.client('ses')

    # Send an EMail to the specified email
    response = sns.publish(
        SENDER=email,
        Message=msg,
        MessageAttributes={
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'
            }
        }
    )
    print(response)


def send_email(to_email, msg_content, from_email='noreply@vibrant.org'):
    client = boto3.client('ses', region_name='us-east-1')

    response = client.send_email(
        Destination={
            'ToAddresses': [
                to_email,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': "UTF-8",
                    'Data': "Here's your safety plan",
                },
                'Text': {
                    'Charset': "UTF-8",
                    'Data': "BODY_TEXT",
                },
            },
            'Subject': {
                'Charset': "UTF-8",
                'Data': "Your Safety Plan",
            },
        },
        Source=from_email,
        # If you are not using a configuration set, comment or delete the
        # following line
        # ConfigurationSetName=CONFIGURATION_SET,
    )
    print(response)


def handler(event, context):

    event = json.loads(event['body'])
    type = event['type']

    if type == "text":
        base64_data = event['data']
        phone_number = event['number']

        object_url = upload_file(base64_data)
        publish_to_phone(object_url, phone_number)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "url": object_url
            }),
        }
    else:
        email_content = event['data']

        send_email('atarla@vibrant.org', email_content, from_email='noreply@vibrant.org')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "pdf": "pdf"
            }),
        }

