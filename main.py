# main.py

from src.scanner.port_scanner import check_port

def main():
    """
    ユーザーからホストとポートの入力を受け取り、スキャンを実行します。
    """
    print("=== シンプルポートスキャナ ===")
    
    try:
        host_ip = input("スキャン対象のIPアドレスまたはホスト名を入力してください: ")
        port_num_str = input("スキャン対象のポート番号を入力してください: ")
        port_num = int(port_num_str)

        if not (0 < port_num < 65536):
            print("エラー: ポート番号は1から65535の間で指定してください。")
            return

        print(f"\nスキャン中... -> {host_ip}:{port_num}")

        # 作成したポートチェック関数を呼び出す
        is_open = check_port(host_ip, port_num)

        # 結果を表示
        if is_open:
            print(f"結果: ポート {port_num} は [オープン] です。✅")
        else:
            print(f"結果: ポート {port_num} は [クローズ] です。❌")

    except ValueError:
        print("エラー: ポート番号は数字で入力してください。")
    except KeyboardInterrupt:
        print("\nスキャンを中断しました。")

if __name__ == "__main__":
    main()