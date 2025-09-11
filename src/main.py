# src/main.py (更新後)

import argparse
import importlib.metadata
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# C言語でコンパイルした高速なスキャン関数をインポート
# もしインポートに失敗した場合、Python版を予備として使う
# try:
from scanner.c_scanner import scan_port
SCAN_MODE = "C"
# except ImportError:
#     from src.scanner.port_scanner import check_port as scan_port
#     SCAN_MODE = "Python"

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
        version=f"%(prog)s {__version__}" # 表示する文字列 (例: "reaper 0.2.0")
    )
    
    args = parser.parse_args()

    host_ip = args.host
    num_workers = args.workers
    try:
        target_ports = parse_ports(args.ports)
    except ValueError:
        print("Error: Invalid port format. Please use formats like '80', '1-1024', '80,443'.")
        return
    
    print(f"🚀 Starting Reaper scanner on {host_ip} (Engine: {SCAN_MODE})")
    print(f"Scanning {len(target_ports)} ports with {num_workers} workers...\n")

    open_ports = []

    # ThreadPoolExecutorを使って並列処理を実行
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # {future: port} の辞書を作成
        future_to_port = {executor.submit(scan_port, host_ip, port): port for port in target_ports}
        
        # tqdmで進捗バーを表示しながら結果を待つ
        progress_bar = tqdm(as_completed(future_to_port), total=len(target_ports), desc="Scanning Ports")
        for future in progress_bar:
            port = future_to_port[future]
            try:
                # C関数がTrueを返した場合 (ポートがオープン)
                if future.result():
                    open_ports.append(port)
                    # 進捗バーの横に見つかったオープンポートを表示
                    progress_bar.set_postfix_str(f"Found: {port}")
            except Exception as exc:
                print(f"Port {port} generated an exception: {exc}")

    print("\n✨ Scan Complete!")
    if open_ports:
        print("✅ Open Ports Found:")
        print(", ".join(map(str, sorted(open_ports))))
    else:
        print("❌ No open ports found in the specified range.")

if __name__ == "__main__":
    main()