# Json2Xls
This application helps to quickly grab the Application Policies JSON file from a Tetration Cluster and convert it into Excel XLS file for reporting purpose. You can have an option to download the Policies JSON file and convert it.

## Table of contents
* [Installation](#Installation)
* [Screenshots](#screenshots)
* [How to Use](#UserGuide)
* [Files](#Files)
* [Steps to run](#Steps)
* [Feedback and Author](#Feedback)

## Installation

From sources

Download the sources from [Github](https://github.com/leeahnduk/Json2xls.git), extract and execute the following commands

```
$ pip3 install -r requirements.txt

```

## Screenshots
![Run screenshot](https://github.com/leeahnduk/Json2xls/blob/master/Result1.jpg)
![Run screenshot](https://github.com/leeahnduk/Json2xls/blob/master/Result2.jpg)

## UserGuide
How to use this application:
To access to the cluster you need to get the API Credentials with the following permissions
* `sensor_management` - option: SW sensor management: API to configure and monitor status of SW sensors
* `hw_sensor_management` - option: HW sensor management: API to configure and monitor status of HW sensors
* `flow_inventory_query` - option: Flow and inventory search: API to query flows and inventory items in Tetration cluster
* `user_role_scope_management` - option: Users, roles and scope management: API for root scope owners to read/add/modify/remove users, roles and scopes
* `app_policy_management` - option: 
 Applications and policy management: API to manage applications and enforce policies

Download the api_credentials.json locally and have it ready to get the information required for the setup.

A quick look for the help will list the current available options.
* To start the script, just use: `python3 json2xls.py --url https://Cluster-IP --credential api_credentials.json --policies policies.json`
* Or if you want to connect to Tetration Cluster to download the App policy, use this: `python3 json2xls.py --url https://Cluster-IP --credential api_credentials.json`


## Files
Need to prepare Tetration Policies JSON file. The sample Tetration Policies JSON file is in the github folder.


## Steps

Step 1: Issue `$ pip3 install -r requirements.txt` to install all required packages.

Step 2: To run the apps: `python3 json2xls.py --url https://Cluster-IP --credential api_credentials.json --policies policies.json`

Step 3: Answer all the questions about scope and application name to import to your cluster.


## Feedback
Any feedback can send to me: Chris McHenry (https://github.com/cmchenr), I just changed some items to connect to cluster easier.
