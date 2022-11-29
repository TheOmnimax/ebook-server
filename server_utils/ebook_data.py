from ebooklib import epub
from os import environ
from google.cloud import storage
import json
import logging

EBOOK_BUCKET = environ['EBOOK_BUCKET']
HELPER_BUCKET = environ['HELPER_BUCKET']
EBOOK_DATA = environ['EBOOK_DATA']
TMP_PATH = environ['TMP_PATH']

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
      'publishers': self.publishers,
    }

class GCloudEbookTool: # Currently unused, but may update later so a DOA is used for ebooks instead of functions.
  def __init__(self):
    self.gcs = storage.Client()
    self.ebook_bucket = self.gcs.get_bucket(EBOOK_BUCKET)
    self.helper_bucket = self.gcs.get_bucket(HELPER_BUCKET)
  
  def getDictData(self):
    ebook_dict_blob = self.helper_bucket.blob(EBOOK_DATA)
    ebook_data_raw = ebook_dict_blob.download_as_string()
    try:
      ebook_data = json.loads(ebook_data_raw)
    except:
      logging.exception('Error converting string to dict.')
      return {'error': 'Failed'}

    return ebook_data