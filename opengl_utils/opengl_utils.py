#!/usr/bin/env python
# vim:sw=4:ts=4:et 
#
# Copyright 2011 Knowledge Economy Developments Ltd

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Henry Gomersall
# heng@kedevelopments.co.uk

''' Utilities for wrapping some OpenGL stuff into a
more pythonic set of objects.
'''
import numpy
from OpenGL import GL
from OpenGL.GL.ARB import sync as GL_sync
import ctypes

# Map the GL types to bytes per texel.
#
# The following is required knowledge to minimise
# the risk of segfaulting when copying data out
# of the numpy arrays.
GL_TYPES = {GL.GL_UNSIGNED_BYTE:           1,
        GL.GL_BYTE:                        1,
        #GL.GL_BITMAP - We ignore this.
        GL.GL_UNSIGNED_SHORT:              2,
        GL.GL_SHORT:                       2,
        GL.GL_UNSIGNED_INT:                4,
        GL.GL_INT:                         4,
        GL.GL_FLOAT:                       4,
        GL.GL_UNSIGNED_BYTE_3_3_2:         1,
        GL.GL_UNSIGNED_BYTE_2_3_3_REV:     1,
        GL.GL_UNSIGNED_SHORT_5_6_5:        2,
        GL.GL_UNSIGNED_SHORT_5_6_5_REV:    2,
        GL.GL_UNSIGNED_SHORT_4_4_4_4:      2,
        GL.GL_UNSIGNED_SHORT_4_4_4_4_REV:  2,
        GL.GL_UNSIGNED_SHORT_5_5_5_1:      2,
        GL.GL_UNSIGNED_SHORT_1_5_5_5_REV:  2,
        GL.GL_UNSIGNED_INT_8_8_8_8:        4,
        GL.GL_UNSIGNED_INT_8_8_8_8_REV:    4,
        GL.GL_UNSIGNED_INT_10_10_10_2:     4,
        GL.GL_UNSIGNED_INT_2_10_10_10_REV: 4}

