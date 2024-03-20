import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def query_shodan_api(ioc_type, ioc_value):
    api_key = os.getenv('SHODAN_API')
    base_url = 'https://api.shodan.io'

    if ioc_type == 'ip':
        endpoint = f'{base_url}/shodan/host/{ioc_value}?key={api_key}&history=true'
    elif ioc_type == 'domain':
        endpoint = f'{base_url}/dns/resolve?hostnames={ioc_value}&key={api_key}'
    else:
        return 'Invalid IOC type. Must be "ip" or "domain".'

    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        if ioc_type == 'ip':
            # Extract the required information for IP
            tags = data.get("tags", [])
            domains = data.get("domains", [])
            hostnames = data.get("hostnames", [])
            org = data.get("org", "")
            operating_system = data.get("os", "")  # renamed 'os' to 'operating_system'
            ports = data.get("ports", [])

            extracted_data = {
                "source": "Shodan",
                "url": f"https://www.shodan.io/host/{ioc_value}",
                "tags": tags,
                "domains": domains,
                "hostnames": hostnames,
                "org": org,
                "operating_system": operating_system,
                "ports": ports
            }
        elif ioc_type == 'domain':
            # Extract the required information for domain
            ip_address = data.get(ioc_value, "")

            extracted_data = {
                "source": "Shodan",
                "url": f"https://www.shodan.io/host/{ip_address}",
                "ip_address": ip_address
            }
        return json.dumps(extracted_data, indent=4)
    else:
        print(f'Response text: {response.text}')
        return f'Error: {response.status_code}'