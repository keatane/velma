import requests
from bs4 import BeautifulSoup
import mysql.connector
import json
from colorama import Fore, Style

# ----------------------------------------------------- #
# Add here your functions to search for service version #
# ----------------------------------------------------- #
# Supported services: #
# - Apache
# - PHP
# - MySQL
# - WordPress
# - Joomla
# ------------------- #

def search_apache(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            server = response.headers['Server']
            if "apache" in server.lower():
                return server.split('/')[1].split(' ')[0]            
    except Exception:
        print(f"{Fore.RED}[X] Failed to retrieve Apache version{Style.RESET_ALL}")
        return "-"

def search_mysql(url, configuration_file="mysql.json"):

    configuration_loaded = False
    try:
        with open("configurations/" + configuration_file) as f:
            configuration_loaded = True
            data = json.load(f)
            host = data['mysql']['host']
            user = data['mysql']['user']
            password = data['mysql']['password']
            database = data['mysql']['database']
    except FileNotFoundError:
        print(f"{Fore.RED}[X] Error: Configuration file not found{Style.RESET_ALL}" \
              "\n==> The tool will try to connect to the MySQL database with default localhost settings")
    except Exception as e:
        print(f"{Fore.RED}[X] Error: Failed to read the configuration file: {e}{Style.RESET_ALL}" \
              "\n==> The tool will try to connect to the MySQL database with default settings")
    
    try:
        if configuration_loaded:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
        else:
            connection = mysql.connector.connect(
                host=url,
                user="user",
                password="password",
                database="generic_db"
            )

        if connection.is_connected():
            # print("[DEBUG] -- Connected to MySQL database")
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()

    except mysql.connector.Error as e:
        print(f"{Fore.RED}[X]Error connecting to MySQL database: {e}{Style.RESET_ALL}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            # print("[DEBUG] -- MySQL connection is closed")
            return version[0]

def search_wordpress(url):
    response = requests.get(url)
    if response.status_code == 200:
        headers = response.headers
        # Check if the WordPress version is present in the headers
        if 'x-generator' in headers:
            # Extract the version from the 'x-generator' header
            version = headers['x-generator'].split(' ')[1]
            return version
        
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'name': 'generator'})
        if meta_tag and 'content' in meta_tag.attrs:
            generator_content = meta_tag['content']
            # Extract the version number from the generator content
            version = generator_content.split(' ')[1].split(',')[0]
            return version
    else:
        print(f"{Fore.RED}[X] Server is not reachable{Style.RESET_ALL}")
    
    print(f"{Fore.RED}[X] Failed to retrieve WordPress version{Style.RESET_ALL}")
    return None
    
def search_joomla(url):
    try:
        response = requests.get(url + '/administrator/manifests/files/joomla.xml')
        if response.status_code == 200:
            version = response.text.split('<version>')[1].split('</version>')[0]
            return version
        else:
            print(f"{Fore.RED}[X] Failed to retrieve Joomla version{Style.RESET_ALL}")
            return None
    except Exception as e:
        return "Error: " + str(e)
