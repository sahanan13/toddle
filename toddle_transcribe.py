from __future__ import print_function
import time
import boto3
import urllib
import sys
import os
import json
import numpy
import scipy
import gensim

# for summarization
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from datetime import datetime

transcribe = boto3.client('transcribe')
s3 = boto3.resource('s3')
bucket_name = "toddle-transcribe-test-mjk" # let files uploaded to the same s3 bucket

# get file path as an input for parameters
def user_input(date):
    os_type = input("Type \"w\" for windows and \"m\" for mac: ")
    file_path = input("type file path: ") 
    if os_type == "w":
        slash = "\\"
    else:
        slash = "/"
    job_name = file_path.split(slash)[2] + "_job_" + date
    file_name = file_path.split(slash)[4]
    file_type = 'mp4' #file_name.split(".")[1]

    # finds file from the input path
    assert os.path.exists(file_path), "File not found at " + str(user_input)
    print("File " + str(file_path) + " is found")
    # job_file = open(file_path, 'r+')

    return file_path, job_name, file_name, file_type

def get_s3uri(file_name, user_input):
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
    # uri = 'https://s3-en-US.amazonaws.com/'+bucket_name+'/'
    print( "Job uri: " + uri )
    return uri 


def transcribe_file(job_name, job_uri, transcribe, file_type):
    text_output = ""

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            data = json.loads(response.read())
            text = data['results']['transcripts'][0]['transcript']
            #print("========== below is output of speech-to-text ========================")
            #print(text)
            text_output += text
            #print("=====================================================================")
            break
        print("In Progress...")
        time.sleep(10)
    
    # delete transcription job in bucket
    transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    s3.delete_object(Bucket=bucket_name)

    return text_output

def summarize_text(file_path, file_name, text, date):
    # Summary (2.0% of the original content)
    summ_per = summarize(text, ratio = 0.20)
    pathname = 'summary' + date + '.txt'
    with open(os.path.join(file_path.replace(file_name, '')), 'w') as f:
        f.write(summ_per)

    print("Written to file: "+ pathname + " at " + file_path)

def main():
    # get datetime for naming
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H.%M.%S")

    # open the file and get parameters from path
    file_path, job_name, file_name, file_type = user_input(dt_string)

    # upload the file to s3 bucket and get its uri
    job_uri = get_s3uri(file_name, file_path)

    # TODO: skip transcription if json/txt file exists & save as file_name.json

    # get a transcription with AWS transcribe from s3 uri
    text_output = transcribe_file(job_name, job_uri, transcribe, file_type)
    
    # use gensim to summarize the transcription
    summarize_text(file_path, file_name, text_output, dt_string)

if __name__ == '__main__':
    main()