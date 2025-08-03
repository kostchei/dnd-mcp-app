
"""
simple_web_server.py - Simple web interface for testing D&D tools
Run this to get a basic web interface for your D&D server
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import threading
import urllib.parse

class DnDWebHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>D&D MCP Server Test</title></head>
            <body>
                <h1>🎲 D&D MCP Server Test Interface</h1>
                
                <h2>Roll Dice</h2>
                <button onclick="rollDice('1d20', 0)">Roll 1d20</button>
                <button onclick="rollDice('2d6', 3)">Roll 2d6+3</button>
                <button onclick="rollDice('1d8', 2)">Roll 1d8+2</button>
                
                <h2>Combat</h2>
                <button onclick="attackRoll(5, 15)">Attack (+5 vs AC 15)</button>
                <button onclick="attackRoll(3, 12)">Attack (+3 vs AC 12)</button>
                
                <h2>Results</h2>
                <div id="results"></div>
                
                <script>
                async function rollDice(dice, modifier) {
                    const response = await fetch('/api/roll', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({dice: dice, modifier: modifier})
                    });
                    const result = await response.json();
                    showResult(`🎲 ${dice}+${modifier}: ${result.rolls} = ${result.total}`);
                }
                
                async function attackRoll(bonus, ac) {
                    const response = await fetch('/api/attack', {
                        method: 'POST', 
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({bonus: bonus, ac: ac})
                    });
                    const result = await response.json();
                    showResult(`⚔️ ${result.description}`);
                }
                
                function showResult(text) {
                    document.getElementById('results').innerHTML = '<p>' + text + '</p>' + 
                        document.getElementById('results').innerHTML;
                }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/roll':
            self.handle_roll()
        elif self.path == '/api/attack':
            self.handle_attack()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_roll(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # This is a simplified version - in reality you'd call the MCP server
            import random
            dice_parts = data['dice'].split('d')
            num_dice = int(dice_parts[0]) 
            sides = int(dice_parts[1])
            
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(rolls) + data['modifier']
            
            result = {'rolls': rolls, 'total': total}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def handle_attack(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            import random
            roll = random.randint(1, 20)
            total = roll + data['bonus']
            hit = total >= data['ac']
            
            if hit:
                damage = random.randint(1, 8) + 2
                description = f"Hit! {roll} + {data['bonus']} = {total} vs AC {data['ac']}. Damage: {damage}"
            else:
                description = f"Miss! {roll} + {data['bonus']} = {total} vs AC {data['ac']}"
            
            result = {'description': description, 'hit': hit}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_web_server():
    server = HTTPServer(('localhost', 8080), DnDWebHandler)
    print("🌐 D&D Web Interface running at: http://localhost:8080")
    server.serve_forever()

if __name__ == "__main__":
    run_web_server()