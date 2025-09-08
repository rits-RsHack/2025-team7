// C言語で書くスキャン機能(将来用)
#include <Python.h>
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

static PyObject *scan_port_c(PyObject *self, PyObject *args)
{
    const char *host;
    int port;

    // Pythonから渡された引数 (文字列, 整数) をCの変数に変換
    if (!PyArg_ParseTuple(args, "si", &host, &port))
    {
        return NULL; // 引数のパースに失敗
    }

    // 1. ソケットを作成
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
        Py_RETURN_FALSE; // ソケット作成失敗
    }

    // 2. 接続先情報(アドレス、ポート)を設定
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port); // ポート番号をネットワークバイトオーダーに変換

    // IPアドレスをバイナリ形式に変換
    if (inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0)
    {
        close(sock);
        Py_RETURN_FALSE; // 無効なIPアドレス
    }

    // 3. 接続を試みる
    // タイムアウトを設定するのが望ましいが、シンプルにするためここでは省略
    int connect_status = connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

    // 4. ソケットを閉じる
    close(sock);

    // 5. 接続結果をPythonに返す
    if (connect_status < 0)
    {
        Py_RETURN_FALSE; // 接続失敗 (ポートはクローズ)
    }
    else
    {
        Py_RETURN_TRUE; // 接続成功 (ポートはオープン)
    }
}

// Pythonモジュールに登録するメソッドのリスト
static PyMethodDef CScannerMethods[] = {
    {"scan_port", scan_port_c, METH_VARARGS, "Scan a single port."},
    {NULL, NULL, 0, NULL}};

// Pythonモジュールの定義
static struct PyModuleDef cscannermodule = {
    PyModuleDef_HEAD_INIT,
    "c_scanner", // モジュール名
    NULL,        // モジュールのドキュメント (今回はなし)
    -1,
    CScannerMethods};

// Pythonがモジュールをインポートしたときに呼び出される初期化関数
PyMODINIT_FUNC PyInit_c_scanner(void)
{
    return PyModule_Create(&cscannermodule);
}