class TextureStream2D(object):
    ''' A class that defines a 2D texture stream. A
    texture stream in this context is an object through
    which a texture that is used in rendering is
    updated repeatedly. The intention of this class
    is to provide a simple way in which users can
    make use of pixel buffer objects to stream
    textures asynchronously without having to
    worry about synchronising the uploads with
    the rendering. It makes use of multiple
    buffers (2 by default) so any rendering code
    has something to work with whilst an upload
    is going on.

    The idea is that the most recent texture upload is
    bound when instance.bind_texture() is called.

    Textures are uploaded using update_texture() or
    update_texture_with_clear(). The latter clearing
    the texture before upload if the data is not
    going to overwrite the non-blank sections of 
    the texture because it isn't big enough.

    If an attempt is made to upload a texture whilst
    non of the previous uploads have finished and
    there are no more remaining buffers that are 
    currently unused (either for upload or for
    reading) then the data will just be ignored.

    The class can be used as a texture context manager.
    In this case, the textures are uploaded as 
    described, but they are used within the 
    context manager which takes care of binding
    the correct texture. For example:

    with texture_stream_2d_instance:
        the rendering code
        goes
        here
        :

    '''
    
    def __init__(self, size, gl_format, gl_type, gl_internal_format,
            buffers=2, buffer_usage=GL.GL_STREAM_DRAW):
        ''' Initialise the texture stream.

        size is a tuple or similarly indexable array with
        the first entry giving the x-dimension and the second
        the y-dimension.

        gl_format, gl_type and gl_internal_format are all
        referenced at:
        http://www.opengl.org/sdk/docs/man/xhtml/glTexImage2D.xml
        
        (under the subheadings given by format, type
        and internalformat respectively), and the 
        arguments should satisfy those descriptions.

        The argument buffers is the number of pixel
        buffer objects, and by extension the number
        of textures, that are used by an instance
        for buffering the texture uploads. More buffers
        uses more on-card memory and its probably 
        pointless to have more than 2 or 3.

        buffer_usage is a description of how the
        buffer is likely to be used and gives a
        hint to the hardware about how to allocate
        the buffers. See:
        http://www.opengl.org/sdk/docs/man/xhtml/glBufferData.xml
        for more information (under 'usage').
        '''
        # Args
        self.__size = size
        self.__gl_format = gl_format
        self.__gl_type = gl_type
        self.__gl_internal_format = gl_internal_format
        self.__buffer_usage = buffer_usage
        
        # The number of pixel buffers that are used for
        # streaming the textures.
        self.__n_pixel_buffers = buffers

        if not GL_TYPES.has_key(self.__gl_type):
            raise ValueError(repr(self.__gl_type) + ' is not a valid type.')

        # Set up variables
        self.__data_silhouette = None
        self.__copy_sync = [GLSyncObject()] * self.__n_pixel_buffers
        self.__read_idx = 0
        self.__write_idx = 0
        
        for each_sync in self.__copy_sync:
            status = each_sync.block_until_signalled()
            if status is GLSyncObject.GL_TIMEOUT_EXPIRED:
                raise RuntimeError('Problem clearing the OpenGL pipeline in a '\
                    'reasonable time frame.')

        # Initialise the textures
        self.__textures = GL.glGenTextures(self.__n_pixel_buffers)
        if self.__n_pixel_buffers == 1:
            self.__textures = [self.__textures]
        
        for each_texture in self.__textures:
            GL.glBindTexture(GL.GL_TEXTURE_2D, each_texture)

            GL.glTexImage2D(
                GL.GL_TEXTURE_2D,
                0, self.__gl_internal_format, self.__size[0], self.__size[1],
                0, self.__gl_format, self.__gl_type, None)
        
            # Set up the texture parameters
            # Nearest neighbour filters, clamping texture coordinates to 
            # between 0 and 1.http://docs.python.org/library/exceptions.html#exceptions.RuntimeError
            GL.glTexParameterf(GL.GL_TEXTURE_2D, \
                    GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, \
                    GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, \
                    GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, \
                    GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)

        # We're done with those textures
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        
        buffer_size = self.__size[0]*self.__size[1]*GL_TYPES[self.__gl_type]

        # Set up the pixel buffers
        self.__pixel_buffers = GL.glGenBuffers(self.__n_pixel_buffers)
        if self.__n_pixel_buffers == 1:
            self.__pixel_buffers = [self.__pixel_buffers]

        for pixel_buffer in self.__pixel_buffers:
            GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, pixel_buffer)
            GL.glBufferData(GL.GL_PIXEL_UNPACK_BUFFER, buffer_size, 
                    None, self.__buffer_usage)

        # we're finished setting up the buffers so
        # we bind it to 0
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
        
        # Initialize empty textures (just need to pass a single
        # texel).
        for n in range(0,self.__n_pixel_buffers):
            self.update_texture_with_clear(\
                    numpy.zeros((1,1,GL_TYPES[self.__gl_type]), dtype='uint8'))
        
        init_sync = GLSyncObject()
        
        status = init_sync.block_until_signalled(timeout=2.0)
        if status is GLSyncObject.GL_TIMEOUT_EXPIRED:
            raise RuntimeError('Problem initialising the textures in a '\
                    'reasonable time frame.')

    def __enter__(self):
        self.bind_texture()

    def __exit__(self, *args):
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        return False
    
    def __update_read_idx(self):
        '''Update the read index to the most 
        recently filled buffer.
        '''
        # Count backwards from the write index
        # until we get to a buffer that has signalled
        # completion. If none is found, the read index
        # remains unchanged.
        for n in range(0,self.__n_pixel_buffers):
            idx = (self.__write_idx-n)%self.__n_pixel_buffers
            if self.__copy_sync[idx].get_fence_signalled():
                self.__read_idx = idx
                break

    def bind_texture(self):
        ''' Bind the current texture to the OpenGL context 
        for rendering. You can release the texture in the
        usual way by binding the zero texture.
        i.e with GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        Alternatively, using the texture rendering code
        within the context manager defined by an instance
        of the class will bind the textures 
        automatically. Use this as:

        with texture_stream_2d_instance:
            rendering code
            goes
            here
        '''
        
        if self.__n_pixel_buffers is 1:
            texture_id = self.__textures[0]
        else:
            self.__update_read_idx()
            texture_id = self.__textures[self.__read_idx]

        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    
    def update_texture(self, data):
        '''Update the texture with a passed data array.

        The data is expected to be a three-dimensional
        array of size NxMxP (c-ordering), where N and M
        are the dimensions of the image and P is the
        number of array elements per texel. The type
        should agree with that set by the gl_type argument
        at instantiation. P only really makes a lot of
        sense if each array element that together make up
        a texel are the same size. For example, if the
        type is GL_UNSIGNED_SHORT_5_5_5_1, then its 2
        bytes per texel, but with a differing number of
        bits per colour, in which case the array can just
        be two-dimensional.  The crucial test is that
        data.itemsize*P is equal to the number of bytes
        per texel expected by gl_type.  Its up to you how
        the data is packed beyond that.

        This method will fill the texture from the
        beginning of the texture memory.
        
        If the data is smaller than the texture then
        outside the data is left untouched.
        
        If the data is bigger than the texture, an
        exception is raised.

        If an attempt is made to upload a texture whilst
        non of the previous uploads have finished and
        there are no more remaining buffers that are 
        currently unused (either for upload or for
        reading) then the data will just be ignored.
        '''
        if not self.__set_next_write_idx():
            return None

        GL.glBindTexture(GL.GL_TEXTURE_2D, 
                self.__textures[self.__write_idx])
        
        self.__update_texture(data)

        if data.shape[0:1] > self.__data_silhouette:
            self.__data_silhouette = data.shape[0:1]

    def __set_next_write_idx(self):
        ''' Set the next write index for updating
        the texture.

        Return True if the write buffer was update
        ok, otherwise False. False is returned
        if the next buffer is the one currently
        being read from.
        '''
        
        if self.__n_pixel_buffers is 1:
            self.__write_idx = 0
        else:
            # Firstly update the read index to the most current one.
            self.__update_read_idx()

            self.__write_idx = (self.__write_idx+1)%self.__n_pixel_buffers
            # The policy is that we don't overwrite the buffer that is 
            # currently being read from.
            if self.__write_idx == self.__read_idx:
                self.__write_idx = (self.__write_idx-1)%self.__n_pixel_buffers
                return False

        return True
        

    def __update_texture(self, data):
        ''' Method that actually does the texture
        updating after the self.__write_idx has 
        been set up and the correct texture
        has been bound.
        '''
        # A bit of data checking...
        _data = numpy.atleast_3d(data)
        
        if not data.itemsize*_data.shape[2] == \
                GL_TYPES[self.__gl_type]:
            raise ValueError('The number of bytes per texel for the '\
                    'passed data does not agree with that expected by '\
                    'the previously given GL type: ' + repr(self.__gl_type))
        
        # get the bytes per texel from GL_TYPES
        bytes_per_data_point = GL_TYPES[self.__gl_type]

        # Compute the buffer size from the defaults
        buffer_size = self.__size[0]*self.__size[1]*bytes_per_data_point
        
        data_size_to_copy = data.shape[0]\
                * data.shape[1] * bytes_per_data_point
        
        if data_size_to_copy > buffer_size:
            raise ValueError('The data array is larger than the texture.')
        
        # Bind the buffer
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER,
                self.__pixel_buffers[self.__write_idx])
        
        GL.glBufferData(GL.GL_PIXEL_UNPACK_BUFFER, buffer_size, 
                    None, self.__buffer_usage)
        
        # Map the buffer object to a pointer
        pbo_pointer = ctypes.cast(\
                GL.glMapBuffer(GL.GL_PIXEL_UNPACK_BUFFER, GL.GL_WRITE_ONLY),
                ctypes.POINTER(ctypes.c_ubyte))
        
        # Turn that pointer into a numpy array that spans
        # the whole block.
        pbo_array = numpy.ctypeslib.as_array(pbo_pointer, (buffer_size,))
        
        pbo_array[0:data_size_to_copy] = \
                data.view(dtype='uint8').ravel()

        # Unmap the buffer. This then pushes the memory
        # block to the graphics card with a DMA transfer??
        GL.glUnmapBuffer(GL.GL_PIXEL_UNPACK_BUFFER) 
        
        # Copy the image to the texture memory. Since
        # we have a buffer object, this copies it out
        # of that memory.
        GL.glTexSubImage2D(
            GL.GL_TEXTURE_2D, 0, 0, 0, 
            data.shape[1],
            data.shape[0], 
            self.__gl_format,
            self.__gl_type,
            None)
        
        self.__copy_sync[self.__write_idx] = GLSyncObject()

    def update_texture_with_clear(self, data):
        ''' Update the texture with a passed data array.

        The data is expected to be a three-dimensional
        array of size NxMxP (c-ordering), where N and M
        are the dimensions of the image and P is the
        number of array elements per texel. The type
        should agree with that set by the gl_type argument
        at instantiation. P only really makes a lot of
        sense if each array element that together make up
        a texel are the same size. For example, if the
        type is GL_UNSIGNED_SHORT_5_5_5_1, then its 2
        bytes per texel, but with a differing number of
        bits per colour, in which case the array can just
        be two-dimensional.  The crucial test is that
        data.itemsize*P is equal to the number of bytes
        per texel expected by gl_type.  Its up to you how
        the data is packed beyond that.

        This method will fill the texture from the
        beginning of the texture memory.  If the shape of
        data is different to a previous call to this
        method, then the texture is cleared first. The
        assumption is that the size will change rarely.
        
        If the data is bigger than the texture, an
        exception is raised.

        If an attempt is made to upload a texture whilst
        non of the previous uploads have finished and
        there are no more remaining buffers that are 
        currently unused (either for upload or for
        reading) then the data will just be ignored.
        '''
        if not self.__set_next_write_idx():
            return None
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, 
                self.__textures[self.__write_idx])
        
        # get the bytes per texel from GL_TYPES
        bytes_per_data_point = GL_TYPES[self.__gl_type]

        # Compute the buffer size from the defaults
        buffer_size = self.__size[0]*self.__size[1]*bytes_per_data_point
        
        # Clear the texture if the new data is smaller than
        # the old data in either dimension.
        if data.shape[0:1] < self.__data_silhouette:
            zero_texture = numpy.zeros(buffer_size, dtype='uint8')
            
            GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 
                    self.__pixel_buffers[self.__write_idx])
            
            GL.glBufferData(GL.GL_PIXEL_UNPACK_BUFFER, buffer_size, 
                        zero_texture, self.__buffer_usage)

            self.__data_silhouette = data.shape[0:1]
       
        self.__update_texture(data)
        

