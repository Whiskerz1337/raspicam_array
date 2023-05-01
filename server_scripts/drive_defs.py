import os
import pickle
import google.auth
import tempfile
from io import BytesIO 
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            print('Please go to this URL and authorize the app:', auth_url)
            auth_code = input('Enter the authorization code: ')
            flow.fetch_token(code=auth_code)
            creds = flow.credentials

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_folder(parent_id, folder_name):
    try:
        service = build('drive', 'v3', credentials=authenticate())

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        file = service.files().create(body=file_metadata, fields='id').execute()
        print(F'Folder ID: "{file.get("id")}".')
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get("id")

def upload_to_drive(image_data, file_name, folder_id):
    try:
        service = build('drive', 'v3', credentials=authenticate())

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(image_data.getvalue())
            tmp.flush()
            media = MediaFileUpload(tmp.name, mimetype='image/jpeg', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(F'File ID: "{file.get("id")}".')
        return True
    except HttpError as error:
        print(F'An error occurred: {error}')
        return False
