import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error

print('Loading function')

rekognition = boto3.client('rekognition')


# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_text(photo, bucket):

    client=boto3.client('rekognition', 'us-east-2')

    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
                        
    textDetections=response['TextDetections']
    detected_text = ""
    
    for text in textDetections:
        if not 'ParentId' in text:
            detected_text += ('Detected text: ' + text['DetectedText'] + '  @ Confidence: ' + "{:.2f}".format(text['Confidence']) + "%\n")
    return detected_text
    
def upload_to_aws(data, bucket_name, s3_file):
    encoded_data = data.encode("utf-8")
    
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_file, Body=encoded_data)


# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    print (input_bucket)
    
    output_bucket = 'odt-receipt-output-bucket'
    print(output_bucket)
    
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    print(key)
    response = ""
    
    try:
        # Calls rekognition DetectText API to detect faces in S3 object
        response=detect_text(key,input_bucket)
        print(response)

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, input_bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
        
    try:
        upload_to_aws(response, output_bucket, key.replace(".jpg", "_output.txt"))

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, output_bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
