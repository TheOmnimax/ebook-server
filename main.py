import logging
import google.auth.transport.requests
import google.cloud.logging
import google.oauth2.id_token

from fastapi import FastAPI,  Request
from fastapi.responses import JSONResponse

from server_utils import ebook_uploader, ebook_downloader

logging.getLogger().addHandler(logging.StreamHandler()) # For testing

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()

HTTP_REQUEST = google.auth.transport.requests.Request()

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