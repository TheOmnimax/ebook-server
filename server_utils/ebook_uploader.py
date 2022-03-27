from fastapi import Request
from fastapi.responses import JSONResponse
from ebooklib import epub
from os.path import dirname, join, abspath
from os import remove, environ, listdir
from ebooklib import epub
import logging
import tempfile
import json

from google.cloud import storage

EBOOK_BUCKET = environ['EBOOK_BUCKET']
HELPER_BUCKET = environ['HELPER_BUCKET']
EBOOK_DATA = environ['EBOOK_DATA']

class EbookMetadata:
  def __init__(self, path):
    self.path = path
  
  def process(self):
    self.book = epub.read_epub(self.path)
    self.title = self.book.title

    authors_raw = self.book.get_metadata('DC', 'creator')
    publishers_raw = self.book.get_metadata('DC', 'publisher')

    self.authors = []
    self.publishers = []
    for author in authors_raw:
      self.authors.append(author[0])
    for publisher in publishers_raw:
      self.publishers.append(publisher[0])
  
  def genFilename(self):
    filename = self.title + '|' \
      ','.join(self.authors) + '|' \
        ','.join(self.publishers) + \
          '.epub'

    return filename
  
  def toDict(self):
    return {
      'title': self.title,
      'authors': self.authors,
      'publishers': self.publishers
    }

  
    

async def uploadBook(request: Request):
  logging.info('Working...')

  book_data = b''
  
  async for chunk in request.stream():
    book_data += chunk
  
  
  gcs = storage.Client()
  ebook_bucket = gcs.get_bucket(EBOOK_BUCKET)
  helper_bucket = gcs.get_bucket(HELPER_BUCKET)

  
  
  path = join('/tmp', 'tmp_ebook') # The leading slash is crucial, or it will fail
  with open(path, 'wb') as fp:
    fp.write(book_data)
    logging.info(f'Path: {path}')
    book_metadata = EbookMetadata(path)
    book_metadata.process()
    logging.info('Processing successful!')

  filename = book_metadata.genFilename()
  ebook_blob = ebook_bucket.blob(filename)
  with open(path, 'rb') as f:
    ebook_blob.upload_from_file(f)

  logging.info('Upload successful!')

  ebook_dict_blob = helper_bucket.blob(EBOOK_DATA)
  ebook_data_raw = ebook_dict_blob.download_as_string()

  try:
    ebook_data = json.loads(ebook_data_raw)
  except:
    logging.exception('Unable to convert ebook data list to dict.')
    response = JSONResponse(content = {
      'filename': filename,
      'info': 'The file was successfully uploaded, but it was not added to the list of ebooks, so it will not come up in a search.'
      })
    response.status_code = 500
    logging.info('Completed with errors.')
    return response

  if filename in ebook_data:
    logging.error(f'File "{filename} already exists.')
    response = JSONResponse(content = {
      'filename': filename,
      'info': f'File "{filename} already exists.'
      })
    response.status_code = 500
    logging.info('Completed with errors')
    return response
  else:
    ebook_data[filename] = book_metadata.toDict()
    str_ebook_data = json.dumps(ebook_data)
    ebook_dict_blob.upload_from_string(str_ebook_data)

    response = JSONResponse(content = {
      'filename': filename,
      'info': 'The file was successfully added!'
      })
    response.status_code = 201
    logging.info('Done!')
    return response
