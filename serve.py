#!/usr/bin/env python3
"""
Ad Creative Lab Landing Page - Simple HTTP Server
"""

import http.server
import socketserver
import os
import argparse
from pathlib import Path

def serve_directory(directory="public", port=8000):
    """Serve the specified directory on the given port."""
    # Change to the directory containing the files
    os.chdir(directory)
    
    # Set up the handler for serving files
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create a TCP server with the handler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving {os.path.abspath(directory)} at http://localhost:{port}")
        
        # Serve until process is killed
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Simple HTTP server for Ad Creative Lab Landing Page")
    parser.add_argument(
        "--dir", 
        default="public", 
        help="Directory to serve (default: 'public')"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to serve on (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Check if the directory exists
    if not Path(args.dir).is_dir():
        print(f"Error: Directory '{args.dir}' does not exist.")
        exit(1)
    
    serve_directory(args.dir, args.port) 