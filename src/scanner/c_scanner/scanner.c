// src/scanner/c_scanner/scanner.c (修正後)

#include <Python.h>

// OSによってインクルードするヘッダーを切り替える
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    // Ws2_32.lib をリンクするよう指示
    #pragma comment(lib, "Ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
#endif

// Pythonから呼び出されるスキャン関数
static PyObject* scan_port(PyObject* self, PyObject* args) {
    const char* host;
    int port;

#ifdef _WIN32
    // WindowsのWinsockを初期化
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        Py_RETURN_FALSE;
    }
#endif

    if (!PyArg_ParseTuple(args, "si", &host, &port)) {
#ifdef _WIN32
        WSACleanup();
#endif
        return NULL;
    }

    // Windowsではソケットの型がSOCKET
#ifdef _WIN32
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
#else
    int sock = socket(AF_INET, SOCK_STREAM, 0);
#endif

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &serv_addr.sin_addr);

    int connect_status = connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    
#ifdef _WIN32
    closesocket(sock); // Windowsではclosesocket()を使う
#else
    close(sock);
#endif

#ifdef _WIN32
    // Winsockをクリーンアップ
    WSACleanup();
#endif

    if (connect_status < 0) {
        Py_RETURN_FALSE;
    } else {
        Py_RETURN_TRUE;
    }
}

// (これ以降のPyMethodDefやPyModuleDefなどは変更なし)
static PyMethodDef CScannerMethods[] = {
    {"scan_port", scan_port, METH_VARARGS, "Scan a single port."},
    {NULL, NULL, 0, NULL}
};
static struct PyModuleDef cscannermodule = {
    PyModuleDef_HEAD_INIT, "c_scanner", NULL, -1, CScannerMethods
};
PyMODINIT_FUNC PyInit_c_scanner(void) {
    return PyModule_Create(&cscannermodule);
}