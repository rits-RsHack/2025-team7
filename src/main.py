# src/main.py (サービス名表示機能を追加)

import argparse
import importlib.metadata
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import socket
from src.scanner.port_scanner import check_port as scan_port, get_banner

# C言語でコンパイルした高速なスキャン関数をインポート
# もしインポートに失敗した場合、Python版を予備として使う
try:
    from c_scanner import scan_port
    SCAN_MODE = "C"
except ImportError:
    from src.scanner.port_scanner import check_port as scan_port
    SCAN_MODE = "Python"

# --- 変更点 1: サービス名を取得する関数を追加 ---
def get_service_name(port):
    """ポート番号からサービス名を返す。見つからなければ'unknown'を返す。"""
    try:
        return socket.getservbyport(port, 'tcp')
    except (OSError, TypeError): # ポート番号がNoneの場合も考慮
        return "unknown"
# --------------------------------------------

def parse_ports(port_range_str):
    """ポート範囲の文字列 (例: '1-1024', '80,443', '22') を解析してポートのリストを返す"""
    ports = set()
    parts = port_range_str.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return sorted(list(ports))

def main():
    parser = argparse.ArgumentParser(description="A fast and parallel port scanner.")
    parser.add_argument("host", type=str, help="Target host IP address or hostname.")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", 
                        help="Ports to scan. (e.g., '1-1024', '80,443', '22,80-90')")
    parser.add_argument("-w", "--workers", type=int, default=100, 
                        help="Number of parallel scanning threads (workers).")
    
    try:
        __version__ = importlib.metadata.version("reaper")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "unknown"
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()

    host_ip = args.host
    num_workers = args.workers

    try:
        resolved_ip = socket.gethostbyname(host_ip)
        print(f"Resolving '{host_ip}' to {resolved_ip}")
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{host_ip}'")
        return
    
    try:
        target_ports = parse_ports(args.ports)
    except ValueError:
        print("Error: Invalid port format. Please use formats like '80', '1-1024', '80,443'.")
        return
    
    print(f"🚀 Starting Reaper scanner on {host_ip} (Engine: {SCAN_MODE})")
    print(f"Scanning {len(target_ports)} ports with {num_workers} workers...\n")

    # --- 変更点 2: 結果を {ポート番号: サービス名} の辞書で保存 ---
    open_ports = {}
    # ---------------------------------------------------------

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_port = {executor.submit(scan_port, resolved_ip, port): port for port in target_ports}
        
        progress_bar = tqdm(as_completed(future_to_port), total=len(target_ports), desc="Scanning Ports")
        for future in progress_bar:
            port = future_to_port[future]
            try:
                banner = ""
                if future.result():
                    # --- 変更点 3: サービス名を取得し、辞書に保存 ---
                    service = get_service_name(port)

                    if service != "unknown":
                    
                        banner = get_banner(host_ip, port) # get_bannerを呼び出す
                    
                        open_ports[port] = service # 結果を保存
                    
                    # 進捗バーの表示を更新
                    if banner:
                        progress_bar.set_postfix_str(f"Found: {port} ({service}) - {banner[:20]}...")
                    else:
                        progress_bar.set_postfix_str(f"Found: {port} ({service})")
                        # ------------------------------------------------
            except Exception as exc:
                print(f"Port {port} generated an exception: {exc}")

    print("\n✨ Scan Complete!")
    if open_ports:
        print("✅ Open Ports Found:")
        # --- 変更点 4: 辞書の内容を綺麗に表示 ---
        for port, service in sorted(open_ports.items()):
            print(f"  - Port {port:<5} ({service})")
        # ---------------------------------------
    else:
        print("❌ No open ports found in the specified range.")

if __name__ == "__main__":
    main()