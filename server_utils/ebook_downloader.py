from .ebook_data import EBOOK_BUCKET, HELPER_BUCKET, EBOOK_DATA, EbookMetadata, GCloudEbookTool
from fastapi import FastAPI, Header, Response, Request
from google.cloud import storage, datastore
from google.api_core.exceptions import NotFound
import json
import logging
from fastapi.responses import JSONResponse

def renameKey(kind, oldname, newname): # UNUSED, DELETE
  
    d_client = datastore.Client()

    query = d_client.query(kind=kind)
    results = list(query.fetch())
    for old_entity in results:
      key_name = old_entity.key.id_or_name
      entity_dict = dict(old_entity.items())
      task_key = d_client.key(kind, key_name)
      new_entity = datastore.Entity(key=task_key)
      for key in entity_dict:
        if key == oldname:
          new_entity[newname] = entity_dict[key]
        else:
          new_entity[key] = entity_dict[key]

      # d_client.delete(key_name)
      d_client.put(new_entity)

def listEbookFiles(request: Request):

  try:
    d_client = datastore.Client()

    query = d_client.query(kind='eBook')
    results = list(query.fetch())
    ebook_list = []
    for entity in results:
      filename = entity.key.id_or_name
      ebook_dict = dict(entity.items())
      ebook_dict['filename'] = filename
      ebook_list.append(ebook_dict)

    response = JSONResponse(ebook_list)
    response.status_code = 200
    return response
  except:
    logging.exception('Error getting list of eBooks.')
    response = Response(content = 'Error getting list of eBooks')
    response.status_code = 500
    return response

async def downloadEbookFile(request: Request):
  logging.info('Starting...')
  filename_bytes = b''
  async for chunk in request.stream():
    filename_bytes += chunk
  filename = filename_bytes.decode('utf-8')
  logging.info(f'File name: {filename}')

  if filename == '':
    response = Response(content = 'No name given')
    logging.info(f'Created response')
    response.status_code = 404
    return response

  gcs = storage.Client()
  ebook_bucket = gcs.get_bucket(EBOOK_BUCKET)
  logging.info(f'Got bucket')

  ebook_blob = ebook_bucket.blob(filename)
  logging.info(f'Got blob')
  
  try:
    ebook_file = ebook_blob.download_as_bytes()
    logging.info(f'Got file')
  except NotFound:
    print('File ')
    response = JSONResponse(content={'error': f'No file found called {filename}.'})
    response.status_code = 404
    return response

  response = Response(content = ebook_file)
  logging.info(f'Created response')
  response.status_code = 200
  return response

