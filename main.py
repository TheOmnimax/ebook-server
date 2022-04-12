from typing import Optional
import logging
import google.auth.transport.requests
from google.cloud import storage
import google.cloud.logging
import google.oauth2.id_token

from ebooklib import epub

from os.path import dirname, join
from os import remove, environ

from fastapi import FastAPI, Header, Response, Request
from fastapi.responses import JSONResponse
# from pydantic import BaseModel

from server_utils import ebook_uploader, ebook_downloader


logging.getLogger().addHandler(logging.StreamHandler()) # For testing

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()

HTTP_REQUEST = google.auth.transport.requests.Request()
EBOOK_BUCKET = environ['EBOOK_BUCKET']
HELPER_BUCKET = environ['HELPER_BUCKET']
EBOOK_DATA = environ['EBOOK_DATA']

# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Optional[bool] = None

@app.middleware('http')
async def checkAuthToken(request: Request, call_next):
  print('In middleware')
  headers = request.headers
  print(headers)

  if 'authorization' in headers:
    authorization = headers['authorization']
    print('Have header!')
  else:
    response = JSONResponse(content = {'message': 'Authorization token empty!'})
    response.status_code = 401
    return response
    
  # return await call_next(request) # TESTING ONLY!

  try:
    claims = google.oauth2.id_token.verify_firebase_token(
      authorization, HTTP_REQUEST, audience=environ.get('GOOGLE_CLOUD_PROJECT'))
  except:
    response = JSONResponse(content = {'message': 'Unauthorized!'})
    response.status_code = 401
    return response
  if not claims:
    response = JSONResponse(content = {'message': 'Unauthorized!'})
    response.status_code = 401
    return response
  else:
    response = JSONResponse(content = {'message': 'Authorized, yeah!'})
    response.status_code = 200
    return await call_next(request)
  return checkToken

@app.get('/')
async def read_root():
  return "Hi!"

@app.post('/list-all')
async def listAll(request: Request):
  return ebook_downloader.listEbookFiles(request)

@app.post('/download-ebook')
async def getEbook(request: Request):
  logging.info('In main function')
  return await ebook_downloader.downloadEbookFile(request)


@app.post('/upload')
async def uploadBook(request: Request):
  logging.info('In main function')
  return await ebook_uploader.uploadBook(request)


# TODO: Add endpoint for info on specific book

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)