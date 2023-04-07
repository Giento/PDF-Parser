import os
import shutil
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Define the function to download a Google Drive folder
def download_folder(folder_id, save_path, creds):
    # Build the Google Drive API client
    service = build('drive', 'v3', credentials=creds)

    # Get the metadata of the folder
    try:
        folder_metadata = service.files().get(fileId=folder_id, fields='name,mimeType').execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
        return

    # Make sure the folder is actually a folder
    if folder_metadata['mimeType'] != 'application/vnd.google-apps.folder':
        print('The provided ID does not belong to a Google Drive folder.')
        return

    # Create the save directory
    folder_name = folder_metadata['name']
    save_dir = os.path.join(save_path, folder_name)
    os.makedirs(save_dir, exist_ok=True)

    # Download each file in the folder
    files = service.files().list(q=f"'{folder_id}' in parents",
                                 fields='files(id,name,mimeType,webContentLink)').execute().get('files', [])
    for file in files:
        file_id = file['id']
        file_name = file['name']
        file_type = file['mimeType']
        file_link = file['webContentLink']

        # Skip over Google Docs, Sheets, etc.
        if file_type.startswith('application/vnd.google'):
            continue

        # Download the file
        response = requests.get(file_link, headers={'Authorization': f'Bearer {creds.token}'})
        with open(os.path.join(save_dir, file_name), 'wb') as f:
            f.write(response.content)

        print(f'Downloaded {file_name}')

    print(f'Download complete: {folder_name} -> {save_dir}')


# Set the folder ID, save path, and credentials
folder_id = ''      # add folder id here
save_path = './dwnld_drive'
creds = Credentials.from_authorized_user_file('./credentials.json', ['https://www.googleapis.com/auth/drive'])

# Call the function to download the folder
download_folder(folder_id, save_path, creds)
