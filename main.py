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


from server_utils import ebook_uploader

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()

HTTP_REQUEST = google.auth.transport.requests.Request()
EBOOK_BUCKET = environ['EBOOK_BUCKET']

# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Optional[bool] = None


def checkAuthToken(func): # Decorator
  logging.info('Preparing decorator')
  async def checkToken(request: Request,authorization: Optional[str] = Header(None)):
    logging.info('In decorator')
    return await func(request) # TESTING ONLY!

    if authorization == Header(None):
      response = JSONResponse(content = {'message': 'Authorization token empty!'})
      response.status_code = 401
      return response
    else:
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
        return await func(request)
  return checkToken

@app.get('/')
async def read_root():
  return "Hi!"

@app.get('/list-all')
@checkAuthToken
def listAll():
  storage_client = storage.Client()
  bucket = storage_client.bucket(EBOOK_BUCKET)


@app.post('/upload')
@checkAuthToken
async def uploadBook(request: Request):
  logging.info('In main function')
  return await ebook_uploader.uploadBook(request)

# if __name__ == '__main__':
#   app.run(host='127.0.0.1', port=8080, debug=True)