#!/usr/bin/env python
"""
Test de ports pour diagnostiquer le firewall
"""
import socket
import sys

def test_port(host, port, timeout=5):
    """Test si un port est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def main():
    host = "capdrive.caplogy.com"
    ip = "51.68.102.116"
    
    print(f"🔍 Test de ports pour {host} ({ip})")
    print("=" * 50)
    
    # Ports communs à tester
    ports_to_test = [
        (80, "HTTP"),
        (443, "HTTPS"),
        (8080, "HTTP Alt"),
        (8443, "HTTPS Alt"),
        (22, "SSH"),
        (21, "FTP"),
        (25, "SMTP"),
        (53, "DNS"),
    ]
    
    print("Test avec le nom de domaine:")
    for port, service in ports_to_test:
        is_open = test_port(host, port)
        status = "✅ OUVERT" if is_open else "❌ FERMÉ"
        print(f"  Port {port:4} ({service:10}): {status}")
    
    print(f"\nTest avec l'IP directe ({ip}):")
    for port, service in ports_to_test:
        is_open = test_port(ip, port)
        status = "✅ OUVERT" if is_open else "❌ FERMÉ"
        print(f"  Port {port:4} ({service:10}): {status}")

if __name__ == "__main__":
    main()
