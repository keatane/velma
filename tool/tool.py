import sys
import requests
import nvdlib
import argparse
import json
from colorama import Fore, Style

# Importing my modules
import search_modules
from pdf import generate_pdf

# Const variable declarations
USAGE = "tool.py [OPTIONS --help] <service_name_1>::<service_type_1>::[configuration_file_1.json] \
<service_name_2>::<service_type_2>::[configuration_file_2.json] ..."
DESCRIPTION = "Description: vulnerability assessment tool that search for CVEs online given the URL, the service type and the correct CPE"
DEFAULT_FILE_TXT="results.txt"

# Searching with nvdlib (more precise for versions)
def search_cve(service_name, service_version):
    try:
        with open("configurations/cpe.json") as f:
            cpe_list = json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}[X] Error: cpe.json file not found, the tool can't search for CVEs without it{Style.RESET_ALL}")
        sys.exit(1)
    cpe = cpe_list[service_name.lower()].replace('*', str(service_version))
    try:
        results = nvdlib.searchCVE(cpeName=cpe)
    except Exception:
        # No CVEs found (e.g. version not found in NVD database)
        return []
    return results

    
def print_cves(cve_list, service_name, service_version, verbose=False):
    if cve_list:
        print("[!] Found CVEs for ", service_name, service_version)
        
        low_count = 0
        medium_count = 0
        high_count = 0
        
        for cve in cve_list:
            # Count occurrences of severity levels
            try:
                severity = cve.v2severity.upper()
            except AttributeError:
                severity = cve.v31severity.upper()
            if severity == "LOW":
                low_count += 1
                print(f"    >>> CVE ID: {cve.id} -- SEVERITY: {Fore.GREEN}{severity}{Style.RESET_ALL}\n")
            elif severity == "MEDIUM":
                medium_count += 1
                print(f"    >>> CVE ID: {cve.id} -- SEVERITY: {Fore.YELLOW}{severity}{Style.RESET_ALL}\n")
            elif severity == "HIGH":
                high_count += 1
                print(f"    >>> CVE ID: {cve.id} -- SEVERITY: {Fore.RED}{severity}{Style.RESET_ALL}\n")

            if verbose:
                print(f"    ==> Description: {cve.descriptions[0].value}")
                print("-" * 30)
        
        print("\n[!] CVE Severity report:")
        print(f"{Fore.GREEN}LOW: {low_count} -- {Fore.YELLOW}MEDIUM: {medium_count} -- {Fore.RED}HIGH: {high_count}{Style.RESET_ALL}\n")
        print("#" * 30 + "\n")
                
    else:
        print("No CVEs found for " + service_name + " " + service_version + "\n")


# Wrapping text to a specific width for better PDF printing
def wrap_text(text, width):
    lines = []
    while len(text) > width:
        split_index = text.rfind(' ', 0, width)
        if split_index == -1:
            split_index = width
        lines.append(text[:split_index].lstrip('\n'))
        text = text[split_index + 1:]
    lines.append(text)
    return lines

def print_cves_to_file(cve_list, service_name, service_version, file_path, line_width=50, verbose=False):
    with open(file_path, 'a') as f:
        if cve_list:
            f.write("[!] Found CVEs for " + service_name + " " + service_version + "\n")

            low_count = 0
            medium_count = 0
            high_count = 0

            for cve in cve_list:
                # Count occurrences of severity levels
                try:
                    severity = cve.v2severity.upper()
                except AttributeError:
                    severity = cve.v31severity.upper()
                if severity == "LOW":
                    low_count += 1
                elif severity == "MEDIUM":
                    medium_count += 1
                elif severity == "HIGH":
                    high_count += 1
                
                f.write(f"    >>> CVE ID: {cve.id} -- SEVERITY: {severity}\n")
                                
                if verbose:
                    descriptions = wrap_text(cve.descriptions[0].value, line_width)
                    f.write("    ==> Description: ")
                    for desc_line in descriptions:
                        f.write(f"      {desc_line}\n")
                    f.write("-" * 50 + "\n")
        
            f.write("\n[!] CVE Severity report:\n")
            f.write(f"LOW: {low_count} -- MEDIUM: {medium_count} -- HIGH: {high_count}\n")
            f.write("#" * 30 + "\n")

        else:
            f.write("No CVEs found for " + service_name + " " + service_version + "\n")

def handle_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)
    parser.add_argument('-v', '--verbose', action='store_true', help='prints detailed information about the CVEs found')
    parser.add_argument('-d', '--deep', action='store_true', help='searches for CVEs related to the server and engine')
    parser.add_argument('-f', '--file', action='store', help='saves the results to a file')
    parser.add_argument('-p', '--pdf', action='store', help='saves the results to a PDF file - note: this will create also a txt file')
    parser.add_argument('services', nargs=argparse.REMAINDER, help='<service_name1>::<service_type1>::[configuration_file_1.json] <service_name2>::<service_type2>::[configuration_file_2.json] ...', default=[])
    args = parser.parse_args()
    if not args.services or len(args.services) == 0:
        print(USAGE)
        sys.exit(1)
    if args.file and not args.file.endswith('.txt'):
        print(f"{Fore.RED}[X] The file name provided is not a .txt file{Style.RESET_ALL}")
        sys.exit(1)
    if args.pdf and not args.pdf.endswith('.pdf'):
        print(f"{Fore.RED}[X] The file name provided is not a .pdf file{Style.RESET_ALL}")
        sys.exit(1)
    return args.verbose, args.deep, args.file, args.pdf, args.services

