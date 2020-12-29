import json
import boto3
import base64
import uuid

s3 = boto3.resource('s3')
bucket_name = 'safety-plan-artifacts'


def upload_file(data):
    obj_id = uuid.uuid4()
    obj_name = '{}.pdf'.format(obj_id)

    obj = s3.Object(bucket_name, obj_name)
    obj.put(Body=base64.b64decode(data), ACL='public-read')
    object_url = "https://%s.s3.amazonaws.com/%s" % (bucket_name, obj_name)
    return object_url


def publish_to_phone(msg, phone_number='+17544221236'):
    sns = boto3.client('sns')

    # Send a SMS message to the specified phone number
    response = sns.publish(
        PhoneNumber=phone_number,
        Message=msg,
        MessageAttributes={
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'
            }
        }
    )
    print(response)


def handler(event, context):

    event = json.loads(event['body'])
    base64_data = event['data']
    phone_number = event['number']

    object_url = upload_file(base64_data)
    publish_to_phone(object_url, phone_number)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "url":  object_url
        }),
    }
