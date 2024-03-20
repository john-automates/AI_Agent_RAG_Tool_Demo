import requests
import os
import json
from collections import Counter
from datetime import datetime

def query_virus_total(ioc_type, ioc_value):
    # Get the API key from environment variables
    api_key = os.getenv('VIRUS_TOTAL_API')  # Changed from 'VIRUS_TOTAL_API_KEY' to 'VIRUS_TOTAL_API'

    # Map the ioc_type values to the correct strings for the API
    ioc_type_mapping = {
        'ip': 'ip_addresses',
        'domain': 'domains',
        'hash': 'files'
    }

    # Get the correct ioc_type for the API
    ioc_type_api = ioc_type_mapping.get(ioc_type, ioc_type)

    # Construct the URL based on the IOC type and value
    url = f"https://www.virustotal.com/api/v3/{ioc_type_api}/{ioc_value}"

    # Set the headers with the API key and accept header
    headers = {
        'x-apikey': api_key,
        'accept': 'application/json'
    }

   # Make the GET request and get the response
    response = requests.get(url, headers=headers)

    # Get the JSON data from the response
    vt_data = response.json()
    if 'data' in vt_data and 'attributes' in vt_data['data']:
        attributes = vt_data['data']['attributes']

        if ioc_type == 'ip':
            last_analysis_results = {
                vendor: data.get('result') for vendor, data in attributes.get('last_analysis_results', {}).items()
            }
            result_counts = dict(Counter(last_analysis_results.values()))

            extracted_values = {
                "source": "VirusTotal",
                "url": f"https://www.virustotal.com/gui/{ioc_type}-address/{ioc_value}",
                #'JARM': attributes.get('jarm'),
                'Network Information': attributes.get('network'),
                'Tags': attributes.get('tags'),
                'Whois Data': attributes.get('whois'),
                'Result Counts': result_counts,
                'Reputation Score': attributes.get('reputation'),
                'HTTPS Certificate Information': attributes.get('last_https_certificate'),
                'ASN (Autonomous System Number)': attributes.get('asn'),
                'Total Votes': attributes.get('total_votes')
            }
            return json.dumps(extracted_values, indent=4)

        elif ioc_type == 'domain':
            extracted_values = {
                "source": "VirusTotal",
                "url": f"https://www.virustotal.com/gui/{ioc_type}/{ioc_value}",
                "whois": attributes.get("whois"),
                "last_analysis_date": datetime.utcfromtimestamp(attributes.get("last_analysis_date")).strftime('%Y-%m-%d %H:%M:%S') if attributes.get("last_analysis_date") else None,
                "last_dns_records_date": datetime.utcfromtimestamp(attributes.get("last_dns_records_date")).strftime('%Y-%m-%d %H:%M:%S') if attributes.get("last_dns_records_date") else None,
                "last_analysis_stats": attributes.get("last_analysis_stats"),
                "whois_date": datetime.utcfromtimestamp(attributes.get("whois_date")).strftime('%Y-%m-%d %H:%M:%S') if attributes.get("whois_date") else None,
                "reputation": attributes.get("reputation"),
                "total_votes": attributes.get("total_votes"),
                "links": attributes.get("links")
            }
            return json.dumps(extracted_values, indent=4)

    # If 'data' or 'attributes' is not in vt_data, or if ioc_type is not 'ip' or 'domain', return an error message
    return "Error: Unexpected API response"