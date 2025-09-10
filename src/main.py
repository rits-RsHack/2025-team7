#!/usr/bin/env python3

import argparse # argparseライブラリをインポート
from src.scanner.port_scanner import check_port
from src.utils.network_utils import get_service_name

def main():
    """
    コマンドライン引数からホストとポートを受け取り、スキャンを実行します。
    """
    # 1. パーサー（引数を解析するオブジェクト）を作成
    parser = argparse.ArgumentParser(
        description="指定されたホストとポートのスキャンを実行するシンプルなポートスキャナです。"
    )

    # 2. 受け取る引数を定義
    # 'host'という名前の位置引数を追加
    parser.add_argument("host", type=str, help="スキャン対象のIPアドレスまたはホスト名")
    # 'port'という名前の位置引数を追加
    parser.add_argument("port", type=int, help="スキャン対象のポート番号 (1-65535)")

    # 3. コマンドライン引数を解析
    args = parser.parse_args()
    
    # 4. 解析した引数を変数に格納
    host_ip = args.host
    port_num = args.port

    # ポート番号が有効な範囲かチェック
    if not (0 < port_num < 65536):
        print(f"エラー: ポート番号は1から65535の間で指定してください。入力値: {port_num}")
        return

    try:
        print(f"\nスキャン中... -> {host_ip}:{port_num}")

        # 作成したポートチェック関数を呼び出す
        is_open = check_port(host_ip, port_num)

        # 結果を表示
        if is_open:
            service = get_service_name(port_num)
            print(f"結果: ポート {port_num} ({service}) は [オープン] です。✅")
        else:
            print(f"結果: ポート {port_num} は [クローズ] です。❌")

    except KeyboardInterrupt:
        print("\nスキャンを中断しました。")

if __name__ == "__main__":
    main()