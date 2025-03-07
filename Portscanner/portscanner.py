import socket
import threading

def scan_port(target, port):
    """Scans a single port on a target IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        conn = s.connect_ex((target, port))  # 0 means open
        if conn == 0:
            print(f"[+] Port {port} is open on {target}")
        s.close()
    except Exception as e:
        pass

def run_scanner(target, ports):
    """Runs port scanning on a list of ports."""
    print(f"Scanning {target} for open ports...")
    threads = []
    
    for port in ports:
        t = threading.Thread(target=scan_port, args=(target, port))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    target_ip = input("Enter target IP: ")
    ports_to_scan = range(20, 1025)  # Scanning ports 20-1024
    run_scanner(target_ip, ports_to_scan)