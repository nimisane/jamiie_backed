

# from logging import raiseExceptions
import logging
import dwollav2
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import requests
import shutil
from PIL import Image
from io import BytesIO
import urllib.request
import threading
from .models import ServerStat
import time
load_dotenv(dotenv_path='../.env')
import os
import psutil
def auth():
    client = dwollav2.Client(
        key = os.getenv('DWOLLA_KEY'),
        secret= os.getenv('DWOLLA_SECRET_KEY'),
        environment= os.getenv('ENV'), # defaults to 'production'
    )
    app_token = client.Auth.client()
    return app_token
app_token = auth()
# https://docs.dwolla.com/#create-a-funding-source-for-an-account
# creating funding source for JAMIIE
def refreshToken():
    try:
        ServerStat.objects.create(ram=psutil.virtual_memory()[3], status='Before')
        logging.info('Refresh token is called')
        global app_token
        del app_token
        client = dwollav2.Client(key = os.getenv('DWOLLA_KEY'),secret= os.getenv('DWOLLA_SECRET_KEY'),environment= os.getenv('ENV')) # defaults to 'production'
        app_token = client.Auth.client()
        # time.sleep(45*60)
        ServerStat.objects.create(ram=psutil.virtual_memory()[3], status= 'After')
    except Exception as e:
        print(e)
# t1 = threading.Thread(target=refreshToken, args=())  
# t1.start()    
# https://docs.dwolla.com/#idempotency-key
# To prevent multiple post req
headers = {
    'Idempotency-Key': '19051a62-3403-11e6-ac61-9e71128cae77'
}


def owner_acc_details():
    r = app_token.get('/')
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)
    print(r.body['_links']['account']['href'])


def owner_funding_src(request_body):
    r = app_token.post('funding-sources', request_body)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)
    print(r.headers['location'])


def get_owner_funding_src(account_url):
    r = app_token.get('%s/funding-sources' % account_url)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)


def initiate_micro_deposits(funding_source_url):
    r = app_token.post('%s/micro-deposits' % funding_source_url)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)


def verify_micro_deposits(funding_source_url):
    request_body = {
        'amount1': {
            'value': '0.03',
            'currency': 'USD'
        },
        'amount2': {
            'value': '0.09',
            'currency': 'USD'
        }
    }
    r = app_token.post('%s/micro-deposits' % funding_source_url, request_body)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)

def get_customers(limit):
    r = app_token.get('customers', {'limit': limit})
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)

def create_customer(request_body):
    try:   
        r = app_token.post('customers', request_body)
        return r.headers['location']
    except dwollav2.error.ValidationError as e:
        return 400
    except Exception as e:
        print(e)

def customer_status(url):
    r = app_token.post(url)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)
    print(r.body['status'])


def upload_customer_documents(url,img_url,documentType): 
    filename = img_url.split("/")[-1]
    urllib.request.urlretrieve(img_url, filename)
    print("app_token",app_token)
    r = app_token.post('%s/documents' % url, file=open(filename, 'rb'), documentType=documentType)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    return r.headers['location']


# get a iav token valid for 60min
try:
    def get_iav_token(url):
        r = app_token.post('%s/iav-token' % url)
        indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
        print(indented_json)
        return r.body['token']
except Exception as e:
    print('get_iav_token: ',e)

def retrieve_funding_src(funding_src):
    r = app_token.get(funding_src)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)
    print(r.body['name'])


def initiate_transfer(request_body):
    r = app_token.post('transfers', request_body)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    return r.headers['location']


def mass_payments(request_body):
    r = app_token.post('mass-payments', request_body)
    indented_json = json.dumps(r.body, indent=4, separators=(',', ': '), sort_keys=True)
    print(indented_json)
    print(r.headers['location'])
