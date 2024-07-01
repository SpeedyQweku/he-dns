import argparse
import sys
import requests
import re
import os
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

def parse_args():
    parser = argparse.ArgumentParser(description='Domain Information Fetcher')
    parser.add_argument('-d', '--domain', required=True, help='Domain for the Info')
    parser.add_argument('-dns', action='store_true', help='Get DNS info')
    parser.add_argument('-web', action='store_true', help='Get website info')
    parser.add_argument('-ip', action='store_true', help='Get IP info')
    parser.add_argument('-whois', action='store_true', help='Get WHOIS info')
    return parser.parse_args()

def clean_text(text):
    return re.sub(r'\s{3,}', '\n', text).strip()

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return False
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Image downloaded and saved as: {save_path}")
    return True

def main():
    args = parse_args()
    
    if not (args.dns or args.web or args.ip or args.whois):
        print("[!] No specific info flags provided. Defaulting to DNS info.\n")
        args.dns = True
    
    url = f"https://bgp.he.net/dns/{args.domain}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error visiting the URL: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    if args.dns:
        dns = soup.find(id="dns")
        if dns:
            dnsHeads = dns.find_all('div', class_='dnshead')
            dnsDatas = dns.find_all('div', class_='dnsdata')
            for dns_head, dns_data in zip(dnsHeads, dnsDatas):
                if dns_head and dns_data:
                    print(f"[-] {clean_text(dns_head.text)}\n{clean_text(dns_data.text)}\n")
                else:
                    print("DNS information not found.")
        else:
            print("DNS information not found.")
    
    if args.ip:
        ipinfo_section = soup.find(id='ipinfo')
        if ipinfo_section:
            ip_entries = ipinfo_section.find_all('a', href=re.compile(r'^/ip/'))
            for ip_entry in ip_entries:
                ip_address = ip_entry.text.strip()
                ip_details = ip_entry.find_next_siblings('a')
                if len(ip_details) >= 2:
                    ip_range = ip_details[0].text.strip()
                    as_info_tag = ip_details[1]
                    as_parts = as_info_tag['title'].split(' ', 1) if 'title' in as_info_tag.attrs else ["", ""]
                    as_number = as_parts[0]
                    org_info = as_parts[1].strip() if len(as_parts) > 1 else ""
                    print(f"{ip_address} > {ip_range} > {as_number} > {org_info}")
        else:
            print("IP information section not found.")

    if args.whois:
        whois = soup.find(id="whois")
        if whois:
            print(clean_text(whois.text))

    if args.web:
        website_section = soup.find(id='website')
        if website_section:
            webthumb_img = website_section.find('div', class_='webthumb').find('img')
            if webthumb_img:
                img_src = webthumb_img['src']
                img_url = f"https://bgp.he.net{img_src}"
                
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                filename = unquote(filename.split('?')[0])
                img_save_path = os.path.join(os.getcwd(), filename)
                
                if download_image(img_url, img_save_path):
                    print(f"Image saved: {img_save_path}")
                else:
                    print("Failed to download image.")
            else:
                print("Web thumbnail image not found.")
        else:
            print("Website info section not found.")

if __name__ == "__main__":
    main()
