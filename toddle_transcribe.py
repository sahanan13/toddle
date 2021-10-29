from __future__ import print_function
import time
import boto3

transcribe = boto3.client('transcribe')

def transcribe_file(job_name, job_uri, transcribe)
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='mp4',
    LanguageCode='en-US'
)

while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Not ready yet...")
    time.sleep(5)
print(status)

def main():
    job_name = input("type job name: ")
    job_uri = input("type input uri: ")
    transcribe_file(job_name, job_uri, transcribe_client)

if __name__ == '__main__':
    main()