from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']


def contacts(camion):
    """Shows basic usage of the People API.
    Prints the name of the first 10 connections.
    """
    camion=camion.upper()
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('people', 'v1', credentials=creds)

        # Call the People API
        #print('List 10 connection names')
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=0,
            personFields='names,phoneNumbers,organizations').execute()
        connections = results.get('connections', [])

        #print(connections)
        lista_n=[]

        for person in connections:

                try:

                    names = person.get('names', [])
                    numbers = person.get('phoneNumbers', [])
                    jobs = person.get('organizations',[])
                    if names or numbers:
                        name = names[0].get('displayName')
                        #print(numbers)
                        if numbers[0].get('canonicalForm') == None:
                            number = numbers[0].get('value')
                            number = '+57'+number
                        else:
                            number = numbers[0].get('canonicalForm')

                        job = jobs[0].get('title')
                        job = job.upper()
                        #print(f'{name} {job}')
                        number=number[3:]
                        if camion == 'TODOS':

                            number = ''.join(number.split())
                            lista_n.append(number)
                            #print(f'{name} {number}')
                            print(f'{name} {job}')

                        elif camion == 'TEST':

                            lista_n=['0000000000']
                            break

                        else:

                            if camion == job:

                                number = ''.join(number.split())
                                lista_n.append(number)
                                #print(f'{name} {number}')
                                print(f'{name} {job}')

                            else:
                                pass

                except IndexError as probl:

                    print(f'El contacto {name} tiene un problema con sus datos ({probl})')

        print(camion)

        return(lista_n)

    except HttpError as err:
        print(err)

if __name__ == '__main__':

    #camion="1turbo"
    print(contacts(camion))