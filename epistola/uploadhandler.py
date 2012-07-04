# vim: set ts=4 sw=4 sts=4 et ai:
import mimetypes
from urllib import unquote

from django.core.files.uploadhandler import StopFutureHandlers,\
        MemoryFileUploadHandler, TemporaryFileUploadHandler
from django.http import QueryDict
from django.http.multipartparser import ChunkIter, MultiPartParserError
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_unicode


class AjaxUploadHandlerMixin(object):
    '''
    Ajax upload handler mixin which creates the FILES structure with a
    single file ``file`` which is created from the complete POST request body.

    It can be combined with MemoryFileUploadHandler and
    TemporaryFileUploadHandler.
    '''
    def __init__(self, *args, **kwargs):
        self.field_name = kwargs.pop('field_name', 'f')
        super(AjaxUploadHandlerMixin, self).__init__(*args, **kwargs)

    def handle_raw_input(self, input_data, META, content_length, boundary,
            encoding=None):
        super(AjaxUploadHandlerMixin, self).handle_raw_input(input_data, META,
                content_length, boundary, encoding)
        if META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            return # request is not an ajax request
        if not getattr(self, 'activated', True):
            return # file is too large for MemoryFileUploadHandler

        # filename is set as a header as well as a GET param
        file_name = META.get('HTTP_X_FILE_NAME', META.get('X_FILE_NAME'))
        if file_name is None:
            raise MultiPartParserError('Invalid File-Name: %r' % file_name)

        # clean the filename, taken from the default MultiPartParser
        file_name = force_unicode(file_name, encoding, errors='replace')
        file_name = self.IE_sanitize(unquote(file_name))
        if not file_name:
            raise MultiPartParserError('Invalid File-Name: %r' % file_name)

        # the javascript does not try to set the content_type
        # so we guess it from the filename.
        content_type, enc = mimetypes.guess_type(file_name)

        chunk_start = 0
        try:
            self.new_file(self.field_name, file_name, content_type,
                    content_length, encoding)
        except StopFutureHandlers:
            pass # expected from MemoryFileUploadHandler

        # feed the file to the real upload handler.
        for chunk in ChunkIter(input_data, self.chunk_size):
            chunk_length = len(chunk)
            self.receive_data_chunk(chunk, chunk_start)
            chunk_start += chunk_length
        file_obj = self.file_complete(chunk_start)

        # create the POST and FILES datastructures
        post = QueryDict(MultiValueDict(), encoding=encoding)
        files = MultiValueDict()
        if file_obj:
            files.appendlist(self.field_name, file_obj)
        return post, files

    def IE_sanitize(self, filename):
        '''Cleanup filename from Internet Explorer full paths.'''
        return filename and filename[filename.rfind('\\')+1:].strip()

class AjaxTemporaryFileUploadHandler(AjaxUploadHandlerMixin,
        TemporaryFileUploadHandler):
    pass

class AjaxMemoryFileUploadHandler(AjaxUploadHandlerMixin,
        MemoryFileUploadHandler):
    pass
