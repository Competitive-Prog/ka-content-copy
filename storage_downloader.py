import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

try:
    print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client("target")
    print("\nListing blobs...")
    blob_list = container_client.list_blobs()
    for blob in blob_list:
      if blob.name.startswith('en/'):
        print(blob.name)
        download_file_path = str.replace(blob.name ,'en/', 'tr/')
        print(download_file_path)
        with open(download_file_path, "wb") as download_file:
           download_file.write(container_client.download_blob(blob.name).readall())
except Exception as ex:
    print('Exception:')
    print(ex)
