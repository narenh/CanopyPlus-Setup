#!/usr/bin/env python3
"""
Simple HTTP endpoint for CoreELEC
Accepts rating_key and media_type parameters and executes a shell script
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import URLError
import subprocess
import json
import base64

# Configuration
PORT = 8082
SCRIPT_PATH = "/storage/scripts/process_media.sh"
KODI_JSON_RPC_URL = "http://localhost:8080/jsonrpc"
KODI_USERNAME = ""  # Set if you have authentication enabled
KODI_PASSWORD = ""  # Set if you have authentication enabled

class MediaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Extract rating_key and media_type
        rating_key = query_params.get('rating_key', [''])[0]
        media_type = query_params.get('media_type', [''])[0]

        if not rating_key or not media_type:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Error: Missing rating_key or media_type parameter')
            return

        try:
            # Execute the shell script with parameters
            result = subprocess.run(
                [SCRIPT_PATH, rating_key, media_type],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Get the script output (should be either empty or a Kodi ID number)
            script_output = result.stdout.strip()
            
            # Check if the script returned nothing (media ID not found)
            if not script_output:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'false')
                return
            
            # If we get here, script returned a Kodi ID (movieid or episodeid)
            kodi_id = script_output
            
            # Determine the correct parameter name based on media_type
            if media_type == 'movie':
                item_param = {"movieid": int(kodi_id)}
            elif media_type == 'episode':
                item_param = {"episodeid": int(kodi_id)}
            else:
                # Fallback for unknown types
                item_param = {"file": kodi_id}
            
            # Call Kodi JSON-RPC to start playback
            kodi_payload = {
                "jsonrpc": "2.0",
                "method": "Player.Open",
                "params": {"item": item_param},
                "id": 1
            }
            
            try:
                # Prepare the request
                req = Request(KODI_JSON_RPC_URL, data=json.dumps(kodi_payload).encode('utf-8'))
                req.add_header('Content-Type', 'application/json')
                
                # Add authentication if credentials are provided
                if KODI_USERNAME and KODI_PASSWORD:
                    credentials = base64.b64encode(f"{KODI_USERNAME}:{KODI_PASSWORD}".encode()).decode('utf-8')
                    req.add_header('Authorization', f'Basic {credentials}')
                
                # Send the request
                with urlopen(req, timeout=5) as response:
                    response_data = json.loads(response.read().decode())
                    if response_data.get('error'):
                        print(f"Kodi JSON-RPC error: {response_data['error']}")
                    
            except URLError as e:
                print(f"Kodi JSON-RPC error: {e}")
            except Exception as e:
                print(f"Kodi JSON-RPC error: {e}")
            
            # Send the original script output (the Kodi ID)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.stdout.encode())

        except subprocess.TimeoutExpired:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Error: Script execution timed out')

        except FileNotFoundError:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: Script not found at {SCRIPT_PATH}'.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"{self.address_string()} - {format % args}")

def run_server():
    """Start the HTTP server"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MediaHandler)
    print(f'Starting HTTP server on port {PORT}...')
    print(f'Script path: {SCRIPT_PATH}')
    print(f'Example usage: http://YOUR_IP:{PORT}/?rating_key=12345&media_type=movie')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.shutdown()

if __name__ == '__main__':
    run_server()