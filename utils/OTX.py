import os
import requests
from collections import Counter
from dotenv import load_dotenv
import json

load_dotenv()

def query_otx_api(ioc_type, ioc_value):
    api_key = os.getenv('OTX_API')
    ioc_type_mapping = {
        'ip': 'IPv4',
        'domain': 'domain',
        'hash': 'file'
    }
    ioc_type_api = ioc_type_mapping.get(ioc_type, ioc_type)
    base_url = 'https://otx.alienvault.com/api/v1/indicators'
    endpoint = f'{base_url}/{ioc_type_api}/{ioc_value}/general'
    headers = {
        'X-OTX-API-KEY': api_key
    }

    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        pulses = data["pulse_info"].get("pulses", [])
        if pulses:
            pulse = pulses[0]
            name = pulse.get("name", "")
            description = pulse.get("description", "")
            tags = pulse.get("tags", [])
            references = pulse.get("references", [])
            malware_families_ids = [mf["id"] for mf in pulse.get("malware_families", [])]
            attack_ids_display_names = [aid["display_name"] for aid in pulse.get("attack_ids", [])]
        else:
            name = description = ""
            tags = references = malware_families_ids = attack_ids_display_names = []

        extracted_data = {
            "source": "OTX AlienVault",
            "url": f"https://otx.alienvault.com/indicator/{ioc_type}/{ioc_value}",
            "reputation": data.get("reputation", ""),
            "count": data["pulse_info"].get("count", 0),
            "name": name,
            "description": description,
            "tags": tags,
            "references": references,
            "malware_families_ids": malware_families_ids,
            "attack_ids_display_names": attack_ids_display_names
        }
        return json.dumps(extracted_data, indent=4)
    else:
        return f'Error: {response.status_code}'