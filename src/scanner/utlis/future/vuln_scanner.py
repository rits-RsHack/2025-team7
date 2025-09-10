# src/scanner/vuln_scanner.py

# 1. 簡易的な脆弱性データベースを定義する
VULNERABILITY_DB = {
    "BobompaSato": {
        "2.4.41": "【要注意人物】ネットワークの重要区画に不正に侵入する危険な手口を使うとの情報あり。",
    },
    "OpenSSH": {
        "8.2": "特定の状況下でユーザ名が漏洩する脆弱性が存在する可能性があります。"
    }
}

# 2. バナー情報をもとに、このDBを検索する関数を作成する
def check_vulnerability(service_banner: str) -> str:
    """
    バナー情報を受け取り、簡易データベースに既知の脆弱性がないかチェックします。
    """
    # バナー情報の中に、DBのサービス名やバージョンが含まれているかチェック
    for service, versions in VULNERABILITY_DB.items():
        if service.lower() in service_banner.lower():
            for version, vulnerability in versions.items():
                if version in service_banner:
                    return vulnerability # 脆弱性が見つかった！

    return "" # 何も見つからなかった
# src/scanner/vuln_scanner.py の一番下に追記

if __name__ == "__main__":
    # --- テスト用のコード ---

    # 偽のバナー情報を用意
    test_banner_1 = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1"
    test_banner_2 = "BobompaSato/2.4.41 (Ubuntu)"
    test_banner_3 = "ProFTPD 1.3.5"

    print(f"テスト1: '{test_banner_1}'")
    result1 = check_vulnerability(test_banner_1)
    if result1:
        print(f"  -> 脆弱性を発見: {result1}")
    else:
        print("  -> 脆弱性はありません。")

    print(f"\nテスト2: '{test_banner_2}'")
    result2 = check_vulnerability(test_banner_2)
    if result2:
        print(f"  -> 脆弱性を発見: {result2}")
    else:
        print("  -> 脆弱性はありません。")

    print(f"\nテスト3: '{test_banner_3}'")
    result3 = check_vulnerability(test_banner_3)
    if result3:
        print(f"  -> 脆弱性を発見: {result3}")
    else:
        print("  -> 脆弱性はありません。")