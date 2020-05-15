#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// HTTP API: WP_Http_Encoding class
#// 
#// @package WordPress
#// @subpackage HTTP
#// @since 4.4.0
#// 
#// 
#// Core class used to implement deflate and gzip transfer encoding support for HTTP requests.
#// 
#// Includes RFC 1950, RFC 1951, and RFC 1952.
#// 
#// @since 2.8.0
#//
class WP_Http_Encoding():
    #// 
    #// Compress raw string using the deflate format.
    #// 
    #// Supports the RFC 1951 standard.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $raw String to compress.
    #// @param int $level Optional, default is 9. Compression level, 9 is highest.
    #// @param string $supports Optional, not used. When implemented it will choose the right compression based on what the server supports.
    #// @return string|false False on failure.
    #//
    @classmethod
    def compress(self, raw=None, level=9, supports=None):
        
        return gzdeflate(raw, level)
    # end def compress
    #// 
    #// Decompression of deflated string.
    #// 
    #// Will attempt to decompress using the RFC 1950 standard, and if that fails
    #// then the RFC 1951 standard deflate will be attempted. Finally, the RFC
    #// 1952 standard gzip decode will be attempted. If all fail, then the
    #// original compressed string will be returned.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $compressed String to decompress.
    #// @param int $length The optional length of the compressed data.
    #// @return string|bool False on failure.
    #//
    @classmethod
    def decompress(self, compressed=None, length=None):
        
        if php_empty(lambda : compressed):
            return compressed
        # end if
        decompressed = php_no_error(lambda: gzinflate(compressed))
        if False != decompressed:
            return decompressed
        # end if
        decompressed = self.compatible_gzinflate(compressed)
        if False != decompressed:
            return decompressed
        # end if
        decompressed = php_no_error(lambda: gzuncompress(compressed))
        if False != decompressed:
            return decompressed
        # end if
        if php_function_exists("gzdecode"):
            decompressed = php_no_error(lambda: gzdecode(compressed))
            if False != decompressed:
                return decompressed
            # end if
        # end if
        return compressed
    # end def decompress
    #// 
    #// Decompression of deflated string while staying compatible with the majority of servers.
    #// 
    #// Certain Servers will return deflated data with headers which PHP's gzinflate()
    #// function cannot handle out of the box. The following function has been created from
    #// various snippets on the gzinflate() PHP documentation.
    #// 
    #// Warning: Magic numbers within. Due to the potential different formats that the compressed
    #// data may be returned in, some "magic offsets" are needed to ensure proper decompression
    #// takes place. For a simple progmatic way to determine the magic offset in use, see:
    #// https://core.trac.wordpress.org/ticket/18273
    #// 
    #// @since 2.8.1
    #// @link https://core.trac.wordpress.org/ticket/18273
    #// @link https://www.php.net/manual/en/function.gzinflate.php#70875
    #// @link https://www.php.net/manual/en/function.gzinflate.php#77336
    #// 
    #// @param string $gzData String to decompress.
    #// @return string|bool False on failure.
    #//
    @classmethod
    def compatible_gzinflate(self, gzData=None):
        
        #// Compressed data might contain a full header, if so strip it for gzinflate().
        if php_substr(gzData, 0, 3) == "":
            i = 10
            flg = php_ord(php_substr(gzData, 3, 1))
            if flg > 0:
                if flg & 4:
                    xlen = unpack("v", php_substr(gzData, i, 2))
                    i = i + 2 + xlen
                # end if
                if flg & 8:
                    i = php_strpos(gzData, " ", i) + 1
                # end if
                if flg & 16:
                    i = php_strpos(gzData, " ", i) + 1
                # end if
                if flg & 2:
                    i = i + 2
                # end if
            # end if
            decompressed = php_no_error(lambda: gzinflate(php_substr(gzData, i, -8)))
            if False != decompressed:
                return decompressed
            # end if
        # end if
        #// Compressed data from java.util.zip.Deflater amongst others.
        decompressed = php_no_error(lambda: gzinflate(php_substr(gzData, 2)))
        if False != decompressed:
            return decompressed
        # end if
        return False
    # end def compatible_gzinflate
    #// 
    #// What encoding types to accept and their priority values.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $url
    #// @param array  $args
    #// @return string Types of encoding to accept.
    #//
    @classmethod
    def accept_encoding(self, url=None, args=None):
        
        type = Array()
        compression_enabled = self.is_available()
        if (not args["decompress"]):
            #// Decompression specifically disabled.
            compression_enabled = False
        elif args["stream"]:
            #// Disable when streaming to file.
            compression_enabled = False
        elif (php_isset(lambda : args["limit_response_size"])):
            #// If only partial content is being requested, we won't be able to decompress it.
            compression_enabled = False
        # end if
        if compression_enabled:
            if php_function_exists("gzinflate"):
                type[-1] = "deflate;q=1.0"
            # end if
            if php_function_exists("gzuncompress"):
                type[-1] = "compress;q=0.5"
            # end if
            if php_function_exists("gzdecode"):
                type[-1] = "gzip;q=0.5"
            # end if
        # end if
        #// 
        #// Filters the allowed encoding types.
        #// 
        #// @since 3.6.0
        #// 
        #// @param string[] $type Array of what encoding types to accept and their priority values.
        #// @param string   $url  URL of the HTTP request.
        #// @param array    $args HTTP request arguments.
        #//
        type = apply_filters("wp_http_accept_encoding", type, url, args)
        return php_implode(", ", type)
    # end def accept_encoding
    #// 
    #// What encoding the content used when it was compressed to send in the headers.
    #// 
    #// @since 2.8.0
    #// 
    #// @return string Content-Encoding string to send in the header.
    #//
    @classmethod
    def content_encoding(self):
        
        return "deflate"
    # end def content_encoding
    #// 
    #// Whether the content be decoded based on the headers.
    #// 
    #// @since 2.8.0
    #// 
    #// @param array|string $headers All of the available headers.
    #// @return bool
    #//
    @classmethod
    def should_decode(self, headers=None):
        
        if php_is_array(headers):
            if php_array_key_exists("content-encoding", headers) and (not php_empty(lambda : headers["content-encoding"])):
                return True
            # end if
        elif php_is_string(headers):
            return php_stripos(headers, "content-encoding:") != False
        # end if
        return False
    # end def should_decode
    #// 
    #// Whether decompression and compression are supported by the PHP version.
    #// 
    #// Each function is tested instead of checking for the zlib extension, to
    #// ensure that the functions all exist in the PHP version and aren't
    #// disabled.
    #// 
    #// @since 2.8.0
    #// 
    #// @return bool
    #//
    @classmethod
    def is_available(self):
        
        return php_function_exists("gzuncompress") or php_function_exists("gzdeflate") or php_function_exists("gzinflate")
    # end def is_available
# end class WP_Http_Encoding