class GLSyncObject(object):
    ''' A pythonic wrapper around the GL fence sync
    methods.

    Create with GLSyncObject(). When the GLSyncObject 
    object goes out of scope, the GL fence is tidied 
    up automatically.
    '''
    GL_ALREADY_SIGNALED = GL_sync.GL_ALREADY_SIGNALED
    GL_TIMEOUT_EXPIRED = GL_sync.GL_TIMEOUT_EXPIRED 
    GL_CONDITION_SATISFIED = GL_sync.GL_CONDITION_SATISFIED
    GL_WAIT_FAILED = GL_sync.GL_WAIT_FAILED

    TIMEOUT_STATUS = {GL_sync.GL_ALREADY_SIGNALED: GL_ALREADY_SIGNALED,
            GL_sync.GL_TIMEOUT_EXPIRED: GL_TIMEOUT_EXPIRED,
            GL_sync.GL_CONDITION_SATISFIED: GL_CONDITION_SATISFIED,
            GL_sync.GL_WAIT_FAILED: GL_WAIT_FAILED}

    def __init__(self):

        self.__sync = \
                GL_sync.glFenceSync(GL_sync.GL_SYNC_GPU_COMMANDS_COMPLETE, 0)

    def __del__(self):
        GL_sync.glDeleteSync(self.__sync)
    
    def block_until_signalled(self, timeout=1.0):
        ''' Blocks until the fence has been signalled
        with the timeout given by timeout (in seconds). 
        
        This uses the built in glClientWaitSync method
        and passes back the return value. The return
        enumerations are reimplemented by this class as:

        GLSyncObject.GL_ALREADY_SIGNALED
        GLSyncObject.GL_TIMEOUT_EXPIRED
        GLSyncObject.GL_CONDITION_SATISFIED
        GLSyncObject.GL_WAIT_FAILED

        See the documentation for glClientWaitSync for 
        more information on these return values.
        '''
        ns_timeout = int(timeout*1000000000)
        status = GL_sync.glClientWaitSync(self.__sync,
                GL_sync.GL_SYNC_FLUSH_COMMANDS_BIT, ns_timeout)
        
        return self.TIMEOUT_STATUS[status]

    def get_fence_signalled(self):
        ''' Returns a boolean describing whether 
        the fence has been signalled.
        '''
        fence_status = GL.GLint(0)
        GL_sync.glGetSynciv(self.__sync,
                GL_sync.GL_SYNC_STATUS,
                GL.GLint(1), GL.GLint(0), fence_status)
        
        return (GL_sync.GL_SIGNALED == fence_status.value)
