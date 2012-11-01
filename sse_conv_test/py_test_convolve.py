#!/usr/bin/env python

# Copyright (C) 2012 Henry Gomersall <heng@cantab.net> 
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY  THE AUTHOR ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

import numpy
import ctypes

def check_convolution(input_array, test_output, kernel):

    correct_output = numpy.convolve(input_array, kernel, mode='valid')

    return numpy.alltrue(correct_output - test_output == 0.0)

def get_function_wrapper(function_name, input_array, output_array, kernel,
        n_loops):

    if output_array.ndim != 1 or input_array.ndim != 1 or kernel.ndim != 1:
        raise ValueError('All the arrays should be dimension 1.')

    if len(kernel) > len(input_array):
        raise ValueError('The kernel should be shorter than the input '
                'array')

    if (input_array.dtype != 'float32' or output_array.dtype != 'float32'
            or kernel.dtype != 'float32'):
        raise ValueError('All the arrays should be of type \'float32\'')

    if len(output_array) != len(input_array) - len(kernel) + 1:
        raise ValueError('Output array should be of length '
                'len(input_array) - len(kernel) + 1')

    if len(input_array)%4 != 0:
        raise ValueError('The input array should be divisible by 4.')

    lib = numpy.ctypeslib.load_library('libconvolve_funcs', '.')

    c_function = getattr(lib, function_name)
    c_function.restype = ctypes.c_int
    c_function.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.c_int]

    input_pointer = input_array.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float))
    output_pointer = output_array.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float))

    length = len(input_array)
    kernel_pointer = kernel.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float))
    kernel_length = len(kernel)

    def function_wrapper():
        c_function(input_pointer, output_pointer, length, kernel_pointer, 
                kernel_length, n_loops)

    return function_wrapper

