import http.server
import socketserver
import os

# Set the port number
PORT = 9000

# Get the absolute path to the directory where the script is located
# This is the QA directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the web root to the parent directory of the script's location
# This is the project's root directory
web_root = os.path.abspath(os.path.join(script_dir, '..'))

# --- Custom Handler to Set Headers ---
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=web_root, **kwargs)

# --- Start the Server ---
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Web root is set to: {web_root}")
    print("\nTo view your site, open a web browser and go to:")
    print(f"  http://localhost:{PORT}\n")
    print("Press Ctrl+C to stop the server.")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown() 