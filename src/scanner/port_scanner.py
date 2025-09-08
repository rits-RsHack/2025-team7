# src/scanner/port_scanner.py

import socket

def check_port(host: str, port: int) -> bool:
    """
    指定されたホストとポートの開閉状態を確認します。

    Args:
        host (str): ターゲットのIPアドレスまたはホスト名。
        port (int): ターゲットのポート番号。

    Returns:
        bool: ポートが開いている場合は True、閉じている場合は False を返します。
    """
    # ソケットを作成します。
    # AF_INET: IPv4を使用することを示します。
    # SOCK_STREAM: TCP通信を使用することを示します。
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 接続試行のタイムアウトを1秒に設定します。
    # これがないと、応答がないポートでプログラムがずっと待ってしまいます。
    s.settimeout(1)

    try:
        # ターゲットへの接続を試みます。
        # connect_exは、成功すれば 0 を、失敗すればエラーコードを返します。
        # connect() と違い、失敗時に例外を発生させないため、条件分岐がシンプルになります。
        result = s.connect_ex((host, port))
        
        if result == 0:
            # 接続に成功した場合 (ポートがオープン)
            return True
        else:
            # 接続に失敗した場合 (ポートがクローズまたはフィルタリング)
            return False
            
    except socket.gaierror:
        # ホスト名が解決できない場合（例: www.存在しないドメイン.com）
        print(f"エラー: ホスト名 '{host}' が解決できませんでした。")
        return False
    except socket.error as e:
        # その他のソケット関連エラー
        print(f"エラー: {e}")
        return False
        
    finally:
        # 接続試行が終わったら、必ずソケットを閉じます。
        s.close()