# from http import server
# 
# def run(server_class=server.ThreadingHTTPServer, handler_class=server.SimpleHTTPRequestHandler):
#     server_address = ('', 8000)
#     httpd = server_class(server_address, handler_class)
#     httpd.serve_forever()
# 
#     return httpd
# 
# httpd = run()
# print(httpd.handle())


import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port:", PORT)
    httpd.serve_forever()
