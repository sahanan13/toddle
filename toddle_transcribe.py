from __future__ import print_function
import time
import boto3
import urllib
import sys
import os
import json

transcribe = boto3.client('transcribe')

def transcribe_file(job_name, job_uri, transcribe):
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
            print("========== below is output of speech-to-text ========================")
            print(text)
            print("=====================================================================")
            break
        print("In Progress...")
        time.sleep(10)
    print(status)

def main():
    # user_input = input() # file path
    # assert os.path.exists(user_input), "File not found st" + str(user_input)
    # job_file = open(user_input, 'r+')

    # job_name = input("type job name: ")
    # job_uri = input("type input uri: ")
    job_name = 'test_mjk3'
    job_uri = 's3://toddle-test-mjk/COLHIST12014-V008200_DTH.mp4'
    transcribe_file(job_name, job_uri, transcribe)

if __name__ == '__main__':
    main()