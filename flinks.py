#!/usr/bin/env ./.venv/bin/python3
import subprocess
import json
import datetime
import argparse
import sys
import os
from threading import Thread
import pathlib

parser = argparse.ArgumentParser(description="FLinks: Gathering URL From Multiple Sources.")

parser.add_argument("-d", "--domain", default=False,
                        help='Enter your target Domain to gather URL')
parser.add_argument("-q", "--quite", default=False, action="store_true",
                        help='Suppress all the messages and just return found URLs')
parser.add_argument("-o", "--output", default=False,
                        help='Save output to a file')
parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help='Show verbose output messages.')

options = parser.parse_args()

options.domain = options.domain[:-1] if options.domain[-1] == "/" else options.domain

if not options.domain:
    print("[-] Please enter domain name using -d switch.")
    sys.exit(0)

def message_print(message):
    if not options.quite:
        print(message)

def verbose_print(message):
    if options.verbose:
        print(message)

domain_list = set()

if options.domain == "-":
    domains = sys.stdin
    for domain in domains:
        domain = domain.strip()
        if "http" not in domain:
            message_print(f"[-] Skipping '{domain}'. No Schema Provided (HTTP|HTTPS)")
            continue
        else:
            domain_list.add(domain)
else:
    if "http" not in options.domain:
        print("[-] Please enter domain name with it's schema (HTTP|HTTPS)")
        sys.exit(0)
    else:
        domain_list.add(options.domain)

config_path = f"{pathlib.Path(__file__).parent.resolve()}/configs.json"
if not os.path.exists(config_path):
    print("[-] Could not find 'configs.json', please make sure it's in the current directory.")
    sys.exit(0)
else:
    configs = json.load(open(config_path, "r", encoding="utf-8", errors="ignore"))

def current_time():
    c_time = str(datetime.datetime.now())[:19]
    return c_time



gospider_config = configs["gospider"]
gospider_urls = set()
def gospider(domain):
    message_print(f"[*] Started GoSpider engine to extract URLs [{current_time()}]")
    proxy = f'--proxy \"{gospider_config["proxy"]}\"' if gospider_config["proxy"] else ""
    cookie = f'--cookie \"{gospider_config["cookie"]}\"' if gospider_config["cookie"] else ""
    delay = f'--delay {gospider_config["delay"]}' if gospider_config["delay"] else ""
    user_agent = f'--user-agent \"{gospider_config["user-agent"]}\"'
    threads = f'--threads {int(gospider_config["threads"])}'
    concurrent = f'--concurrent {int(gospider_config["concurrent"])}'
    include_subdomains = f'--subs' if gospider_config["include-subdomains"] else ""
    include_sitemap = f'--sitemap' if gospider_config["include-sitemap"] else ""
    other_source = f'--other-source' if gospider_config["include-sitemap"] else ""
    command = f"gospider -s \"{domain}\" --quiet {proxy} {cookie} {delay} {user_agent} {threads} {concurrent} {include_subdomains} {include_sitemap} {other_source}"
    verbose_print(f"[DEBUG] Command: {command}")

    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for url in output.stdout.splitlines():
        url = url.strip()
        url = url.decode("utf-8")
        if "[code-" in url:
            if not gospider_config["include-js-files"]:
                continue
            try:
                url = url.rsplit(" ", 1)[-1]
            except:
                continue
            gospider_urls.add(url)
        else:
            gospider_urls.add(url)
    return 0


robofinder_config = configs["robofinder"]
robofinder_urls = set()
def robofinder(domain):
    message_print(f"[*] Started RoboFinder engine to extract URLs [{current_time()}]")
    delay = f'--delay {robofinder_config["delay"]}' if robofinder_config["delay"] else ""
    python_command = configs["python-command"]
    robofinder_path = robofinder_config["installation-path"]

    command = f"{python_command} {robofinder_path} -u \"{domain}\" -q -a {delay}"
    verbose_print(f"[DEBUG] Command: {command}")
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for url in output.stdout.splitlines():
        url = url.strip()
        url = url.decode("utf-8")
        robofinder_urls.add(url)

    return 0



message_print(f"[+] Started Gathering URLs [{current_time()}]")
for domain in domain_list:
    message_print(f"[+] Set Target As '{domain}'")

    thread_list = []

    thread_list.append(Thread(target=gospider, args=(domain,)))
    thread_list.append(Thread(target=robofinder, args=(domain,)))

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

fetched_urls = set.union(gospider_urls, robofinder_urls)

if len(fetched_urls) < 1:
    print("[!] No URL Found! Better Luck Next Time...")
    print(f"[+] Finished! [{current_time()}]")
    sys.exit(0)

if not options.output:
    for url in fetched_urls:
        print(url)
else:
    message_print(f"[+] Saving result to '{options.output}'")
    file_handle = open(options.output, "w", encoding="utf-8", errors="ignore")
    for url in fetched_urls:
        file_handle.write(f"{url}\n")
    file_handle.close()

message_print(f"[+] Found URLs: {len(fetched_urls)}")
message_print(f"[+] Finished! [{current_time()}]")
