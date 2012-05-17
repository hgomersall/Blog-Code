
from libc.stdlib cimport free

cdef extern from "hello_string.h":
    char *hello_string()


def get_string_from_lib():

    cdef bytes py_string

    cdef char* c_string = hello_string()

    try:
        py_string = c_string
        print 'In the cython code:', py_string
    finally:
        print 'Trying to free the C string...'
        free(c_string)
        print 'Freed successfully'

    return py_string
