import tetpyclient
import json
import requests.packages.urllib3
import sys
import os
import xlsxwriter
import argparse
import time
import csv

from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from builtins import input
from columnar import columnar

from tetpyclient import RestClient
from tqdm import tqdm as progress
from terminaltables import AsciiTable
import urllib3

CEND = "\33[0m"     #End
CGREEN = "\33[32m"  #Information
CYELLOW = "\33[33m" #Request Input
CRED = "\33[31m"    #Error
URED = "\33[4;31m" 
cyan = "\33[0;36m"  #Return

# =================================================================================
# See reason below -- why verify=False param is used
# python3 app2xls.py --url https://10.71.129.30/ --credential Japan_api_credentials.json
# feedback: Le Anh Duc - anhdle@cisco.com
# =================================================================================
requests.packages.urllib3.disable_warnings()


parser = argparse.ArgumentParser(description='Tetration Create Policy under Apps')
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

def GetAppsId(Apps, name):
    try:
        for app in Apps: 
            if name == app["name"]: return app["id"]
    except:
        print(URED + "Failed to retrieve App ID "+ CEND)

def ShowApps(Apps):
    AppsList = []
    headers = ['Number', 'App Name', 'Author', 'App ID', 'Primary?']
    for i,app in enumerate(Apps): AppsList.append([i+1,app["name"] , app['author'], app["id"], app['primary']])
    table = columnar(AppsList, headers, no_borders=False)
    print(table)

def GetApplicationScopes(rc):
    resp = rc.get('/app_scopes')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve app scopes")
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def resolveFilter(rc, filters):# return all IP and hosts for a specific filters
    ipSet = []
    body = json.dumps({'filter':filters['query']})
   
    resp = rc.post('/inventory/search',json_body=body)
    if resp:
        ips = resp.json()
        for i in ips['results']:
            ipSet.append(i['ip'])

    return ipSet

def GetAppScopeId(scopes,name):
    try:
        return [scope["id"] for scope in scopes if scope["name"] == name][0]
    except:
        print(URED + "App Scope {name} not found".format(name=name))

def ShowScopes(scopes):
    ScopesList = []
    headers = ['Number', 'Scope Name', 'Scope ID', 'VRF ID']
    for i,scope in enumerate(scopes): ScopesList.append([i+1,scope["name"] , scope["id"], scope['vrf_id']])
    table = columnar(ScopesList, headers, no_borders=False)
    print(table)

def GetPolicies(rc, app_id):
    
    resp = rc.get('/applications/' + app_id + '/policies')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve Policies list")
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def getDefaultDetail(rc, id):
    resp = rc.get('/applications/'+ id + '/default_policies')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve Default Policies from your Apps"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json() 

def getAbsoluteDetail(rc, id):
    resp = rc.get('/applications/'+ id + '/absolute_policies')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve Absolute Policies from your Apps"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json() 

