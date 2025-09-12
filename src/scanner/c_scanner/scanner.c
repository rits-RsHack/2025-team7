// src/scanner/c_scanner/scanner_timeout.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#endif

#include <stdio.h>

// --- タイムアウト付きスキャン関数 ---
static PyObject *scan_port(PyObject *self, PyObject *args)
{
    const char *host;
    int port;
    int timeout_ms = 500; // デフォルト 500ms

    if (!PyArg_ParseTuple(args, "si|i", &host, &port, &timeout_ms))
        return NULL;

#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
        return PyBool_FromLong(0);
#endif

#ifdef _WIN32
    SOCKET sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sockfd == INVALID_SOCKET)
    {
        WSACleanup();
        return PyBool_FromLong(0);
    }
#else
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        return PyBool_FromLong(0);
#endif

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
#ifdef _WIN32
    inet_pton(AF_INET, host, &addr.sin_addr);
#else
    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0)
    {
        close(sockfd);
        return PyBool_FromLong(0);
    }
#endif

    int result = 0;

#ifdef _WIN32
    // ノンブロッキング
    u_long mode = 1;
    ioctlsocket(sockfd, FIONBIO, &mode);

    connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));
    WSAPOLLFD fdarray;
    fdarray.fd = sockfd;
    fdarray.events = POLLRDNORM | POLLWRNORM;

    int poll_res = WSAPoll(&fdarray, 1, timeout_ms);
    if (poll_res > 0 && (fdarray.revents & POLLWRNORM))
        result = 1;

    closesocket(sockfd);
    WSACleanup();
#else
    // ノンブロッキング
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));

    fd_set fdset;
    struct timeval tv;
    FD_ZERO(&fdset);
    FD_SET(sockfd, &fdset);
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    if (select(sockfd + 1, NULL, &fdset, NULL, &tv) > 0)
    {
        int so_error = 0;
        socklen_t len = sizeof(so_error);
        getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &so_error, &len);
        if (so_error == 0)
            result = 1;
    }

    close(sockfd);
#endif

    return PyBool_FromLong(result);
}

// --- モジュール定義 ---
static PyMethodDef ScannerMethods[] = {
    {"scan_port", scan_port, METH_VARARGS, "Scan a TCP port with timeout (returns True if open)"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef scannermodule = {
    PyModuleDef_HEAD_INIT,
    "c_scanner",
    "C-based fast port scanner with timeout",
    -1,
    ScannerMethods};

PyMODINIT_FUNC PyInit_c_scanner(void)
{
    return PyModule_Create(&scannermodule);
}
