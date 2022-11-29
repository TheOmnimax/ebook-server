from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from .ebook_data import EBOOK_BUCKET, EbookMetadata, TMP_PATH

from google.cloud import storage, datastore

async def uploadBook(request: Request):
  logging.info('Working...')

  book_data = b''
  
  async for chunk in request.stream():
    book_data += chunk
  
  gcs = storage.Client()
  ebook_bucket = gcs.get_bucket(EBOOK_BUCKET)

  # TMP_PATH = '/tmp/tmp_ebook' # The leading slash is crucial, or it will fail
  with open(TMP_PATH, 'wb') as fp:
    fp.write(book_data)
    logging.info(f'Path: {TMP_PATH}')
    book_metadata = EbookMetadata(TMP_PATH)
    book_metadata.process()
    logging.info('Processing successful!')

  filename = book_metadata.genFilename()
  ebook_blob = ebook_bucket.blob(filename)
  with open(TMP_PATH, 'rb') as f:
    ebook_blob.upload_from_file(f)

  logging.info('Upload successful!')

  # Add to datastore
  datastore_client = datastore.Client()
  kind = 'eBook'
  key_name = filename
  task_key = datastore_client.key(kind, key_name)
  task = datastore.Entity(key=task_key)

  ebook_dict = book_metadata.toDict()

  for key in ebook_dict:
    task[key] = ebook_dict[key]

  try:
    datastore_client.put(task)
  except:
    logging.exception('Error when adding eBook to Datastore.')
    response = JSONResponse(content = {
      'filename': filename,
      'info': 'The file was successfully uploaded, but it was not added to the list of ebooks, so it will not come up in a search.'
      })
    response.status_code = 500
    logging.info('Completed with errors.')
    return response

  response = JSONResponse(content = {
    'filename': filename,
    'info': 'The file was added successfully!'
    })
  response.status_code = 201
  logging.info('Done!')
  return response
