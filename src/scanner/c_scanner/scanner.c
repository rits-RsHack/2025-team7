#include <Python.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#endif

static PyObject *scan_port_c(PyObject *self, PyObject *args)
{
    const char *ip;
    int port;
    int timeout = 3; // デフォルトタイムアウト

    if (!PyArg_ParseTuple(args, "si|i", &ip, &port, &timeout))
        return NULL;

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "WSAStartup failed");
        return NULL;
    }

    SOCKET sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == INVALID_SOCKET)
    {
        WSACleanup();
        PyErr_SetString(PyExc_RuntimeError, "Failed to create socket");
        return NULL;
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = inet_addr(ip); // 安定版：inet_addr()を使用

    if (addr.sin_addr.s_addr == INADDR_NONE)
    {
        closesocket(sockfd);
        WSACleanup();
        PyErr_SetString(PyExc_ValueError, "Invalid IP address");
        return NULL;
    }

    // ブロッキング接続 + タイムアウト設定
    DWORD timeout_ms = timeout * 1000;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout_ms, sizeof(timeout_ms));
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, (const char *)&timeout_ms, sizeof(timeout_ms));

    int result = connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));
    closesocket(sockfd);
    WSACleanup();

    if (result == 0)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;

#else
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create socket");
        return NULL;
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0)
    {
        close(sockfd);
        PyErr_SetString(PyExc_ValueError, "Invalid IP address");
        return NULL;
    }

    // 非ブロッキング + select
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    int conn_result = connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));
    if (conn_result < 0 && errno != EINPROGRESS)
    {
        close(sockfd);
        Py_RETURN_FALSE;
    }

    fd_set fdset;
    struct timeval tv;
    FD_ZERO(&fdset);
    FD_SET(sockfd, &fdset);
    tv.tv_sec = timeout;
    tv.tv_usec = 0;

    int sel = select(sockfd + 1, NULL, &fdset, NULL, &tv);
    if (sel > 0)
    {
        int so_error;
        socklen_t len = sizeof(so_error);
        getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &so_error, &len);
        close(sockfd);
        if (so_error == 0)
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    }
    else
    {
        close(sockfd);
        Py_RETURN_FALSE;
    }
#endif

    Py_RETURN_FALSE;
}

// メソッド定義
static PyMethodDef CScannerMethods[] = {
    {"scan_port", scan_port_c, METH_VARARGS, "Scan a single TCP port."},
    {NULL, NULL, 0, NULL}};

// モジュール定義
static struct PyModuleDef cscannermodule = {
    PyModuleDef_HEAD_INIT,
    "c_scanner",
    NULL,
    -1,
    CScannerMethods};

// モジュール初期化
PyMODINIT_FUNC PyInit_c_scanner(void)
{
    return PyModule_Create(&cscannermodule);
}
