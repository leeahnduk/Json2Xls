from tetpyclient import RestClient
from builtins import input
import tetpyclient
import json
import requests.packages.urllib3
import sys
import os
import argparse
import time
import csv
from columnar import columnar


CEND = "\33[0m"     #End
CGREEN = "\33[32m"  #Information
CYELLOW = "\33[33m" #Request Input
CRED = "\33[31m"    #Error
URED = "\33[4;31m" 
Cyan = "\33[0;36m"  #Return

# =================================================================================
# See reason below -- why verify=False param is used
# python3 downloadAppsPolicies.py --url https://192.168.30.4/ --credential dmz_api_credentials.json
# feedback: Le Anh Duc - anhdle@cisco.com
# =================================================================================
requests.packages.urllib3.disable_warnings()


parser = argparse.ArgumentParser(description='Tetration Get an App detail and create JSON file for the detail')
parser.add_argument('--url', help='Tetration URL', required=True)
parser.add_argument('--credential', help='Path to Tetration json credential file', required=True)
args = parser.parse_args()


def CreateRestClient():
    """create REST API connection to Tetration cluster
    Returns:
        REST Client
    """
    rc = RestClient(args.url,
                    credentials_file=args.credential, verify=False)
    return rc

def GetApps(rc):
    resp = rc.get('/applications')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve Apps list" + CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()


def ShowApps(Apps):
    AppsList = []
    headers = ['Number', 'App Name', 'Author', 'App ID', 'Primary?']
    for i,app in enumerate(Apps): AppsList.append([i+1,app["name"] , app['author'], app["id"], app['primary']])
    table = columnar(AppsList, headers, no_borders=False)
    print(table)


def selectTetApps(apps):
    # Return App IDa for one or many Tetration Apps that we choose
    print (Cyan + "\nHere are all Application workspaces in your cluster: " + CEND)
    ShowApps(apps)
    choice = input('\nSelect which Tetration Apps (Number, Number) above you want to download polices: ')

    choice = choice.split(',')
    appIDs = []
    for app in choice:
        if '-' in app:
            for app in range(int(app.split('-')[0])-1,int(app.split('-')[1])):
                appIDs.append(resp.json()[int(app)-1]['id'])
        else:
            appIDs.append(apps[int(app)-1]['id'])
    return appIDs

def downloadPolicies(rc,appIDs):
    # Download Policies JSON files from Apps workspace
    apps = []
    for appID in appIDs:
        print('Downloading app details for '+appID + "into json file")
        apps.append(rc.get('/openapi/v1/applications/%s/details'%appID).json())
        #json_object = json.load(apps)
    for app in apps:
        with open('./'+app['name'].replace('/','-')+'.json', "w") as config_file:
            json.dump(apps, config_file, indent=4)
            print(app['name'].replace('/','-')+".json created") 


def main():
    rc = CreateRestClient()
    apps = GetApps(rc)
    appIDs = selectTetApps(apps)
    downloadPolicies(rc, appIDs)


if __name__ == "__main__":
    main()