def getCatchAllDetail(rc, id):
    resp = rc.get('/applications/'+ id + '/catch_all')
    if resp.status_code != 200:
        print(URED + "Failed to retrieve catch_all Policy from your Apps"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def selectTetApps(apps):
    # Return App IDa for one or many Tetration Apps that we choose
    print (cyan + "\nHere are all Application workspaces in your cluster: " + CEND)
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
    return apps


def GetAppVersions(rc, appid):
    resp = rc.get('/applications/' + appid + '/versions')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve list of versions for your app" + CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def GetLatestVersion(app_versions):
    try:
        for vers in app_versions: 
            if "v" in vers["version"]: return vers["version"]
    except:
        print(URED + "Failed to retrieve latest app version"+ CEND)

def getAppDetail(rc, id):
    resp = rc.get('/applications/'+ id)

    if resp.status_code != 200:
        print(URED + "Failed to retrieve App detail"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json() 

def GetPolicies(rc, app_id):
    
    resp = rc.get('/applications/' + app_id + '/policies')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve Policies list"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def GetInventoriesId(inventories, name):
    try:
        for inv in inventories:
            if name == inv["name"]:
                print (cyan + "\nHere is your Inventory ID: " + inv["id"] + Cend)
                return inv["id"]
            else: continue
    except:
        print(URED + "Inventory {name} not found".format(name=name)) 

def GetInventoriesNamewithID(inventories):
    inventoriesList = []
    try:
        for inv in inventories: 
            inventoriesList.append([inv["name"] , inv["id"]])
        return inventoriesList
    except:
        print(URED + "Failed to retrieve inventories name with ID list"+ CEND) 


def GetInventories(rc):
    resp = rc.get('/filters/inventories')

    if resp.status_code != 200:
        print(URED + "Failed to retrieve inventories list"+ CEND)
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def filterToString(invfilter):
    if 'filters' in invfilter.keys():
        query=[]
        for x in invfilter['filters']:
            if 'filters' in x.keys():
                query.append(filterToString(x))
            elif 'filter' in x.keys():
                query.append(x['type'] + filterToString(x['filter']))
            else:
                query.append(x['field'].replace('user_','*')+ ' '+ x['type'] + ' '+ str(x['value']))
        operator = ' '+invfilter['type']+' '
        return '('+operator.join(query)+')'
    else:
        return invfilter['field']+ ' '+ invfilter['type'] + ' '+ str(invfilter['value'])

def GetInventoriesId(inventories, name):
    try:
        for inv in inventories:
            if name == inv["name"]:
                print (cyan + "\nHere is your Inventory ID: " + inv["id"])
                return inv["id"]
            else: continue
    except:
        print(URED + "Inventory {name} not found".format(name=name))


def GetAppScopeName(scopes,id):
    try:
        return [scope["name"] for scope in scopes if scope["id"] == id][0]
    except:
        print("App Scope {id} not found".format(name=name)) 

def ShowApplicationScopes(scopes):
    """
        List all the Scopes in Tetration Appliance
        Scope ID | Name | Policy Priority | Query | VRF ID | Parent Scope ID | Root Scope ID | Created At | Updated At
        """
    headers = ['Scope ID', 'Name', 'Policy Priority', 'Query', 'VRF ID', 'Parent Scope ID', 'Root Scope ID', 'Created At', 'Updated At']
    data_list = []
    for x in scopes: data_list. append([x['id'],
                    x['name'],
                    x['policy_priority'],
                    x['short_query'],
                    x['vrf_id'],
                    x['parent_app_scope_id'],
                    x['root_app_scope_id'],
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x['created_at'])),
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x['updated_at']))])
    table = columnar(data_list, headers, no_borders=False)
    print(table)

def GetVRFs(rc):
    # Get all VRFs in the cluster
    resp = rc.get('/vrfs')

    if resp.status_code != 200:
        print("Failed to retrieve app scopes")
        print(resp.status_code)
        print(resp.text)
    else:
        return resp.json()

def ShowVRFs(vrfs):
    """
        List all the Apps in Tetration Appliance
        VRF ID | Created At | Updated At | Name | Tenant name | Root Scope ID
        """
    data_list = []
    headers = ['VRF ID', 'Created At', 'Updated At', 'Name', 'Tenant Name', 'Root Scope ID']
    for x in vrfs: 
        data_list.append([x['id'], time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(x['created_at'])), time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(x['updated_at'])), x['name'], x['tenant_name'], x['root_app_scope_id']]) 
    table = columnar(data_list, headers, no_borders=False)
    print(table)

def GetRootScope(vrfs):
    #return list of Root Scopes and its' names
    rootScopes = []
    headers = ['Root Scope Name', 'VRF ID']
    for vrf in vrfs:
        rootScopes.append([vrf["name"] , vrf["vrf_id"]])
    table = columnar(rootScopes, headers, no_borders=False)
    print(table)

def GetAllSubScopeNames(scopes, name):
    subScopeNames = []
    try:
        for scope in scopes: 
            if name in scope["name"]:
                subScopeNames.append(scope["name"])
            else: continue
        return subScopeNames
    except:
        print(URED + "App Scope {name} not found".format(name=name))

