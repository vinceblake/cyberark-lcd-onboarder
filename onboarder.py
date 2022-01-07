import requests
import json
import keyring

# Ignore SSL cert warnings from requests module?
require_ssl_verify = True
if require_ssl_verify is False:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# EPM Variables
epm_auth_base_url = "https://login.epm.cyberark.com"
epm_api_base_url = "https://EXAMPLE.epm.cyberark.com"
epm_username = "EXAMPLE@cyberark.com"
epm_password = keyring.get_password("CyberArk","epm")
epm_set_id = keyring.get_password("CyberArk","epm_set_id")

# PVWA Variables
pvwa_auth_type = "LDAP"
domain_suffix = ".cybr.com" # Begin with a .
pvwa_base_url = "https://comp01.cybr.com"
pvwa_auth_type = "ldap"
pvwa_username = "Mike"
pvwa_password = keyring.get_password("CyberArk","pvwa")
pvwa_safe_name = "Windows LCD"
pvwa_platform_id = "WinLooselyDevice"

# EPM Functions
def epm_auth(username, password):
    url = f"{epm_auth_base_url}/EPM/API/Auth/EPM/Logon"

    payload = json.dumps({
    "Username": username,
    "Password": password,
    "ApplicationID": "Onboarder"
    })

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['EPMAuthenticationResult']
    headers['Authorization'] = f"basic {token}"
    return headers

def epm_get_sets(headers):
    url = f"{epm_api_base_url}/EPM/API/Sets"
    response = requests.request("GET", url, headers=headers)
    sets = json.dumps(response.json(), indent=4, sort_keys=True)
    return sets

def epm_get_computers(headers,set_id):
    url = f"{epm_api_base_url}/EPM/API/Sets/{set_id}/Computers"
    response = requests.request("GET", url, headers=headers)
    computers = [x['ComputerName'] for x in response.json()['Computers']]
    return computers

# PVWA Functions
def pvwa_auth(auth_type, username, password):
    auth_type = pvwa_auth_type.lower()
    if auth_type == "cyberark":
        url = f"{pvwa_base_url}/PasswordVault/API/Auth/CyberArk/Logon"
    elif auth_type == "ldap":
        url = f"{pvwa_base_url}/PasswordVault/API/Auth/LDAP/Logon"
    elif auth_type == "radius":
        url = f"{pvwa_base_url}/PasswordVault/API/Auth/radius/Logon"
    elif auth_type == "windows":
        url = f"{pvwa_base_url}/PasswordVault/API/Auth/Windows/Logon"
    
    payload = json.dumps({
    "Username": username,
    "Password": password,
    "concurrentSessions": "true"
    })

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=require_ssl_verify)
    headers['Authorization'] = response.json()
    return headers

def pvwa_add_accounts(headers, computers):
    url = f"{pvwa_base_url}/PasswordVault/api/Accounts"
    query_url = f"{url}?search=LCD&searchType=contains&sort=Address&filter=safeName eq {pvwa_safe_name}"
    response = requests.request("GET", query_url, headers=headers, data={}, verify=require_ssl_verify)
    values = response.json()['value']
    already_onboarded = [x['address'].replace(domain_suffix,"") for x in values]
    computers = [x for x in computers if x not in already_onboarded]

    for computer_name in computers:
        computer = f"{computer_name}{domain_suffix}"
        payload = json.dumps({
        "name": f"Windows-LCD-{computer}",
        "address": computer,
        "userName": "Administrator",
        "platformId": pvwa_platform_id,
        "safeName": pvwa_safe_name,
        "secretType": "password",
        "secret": "",
        "secretManagement": {
            "automaticManagementEnabled": True,
        }
        })

        response = requests.request("POST", url, headers=headers, data=payload, verify=require_ssl_verify)
        print(f"{response.text}\n\n")

    print(f"{len(computers)} LCD accounts successfully added to the vault.")

    return response.json()

# Main program
if __name__ == '__main__':
    # EPM: Authentication
    epm_headers = epm_auth(epm_username,epm_password)

    # PVWA: Authentication
    pvwa_headers = pvwa_auth(pvwa_auth_type,pvwa_username,pvwa_password)

    # EPM: Get Sets (used to retrieve value for epm_set_id variable above)
    sets = epm_get_sets(epm_headers)
    print(sets)

    # EPM: Get computers in Set
    #computers = epm_get_computers(epm_headers,epm_set_id)
    
    # PVWA: Add Accounts
    #pvwa_add_accounts(pvwa_headers,computers)
