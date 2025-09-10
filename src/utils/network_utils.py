import socket

def get_service_name(port):
    """
    ポート番号からサービス名を返します。
    見つからない場合は 'unknown' を返します。
    """
    try:
        # TCPプロトコルでサービス名を検索
        service_name = socket.getservbyport(port, 'tcp')
        return service_name
    except OSError:
        # サービス名が見つからない場合のエラー処理
        return "unknown"