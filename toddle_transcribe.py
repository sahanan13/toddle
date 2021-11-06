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
    print(user_input) 
    print(bucket_name)
    print(file_name)

    try:
        bucket.upload_file(user_input, file_name, ExtraArgs = {}) # TODO debug usage of upload_file
    except:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'us-east-2'
        })
        bucket.upload_file(user_input, file_name, ExtraArgs = {})

    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    # url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, key)
    # job_uri = 's3://toddle-test-mjk/COLHIST12014-V008200_DTH.mp4'

    uri = "s3://%s/%s" % (bucket_name, file_name)
    print("uri:  " + uri)
    return uri


def transcribe_file(job_name, job_uri, transcribe, file_type):
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
            print("=====================================================================")
            break
        print("In Progress...")
        time.sleep(10)
    print(status)

def main():
    
    job_name = input("type job name: ")
    file_name = input("type file name: ") # toddle_lec
    file_type = input("type file type: ") # mp4
    # user_input = input("type file path: ") # file path: C:\Users\Minjk\Downloads\toddle_lec.mp4
    user_input = 'C:\\Users\\Minjk\\Downloads\\toddle_lec.mp4'

    # print(type(job_name))
    # print(type(file_name))
    # print(type(file_type))
    # print(type(user_input))

    assert os.path.exists(user_input), "File not found at " + str(user_input)
    print("File " + str(user_input) + "is found")
    job_file = open(user_input, 'r+')

    job_uri = get_s3uri(file_name, file_type, user_input)
    print( "job uri: " + job_uri )

    transcribe_file(job_name, job_uri, transcribe, file_type)

    # job_file.close()

    # job_name = 'test_mjk3'
    # job_uri = 's3://toddle-test-mjk/COLHIST12014-V008200_DTH.mp4'
    # transcribe_file(job_name, job_uri, transcribe)

if __name__ == '__main__':
    main()