# Blastomussa: 12/20/21
# Google Workspace directory access requires accompanying 
# Google Cloud project with API access enabled. See Python quickstart 
# for details: https://developers.google.com/admin-sdk/directory/v1/quickstart/python

# Google requirements
from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# import FreshPy module
from FreshPy import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

# Google cloud project API credentials should be saved in same diectory as credentials.json
def authorize():
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
    return creds


def main():
    """
    Syncs users from Google Workspace to Fresh Service(adds new, deletes old).
    Adds users to their respective requester groups in FreshService
    """

    # create Google service for API calls
    creds = authorize()
    service = build('admin', 'directory_v1', credentials=creds)

    # create FreshPy instance for API calls
    api_key = '################'
    FreshService_domain = 'https://customdomain.freshservice.com'
    FS = FreshPy(api_key, FreshService_domain)


    # Get all users on Google workspace domain
    results = service.users().list(customer='my_customer', maxResults=100,
                                   orderBy='email').execute()
    users = results.get('users', [])
    # paginate results
    next = results.get('nextPageToken', [])
    while(next):
        results = service.users().list(customer='my_customer', maxResults=100,
                                       orderBy='email', pageToken=next).execute()
        u = results.get('users', [])
        users = users + u
        next = results.get('nextPageToken', [])

    # seperate users into staff and students according to Org Unit
    students= []
    staff = []
    for user in users:
        orgUnit = user['orgUnitPath'].lower()
        if('/staff' == orgUnit):
            staff.append(user)
        if('student' in orgUnit):
            students.append(user)

    # get all FreshService requesters
    all_requesters = FS.all_requesters()

    # figure out which student accounts are already created
    student_emails = []
    for student in students:
        student_emails.append(student['primaryEmail'].lower())

    found_students = []
    for requester in all_requesters:
        if(str(requester['primary_email']).lower() in student_emails):
            found_students.append(requester['primary_email'])

    # figure out which staff accounts are already created
    staff_emails = []
    for s in staff:
        staff_emails.append(s['primaryEmail'].lower())

    found_staff = []
    for requester in all_requesters:
        if(str(requester['primary_email']).lower() in staff_emails):
            found_staff.append(requester['primary_email'])

    # create lists of google users who need to be created
    not_found_staff = []
    for s in staff:
        if(s['primaryEmail'] not in found_staff):
            not_found_staff.append(s)

    not_found_students = []
    for s in students:
        if(s['primaryEmail'] not in found_students):
            not_found_students.append(s)

    # create FreshService users and add to proper requester group
    FS_students = 17000090911
    FS_staff = 17000056500
    for user in not_found_staff:
        new_requester = {
            'first_name': user['givenName'],
            'last_name': user['familyName'],
            'primary_email': user['primaryEmail']
        }
        u = FS.create_requester(new_requester)
        FS.add_groupMember(FS_staff, u['id'])

    for user in not_found_students:
        new_requester = {
            'first_name': user['givenName'],
            'last_name': user['familyName'],
            'primary_email': user['primaryEmail']
        }
        u = FS.create_requester(new_requester)
        FS.add_groupMember(FS_students, u['id'])

        
if __name__ == '__main__':
    main()
