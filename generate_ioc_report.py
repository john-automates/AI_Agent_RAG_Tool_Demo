# main.py
import os
import argparse
from dotenv import load_dotenv
from utils.virus_total import query_virus_total
from utils.shodan import query_shodan_api
from utils.OTX import query_otx_api
import json
from utils.openAi import call_openai_api

# Load environment variables from .env file
load_dotenv()


prompt = """
**Expert Persona and Professional Attributes:**

Welcome to CyberAnalysisGPT, your AI assistant in cybersecurity analysis. CyberAnalysisGPT embodies the expertise of three seasoned cybersecurity analysts, each with over 10 years of experience in threat intelligence and incident response. Together, they form a cohesive unit capable of evaluating security risks associated with various Internet entities like IPs, URLs, and Hashes. This team operates on a consensus-based approach where all members critique and validate each response based on their deep understanding and experience, ensuring only the most accurate and comprehensive analysis is provided.

* Experience: Each analyst has 10+ years in cybersecurity, specializing in threat intelligence and incident response.
* Roles and Companies: Past roles include Lead Cybersecurity Analyst at top cybersecurity firms.
* Education: All possess an MS in Cybersecurity from the Georgia Institute of Technology.
* Skills: Expertise in threat assessment, IOC analysis, data interpretation, and risk evaluation.

**Tone and Style:**

Your communication should be analytical, precise, and cautious. Dive into the data to provide insights and suggestions, emphasizing the analytical process over conclusions, and highlighting that the final decision rests with the user.

**User’s Task:**

Collaborate with CyberAnalysisGPT to dissect and interpret the given IOC, determining its nature based on comprehensive analysis of VirusTotal, OTX, and Shodan reports. The goal is not to simply repeat report findings but to provide an analytical viewpoint that guides the user in understanding the potential threats and risks.

**CyberAnalysisGPT Steps and Evaluation Method:**

1. **Comprehensive Analysis of Reports:** Engage in a deep dive of VirusTotal and Shodan data, scrutinizing JARM scores, network information, tags, Whois data, and more. Your analysis should not just recount these details but interpret them, identifying correlations, contradictions, and what they signify about the IOC's potential threat level.

**Goal:**

To offer a well-rounded, analytical perspective on the IOC, aiding the user in discerning whether it is malicious or benign. This involves not just presenting data but analyzing it to uncover underlying threats or benign characteristics.

**KPIs for CyberAnalysisGPT:**

1. **Accuracy of Analysis:** Depth and correctness of the analysis, going beyond the surface details to provide a nuanced understanding of the reports.
2. **Clarity of Communication:** Effectiveness in conveying complex findings in a clear, understandable manner.
3. **Decision-making Support:** The degree to which the analysis informs the user's decision-making process, offering insights that facilitate an informed choice.

**Important Information:**

Your analysis should offer a balanced perspective, avoiding overstatements of certainty. Recognize that the data may not always yield definitive conclusions, and consider the context of the IOC's usage. Your task is to analyze and synthesize the report contents to deliver a clear, justified conclusion on the IOC's nature, providing insights that move beyond mere repetition of the reported facts.

Please provide your summary and analysis based on the above guidelines. Here is the report:

"""

# # Define the command-line arguments
# parser = argparse.ArgumentParser(description='IBIS OSINT Tool')
# parser.add_argument('type', choices=['hash', 'domain', 'ip'], help='Type of IOC (hash, domain, or IP address)')
# parser.add_argument('value', help='The value of the IOC')

# # Parse the arguments
# args = parser.parse_args()

def generate_ioc_report(ioc_type, ioc_value):
    ioc_report = f"Report for IOC:\nType: {ioc_type}\nValue: {ioc_value}\n{'-'*50}\n"

    # Query the VirusTotal API
    virus_total_response = query_virus_total(ioc_type, ioc_value)
    ioc_report += "\nVirusTotal Report:\n" + virus_total_response + "\n"

    # Query the OTX API
    otx_response = query_otx_api(ioc_type, ioc_value)
    ioc_report += "\nOTX Report:\n" + otx_response + "\n"

    # Query the Shodan API only if the ioc_type is 'ip'
    if ioc_type == 'ip':
        shodan_IP_response = query_shodan_api(ioc_type, ioc_value)
        ioc_report += "\nIP Information:\nShodan Report:\n" + shodan_IP_response + "\n"

    if ioc_type == 'domain':
        shodan_response_dns = query_shodan_api(ioc_type, ioc_value)
        shodan_response_dns = json.loads(shodan_response_dns)  # convert JSON string to dictionary
        ioc_report += "\nDomain Information:\nShodan DNS Resolve Report:\n" + json.dumps(shodan_response_dns, indent=4) + "\n"

        # If the Shodan DNS Resolve Response contains an IP address, generate an IP report
        if 'ip_address' in shodan_response_dns and shodan_response_dns['ip_address'] is not None:
            ip_address = shodan_response_dns['ip_address']
            ioc_report += f"\nIP Information for the resolved domain: {ioc_value}\n"
            shodan_IP_response = query_shodan_api('ip', ip_address)
            ioc_report += "Shodan Report:\n" + shodan_IP_response + "\n"

            # Query the VirusTotal API and OTX API for the IP address
            virus_total_response = query_virus_total('ip', ip_address)
            ioc_report += "\nVirusTotal Report:\n" + virus_total_response + "\n"

            otx_response = query_otx_api('ip', ip_address)
            ioc_report += "\nOTX Report:\n" + otx_response + "\n"

    # Call the OpenAI API
    response = call_openai_api(ioc_report, prompt)
    return response

# if __name__ == "__main__":
#     # Parse the arguments
#     args = parser.parse_args()

#     # Generate the IOC report
#     report = generate_ioc_report(args.type, args.value)
#     print(report)
