# Server utilities (server_utils)

The "server_utils" directory on this server contains tools for uploading, downloading, and analyzing ebooks. It contains three files

**ebook_data**: This file contains classes for working with ebooks, including bucket paths of where they are stored, and tools for retrieving metadata.

**ebook_download**: 

This file contains functions used to download ebooks, including listing all of them.

## ebook_uploader

This contains a single function, which is used by the REST API to upload a new EPUB file.

Here is an overview of what the function does:

That function takes raw request data as a parameter, which should contain the EPUB file. Here is what the function does:

1. Extract the EPUB file from the request.
1. Put EPUB file it into a temporary location, so its metadata can be retrieved before it is sent to a permanent location.
1. Metadata is retrieved from the EPUB file in the temporary location.
1. EPUB file name is determined based on metadata, so it is unique.
1. EPUB file is uploaded to bucket.
1. Datastore entity is created with EPUB metadata, including file name, so its data can be sent to the client to determine which book should be downloaded, and so the app knows which file should be downloaded.