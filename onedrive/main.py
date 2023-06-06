
import json
import requests
from darkshield import Darkshield
import os, shutil
import argparse

credentials = open("config.json", 'r')
json_creds = json.loads(credentials.read())
credentials.close()
access_token = ""
tenant_id = json_creds["TenantID"]
client_id = json_creds["ClientID"]
client_secret = json_creds["ClientSecret"]
username = json_creds["Username"]
LOGIN_URI = "https://login.microsoftonline.com/{tenantID}/oauth2/v2.0/token".format(tenantID=tenant_id)
Graph_URL = "https://graph.microsoft.com/v1.0"

def remove_tmp_directory_folders():
    for folder in os.listdir("./tmp"):
        folder_path = os.path.join("./tmp", folder)
        try:
            if os.path.isfile(folder_path) or os.path.islink(folder_path):
                os.unlink(folder_path)
            elif os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            print("Failed to delete folder: "+folder)


def get_token():
    headers = {
        'Host': 'login.microsoftonline.com',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    body = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'tenant': tenant_id
    }

    response = requests.post(url=LOGIN_URI, headers=headers, data=body)
    response.raise_for_status()
    response_body = response.json()
    access_token = 'Bearer ' + response_body['access_token']
    return access_token




def get_user_id(access_headers):
    user_id_url = Graph_URL+"/users?$filter=userPrincipalName eq '{username}'".format(username=username)
    response_user_id = requests.get(url=user_id_url, headers=access_headers)
    response_body = response_user_id.json()
    user_values = response_body["value"]
    ids = []
    for user in user_values:
        id = user["id"]
        ids.append(id)
    return ids


def get_drive_id(user_id, access_headers):
    drives_url = Graph_URL+"/users/"+user_id+"/drives"
    response_drives_id = requests.get(url=drives_url, headers=access_headers)
    response_body  = response_drives_id.json()
    drive_values  = response_body["value"]
    ids = []
    for drive in drive_values:
        drive_id = drive["id"]
        ids.append(drive_id)
    return ids

def handle_file(drive_id, access_headers, relative_path, filename):
    tempfile_name = "tmp/"+relative_path
    os.makedirs(os.path.dirname(tempfile_name), exist_ok=True)
    file = open(tempfile_name, mode="+wb")
    content_url =  Graph_URL+"/drives/"+drive_id+"/root:/"+relative_path+":/content"
    response_items = requests.get(url=content_url, headers=access_headers)
    file.write(response_items.content)
    file.close()
    file_path = tempfile_name
    Darkshield.call_darkshield(file_path, filename)
    upload_file(drive_id=drive_id, file_path=file_path, access_headers=access_headers, relative_path=relative_path, filename=filename)
    os.remove(tempfile_name)
    
    
    
def upload_file(drive_id, file_path, access_headers, relative_path, filename):
    content_url = Graph_URL +"/drives/" + drive_id + "/root:/" + relative_path + ":/content"
    with open(file_path, 'rb') as f:
        data = f.read()
    requests.put(url=content_url, headers=access_headers, data=data)
    f.close()

def list_children_drive_items(drive_id, access_headers):
    items_url = Graph_URL +"/drives/" + drive_id + "/items/root/children"
    response_items = requests.get(url=items_url, headers=access_headers)
    response_body = response_items.json()
    values  = response_body["value"]
    for value in values:
        name = value["name"]
        if "file" in name:
            list_children_drive_items_from_path(drive_id=drive_id, access_headers=access_headers, relative_path=name)
        else:
            handle_file(drive_id=drive_id, access_headers=access_headers, relative_path=name, filename=name)
    

def list_children_drive_items_from_path(drive_id, access_headers, relative_path):
    items_url = Graph_URL +"/drives/" + drive_id + "/root:/"+ relative_path + ":/children"
    try:
        response_items = requests.get(url=items_url, headers=access_headers)
        response_items.raise_for_status()
        response_body = response_items.json()
        values  = response_body["value"]
        for value in values:
            name = value["name"]
            full_path = relative_path + "/" + name
            if value["file"] is None:
                list_children_drive_items_from_path(drive_id=drive_id, access_headers=access_headers, relative_path=full_path)
            else:
                handle_file(drive_id=drive_id, access_headers=access_headers, relative_path=full_path, filename=name)
    except requests.exceptions.HTTPError as error:
        raise SystemExit(error)




def main():
    parser = argparse.ArgumentParser(description='Demo for OneDrive.')
    parser.add_argument('subfolder', nargs='?', type=str, default='',
                        help="Prefix e.g.(folder1/folder2)")
    args = parser.parse_args()
    subfolder = args.subfolder
    relative_path = subfolder
    access_token = get_token()
    access_headers = {
        "Authorization": access_token
    }
    user_ids = get_user_id(access_headers=access_headers)
    for user_id in user_ids:
        drive_ids = get_drive_id(user_id=user_id, access_headers=access_headers)
        if relative_path == '':
            for drive_id in drive_ids:
                list_children_drive_items(drive_id=drive_id, access_headers=access_headers)
        else:
            for drive_id in drive_ids:
                list_children_drive_items_from_path(drive_id=drive_id, access_headers=access_headers, relative_path=relative_path)
        remove_tmp_directory_folders()

main()

