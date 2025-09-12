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
#endif

// ポートスキャン関数
static PyObject *scan_port_c(PyObject *self, PyObject *args)
{
    // ...（scan_port のコード）...
    Py_RETURN_TRUE; // 仮
}

// メソッド定義
static PyMethodDef CScannerMethods[] = {
    {"scan_port", scan_port_c, METH_VARARGS, "Scan a single port."},
    {NULL, NULL, 0, NULL}};

// モジュール定義
static struct PyModuleDef cscannermodule = {
    PyModuleDef_HEAD_INIT,
    "c_scanner", // ← モジュール名と一致
    NULL,
    -1,
    CScannerMethods};

// モジュール初期化関数
PyMODINIT_FUNC PyInit_c_scanner(void)
{
    return PyModule_Create(&cscannermodule);
}