def get_server_info(url):
    try:
        # Initializing request
        response = requests.get(url)
        if response.status_code != 200:
            print(f"{Fore.RED}[X] Server is not reachable{Style.RESET_ALL}")
            return

        # Extract server name and version
        server_name = None
        server_version = None
        server_header = response.headers.get('Server')
        if server_header:
            print(f"{Fore.CYAN}[*] Printing information about underlayer running providers:{Style.RESET_ALL}")
            server_name = server_header.split('/')[0]
            server_version = server_header.split('/')[1].split('(')[0]
            print(f"{server_name} server version: {server_version}")
        else:
            print(f"{Fore.RED}[X] Server header not found in the response{Style.RESET_ALL}")
        
        # Extract other headers 
        print("Content-Type:", response.headers.get('Content-Type'))
        engine = response.headers.get('X-Powered-By')
        server_engine_name = None
        server_engine_version = None
        if engine:
            print("X-Powered-By:", engine)
            server_engine_name = engine.split('/')[0]
            server_engine_version = engine.split('/')[1]
            print(f"{server_engine_name} engine version: {server_engine_version}")
        return server_name, server_version, server_engine_name, server_engine_version, engine
        
    except requests.RequestException as e:
        print(f"{Fore.RED}[X] Failed to retrieve HTTP server information, please check the name (url) of the provided service: {e}{Style.RESET_ALL}")

def handle_service_version(service_type, url, configuration_file):
    try:
        search_fun = getattr(search_modules, f"search_{service_type}")
    except AttributeError:
        print(f"{Fore.RED}[X] The service type provided is not supported by the tool.\n==> Please check the supported services in the search_modules.py file.{Style.RESET_ALL}")
        sys.exit(1)
    
    if not configuration_file:
        service_version = search_fun(url)
    else:
        try:
            service_version = search_fun(url, configuration_file)
        except TypeError:
            print(f"{Fore.YELLOW}[!] The configuration file settings is not supported by the service type provided.{Style.RESET_ALL}\
                \n==> Please check the supported services in the search_modules.py file.\
                \n==> Launching the search without configuration file...")
            service_version = search_fun(url)

    if not service_version or service_version == "-" or service_version == "":
        print(f"{Fore.RED}[X] The service type that is running is not the one provided or the tool has failed in retrieving service version{Style.RESET_ALL}")
        sys.exit(1)
    return service_version

def main():

    # Checking calling arguments
    verbose, deep, file, pdf, services = handle_arguments()

    for service in services:
        server_name = None
        server_version = None
        engine = None
        parts = service.split("::")
        if len(parts) < 2:
            print(USAGE)
            sys.exit(1)
        service_name = parts[0]
        service_type = parts[1]
        if service_name == "" or service_type == "":
            print(USAGE)
            sys.exit(1)
        configuration_file = parts[2] if len(parts) > 2 else None
        url = service_name
        if url.startswith("http://"):
            server_name, server_version, server_engine_name, server_engine_version, engine = get_server_info(url)

        # Checking and retrieving version from the type of service
        service_version = handle_service_version(service_type, url, configuration_file)

        # Searching for CVEs
        cve_list = []

        if deep and server_name and server_version:
            print(f"\n{Fore.CYAN}[*] Searching for CVEs related to the keywords relating the SERVER running the service: {server_name} {server_version}{Style.RESET_ALL}")
            cve_list = search_cve(server_name, server_version)
            print_cves(cve_list, server_name, server_version, verbose)
            if file:
                print_cves_to_file(cve_list, server_name, server_version, file, verbose=verbose)
            if pdf:
                print_cves_to_file(cve_list, server_name, server_version, DEFAULT_FILE_TXT, verbose=verbose)
            
        
        if deep and engine:
            print(f"\n{Fore.CYAN}[*] Searching for CVEs related to the keywords relating the ENGINE running the service: {server_engine_name} {server_engine_version}{Style.RESET_ALL}")
            cve_list = search_cve(server_engine_name, server_engine_version)
            print_cves(cve_list, server_engine_name, server_engine_version, verbose)
            if file:
                print_cves_to_file(cve_list, server_engine_name, server_engine_version, file, verbose=verbose)
            if pdf:
                print_cves_to_file(cve_list, server_engine_name, server_engine_version, DEFAULT_FILE_TXT, verbose=verbose)

        print(f"\n{Fore.CYAN}[*] Searching for CVEs related to the keywords relating the SERVICE: {service_type} {service_version}{Style.RESET_ALL}")
        cve_list = search_cve(service_type, service_version)
        print_cves(cve_list, service_type, service_version, verbose)
        if file:
            print_cves_to_file(cve_list, service_type, service_version, file, verbose=verbose)
            if pdf:
                print_cves_to_file(cve_list, service_type, service_version, file, verbose=verbose)
                generate_pdf(input=file, output=pdf)
        else:
            if pdf:
                print_cves_to_file(cve_list, service_type, service_version, DEFAULT_FILE_TXT, verbose=verbose)
                generate_pdf(input=DEFAULT_FILE_TXT, output=pdf)

if __name__ == "__main__":
    main()