def convApps2xls(rc):
    AllApps = GetApps(rc)
    scopes = GetApplicationScopes(rc)
    apps = []
    appIDs = selectTetApps(AllApps)
    apps.append(downloadPolicies(rc, appIDs))
    #print (json.dumps(apps, indent=4))

    # Load in the IANA Protocols
    protocols = {}
    try: 
        with open('protocol-numbers-1.csv') as protocol_file:
            reader = csv.DictReader(protocol_file)
            for row in reader:
                protocols[row['Decimal']]=row
    except IOError:
        print('%% Could not load protocols file')
        return
    except ValueError:
        print('Could not load improperly formatted protocols file')
        return
    
    for app in apps[0]:
        workbook = xlsxwriter.Workbook(app['name'].replace('/','-')+'.xlsx')
        bold = workbook.add_format({'bold': True})

        if 'clusters' in app.keys():
            worksheet = workbook.add_worksheet(name='App Servers')
            cell_format = workbook.add_format()
            cell_format.set_bg_color('cyan')
            cell_format.set_bold()
            cell_format.set_font_color('black')
            worksheet.set_row(0, None)
            worksheet.write_row(0,0,['Hostname','IP','Cluster Membership'],cell_format)
            i=1
            clusters = app['clusters']
            for cluster in clusters:
                hosts = []
                for node in cluster['nodes']:
                    hosts.append(node['name'])
                    worksheet.write_row(i,0,[node['name'],node['ip'],cluster['name']])
                    i+=1
            worksheet.set_column(0, 0, 30)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 30)

        if 'inventory_filters' in app.keys():
            i=1
            worksheet = workbook.add_worksheet(name='External Groups')
            cell_format = workbook.add_format()
            cell_format.set_text_wrap()
            header_format = workbook.add_format()
            header_format.set_bg_color('cyan')
            header_format.set_bold()
            header_format.set_font_color('black')
            worksheet.set_row(0, None)
            worksheet.write_row(0,0,['Inventory Filter Name', 'IP Addresses', 'Filter Definition'],header_format)
            worksheet.set_column(0, 0, 30)
            worksheet.set_column(1, 1, 60, cell_format)
            worksheet.set_column(2, 2, 50, cell_format)

            filters = app['inventory_filters']
            for invfilter in filters:
                #print (json.dumps(invfilter, indent=4))
                ipSet = resolveFilter(rc, invfilter)
                #print (ipSet)
                worksheet.write_row(i,0,[invfilter['name'], str(ipSet), filterToString(invfilter['query'])])
                i+=1

        if 'default_policies' in app.keys():
            i=1
            worksheet = workbook.add_worksheet(name='Policies')
            header_format = workbook.add_format()
            header_format.set_bg_color('cyan')
            header_format.set_bold()
            header_format.set_font_color('black')
            worksheet.set_row(0, None)
            worksheet.write_row(0,0,['Consumer Group','Provider Group','Services'],header_format)
            worksheet.set_column(0, 0, 30)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 30)

            policies = app['default_policies']
            for policy in policies:
                pols = {}
                for rule in policy['l4_params']:
                    if 'port' in rule:
                        if rule['port'][0] == rule['port'][1]:
                            port = str(rule['port'][0])
                        else:
                            port = str(rule['port'][0]) + '-' + str(rule['port'][1])
                    else:
                        port = None

                    if port == None:
                        try:
                            pols[protocols[str(rule['proto'])]['Keyword']] = []
                        except:
                            pols['PROTO-'+str(rule['proto'])]=[]
                    elif protocols[str(rule['proto'])]['Keyword'] in pols.keys():
                        pols[protocols[str(rule['proto'])]['Keyword']].append(port)
                    else:
                        pols[protocols[str(rule['proto'])]['Keyword']] = [port]

                policy_list = []
                for key, val in pols.items():
                    #print(key,val)
                    if len(val)>0:
                        policy_list.append('{}={}'.format(key,', '.join(val)))
                    else:
                        policy_list.append(key)
                        
                worksheet.write_row(i,0,[policy["consumer_filter_name"],policy["provider_filter_name"],'; '.join(policy_list)])
                i+=1
        
        workbook.close()
        print (app['name'].replace('/','-')+'.xlsx created for policies conversion to CSV')


def main():
    rc = CreateRestClient()
    convApps2xls(rc)
    		

if __name__ == "__main__":
	main()