from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

drive = GoogleDrive(gauth)

# List of folder IDs
folder_ids = ['1_45iWkP556GcLL1Lviw1cqkhFHN5fRbZ', '1zW5mYHd20nNqpDWEJrb6NkBIKWqm5yqa']

for folder_id in folder_ids:
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()

    for file in file_list:
        print('title: %s, id: %s' % (file['title'], file['id']))
        file.GetContentFile(file['title'])
