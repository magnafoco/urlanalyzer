import argparse
import sys
import requests
import ssl
import regex

# Define command line arguments
parser = argparse.ArgumentParser(description="A tool to check URLs for authentication methods, certificates and more.", epilog="")
parser.add_argument("-i", "--input", metavar='', type=argparse.FileType('r'), default=sys.stdin, required=True, help="Input file")
parser.add_argument("-a", "--auth", action="store_true", help="Check authentication methods")
parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity level")
args = parser.parse_args()

# Banner ASCII from manytools.org
banner = '''
██╗   ██╗██████╗ ██╗          █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
██║   ██║██╔══██╗██║         ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
██║   ██║██████╔╝██║         ███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
██║   ██║██╔══██╗██║         ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║███████╗    ██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
Author: magnafoco 🔥
'''
print(banner)

# Read lines from the input file.
input_data = args.input.readlines()

# Define ANSI color codes.
class color:
    bold = '\033[1;37m'
    red = '\033[31m'
    yellow = '\033[33m'
    green = '\033[32m'
    reset = '\033[0m'

# Check the response for authentication.
def parse_response_for_auth(response):
    if 'type="password"' in response.text or "type='password'" in response.text:
        return color.yellow + "\n[!]" + color.reset + " HTML form authentication detected!"
    
    elif 'WWW-Authenticate' in response.headers:
        authenticate_header = response.headers['WWW-Authenticate']
        if 'Negotiate' in authenticate_header:
            return "Kerberos authentication detected."
        elif 'Basic' in authenticate_header:
            return color.yellow + "\n[!]" + color.reset + " Basic authentication detected!"
        elif 'NTLM' in authenticate_header:
            return color.yellow + "\n[!]" + color.reset + " NTLM authentication detected!"
        elif 'Digest' in authenticate_header:
            return color.yellow + "\n[!]" + color.reset + " Digest authentication detected!"
        elif 'Bearer' in authenticate_header:
            return color.yellow + "\n[!]" + color.reset + " Bearer authentication detected!"
        else:
            print(color.red + "\n[!]" + color.reset + " Unknown authentication type.")
    elif 'Proxy-Authenticate:' in response.headers:
        return color.yellow + "\n[!]" + color.reset + " Proxy authentication detected!"
    
    else:
        return "\nNo login or authentication found."

# Add verbosity by printing response headers.
def verbosity(output):
    print("\nResponse headers for URL:", color.bold + response.url + color.reset, "\n")
    for header, value in response.headers.items(): 
        print(header + ": " + value + '\n')
    return

# Check if there's a redirect from HTTP of HTTPS
def redirect_from_http_to_https(response):
    if regex.match(r'^http:', url) and regex.match(r'^https:', response.url):
        print("\nHas been redirected from:", color.bold + url + color.reset, "to:", color.bold + response.url + color.reset)
    return

# Check the HTTP response status code.
def http_status_code(response):
    if regex.match(r'^404', str(response.status_code)):
        return "\nHTTP Status code: " + color.red + str(response.status_code) + color.reset
    if regex.match(r'^401', str(response.status_code)) or regex.match(r'^403', str(response.status_code)):
        return "\nHTTP Status code: " + color.yellow + str(response.status_code) + color.reset
    else:
        return "\nHTTP Status code: " + str(response.status_code)

# Process each URL
for url in input_data:
    url = url.strip()
    
    try:
        response = requests.get(url, timeout=60.0)
        print("\n----------------------------------------\n")
        print("Processing request for URL:", color.bold + response.url + color.reset)
        redirect_from_http_to_https(response)
        print(http_status_code(response))

        if args.auth is True:
            print(parse_response_for_auth(response))

        if args.verbose:
            verbosity(response)

    except requests.exceptions.RequestException as req_exc:
        print(f"Request Exception occurred for URL: {url}")
        print(req_exc)
    except ssl.SSLError as ssl_err:
        print(f"SSL Error occurred for URL: {url}")
        print(ssl_err)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error occurred for URL: {url}")
        print(http_err)
    except Exception as other_exc:
        print(f"An unexpected error occurred for URL: {url}")
        print(other_exc)