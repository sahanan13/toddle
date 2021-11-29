from __future__ import print_function
import time
import boto3
import urllib
import sys
import os
import json

transcribe = boto3.client('transcribe')

def get_s3uri(file_name, file_type, user_input):
    bucket_name = "toddle-transcribe-test-mjk" # let files uploaded to the same s3 bucket

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    try:
        bucket.upload_file(user_input, file_name, ExtraArgs = {}) # TODO debug usage of upload_file
    except:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'us-east-2'
        })
        bucket.upload_file(user_input, file_name, ExtraArgs = {})

    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    uri = "s3://%s/%s" % (bucket_name, file_name)
    return uri


def transcribe_file(job_name, job_uri, transcribe, file_type):
    text_output = ""

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=file_type,
        LanguageCode='en-US'
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            data = json.loads(response.read())
            text = data['results']['transcripts'][0]['transcript']
            print("========== below is output of speech-to-text ========================")
            print(text)
            text_output += text
            print("=====================================================================")
            break
        print("In Progress...")
        time.sleep(10)
    return text_output

def main():
    # gets input for os type and file path
    os_type = input("Type \"w\" for windows and \"m\" for mac: ")
    user_input = input("type file path: ") 
    if os_type == "w":
        slash = "\\"
    else:
        slash = "/"
    job_name = user_input.split(slash)[2] + "_job"
    file_name = user_input.split(slash)[4]
    file_type = file_name.split(".")[1]

    # finds file from the input path
    assert os.path.exists(user_input), "File not found at " + str(user_input)
    print("File " + str(user_input) + " is found")
    job_file = open(user_input, 'r+')

    # uploads the file to s3 bucket and get its uri
    job_uri = get_s3uri(file_name, file_type, user_input)
    print( "job uri: " + job_uri )

    # TODO: skip transcription if json/txt file exists & save as file_name.json

    # gets a transcription with AWS transcribe from s3 uri
    text_output = transcribe_file(job_name, job_uri, transcribe, file_type)
     
if __name__ == '__main__':
    main()