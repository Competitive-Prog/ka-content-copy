import os
import urllib.request

from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

key = os.getenv("TRANSLATOR_KEY")
# only the domain
endpoint = "https://course-translation2.cognitiveservices.azure.com/"
# Had to use account keys, not user delegation keys
source_url = os.getenv("SOURCE_URL")
target_url = os.getenv("TARGET_URL")
language = "pt"

client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

poller = client.begin_translation(sourceUrl, targetUrl, language)
result = poller.result()

print("Status: {}".format(poller.status()))
print("Created on: {}".format(poller.details.created_on))
print("Last updated on: {}".format(poller.details.last_updated_on))
print("Total number of translations on documents: {}".format(poller.details.documents_total_count))

print("\nOf total documents...")
print("{} failed".format(poller.details.documents_failed_count))
print("{} succeeded".format(poller.details.documents_succeeded_count))

for document in result:
    print("Document ID: {}".format(document.id))
    print("Document status: {}".format(document.status))
    if document.status == "Succeeded":
        print("Source document location: {}".format(document.source_document_url))
        print("Translated document location: {}".format(document.translated_document_url))
        print("Translated to language: {}\n".format(document.translated_to))
    else:
        print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))
