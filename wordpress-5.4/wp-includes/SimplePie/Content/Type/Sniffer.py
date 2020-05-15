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
#// SimplePie
#// 
#// A PHP-Based RSS and Atom Feed Framework.
#// Takes the hard work out of managing a complete RSS/Atom solution.
#// 
#// Copyright (c) 2004-2012, Ryan Parman, Geoffrey Sneddon, Ryan McCue, and contributors
#// All rights reserved.
#// 
#// Redistribution and use in source and binary forms, with or without modification, are
#// permitted provided that the following conditions are met:
#// 
#// Redistributions of source code must retain the above copyright notice, this list of
#// conditions and the following disclaimer.
#// 
#// Redistributions in binary form must reproduce the above copyright notice, this list
#// of conditions and the following disclaimer in the documentation and/or other materials
#// provided with the distribution.
#// 
#// Neither the name of the SimplePie Team nor the names of its contributors may be used
#// to endorse or promote products derived from this software without specific prior
#// written permission.
#// 
#// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
#// OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#// AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS
#// AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#// POSSIBILITY OF SUCH DAMAGE.
#// 
#// @package SimplePie
#// @version 1.3.1
#// @copyright 2004-2012 Ryan Parman, Geoffrey Sneddon, Ryan McCue
#// @author Ryan Parman
#// @author Geoffrey Sneddon
#// @author Ryan McCue
#// @link http://simplepie.org/ SimplePie
#// @license http://www.opensource.org/licenses/bsd-license.php BSD License
#// 
#// 
#// Content-type sniffing
#// 
#// Based on the rules in http://tools.ietf.org/html/draft-abarth-mime-sniff-06
#// 
#// This is used since we can't always trust Content-Type headers, and is based
#// upon the HTML5 parsing rules.
#// 
#// 
#// This class can be overloaded with {@see SimplePie::set_content_type_sniffer_class()}
#// 
#// @package SimplePie
#// @subpackage HTTP
#//
class SimplePie_Content_Type_Sniffer():
    file = Array()
    #// 
    #// Create an instance of the class with the input file
    #// 
    #// @param SimplePie_Content_Type_Sniffer $file Input file
    #//
    def __init__(self, file=None):
        
        self.file = file
    # end def __init__
    #// 
    #// Get the Content-Type of the specified file
    #// 
    #// @return string Actual Content-Type
    #//
    def get_type(self):
        
        if (php_isset(lambda : self.file.headers["content-type"])):
            if (not (php_isset(lambda : self.file.headers["content-encoding"]))) and self.file.headers["content-type"] == "text/plain" or self.file.headers["content-type"] == "text/plain; charset=ISO-8859-1" or self.file.headers["content-type"] == "text/plain; charset=iso-8859-1" or self.file.headers["content-type"] == "text/plain; charset=UTF-8":
                return self.text_or_binary()
            # end if
            pos = php_strpos(self.file.headers["content-type"], ";")
            if pos != False:
                official = php_substr(self.file.headers["content-type"], 0, pos)
            else:
                official = self.file.headers["content-type"]
            # end if
            official = php_trim(php_strtolower(official))
            if official == "unknown/unknown" or official == "application/unknown":
                return self.unknown()
            elif php_substr(official, -4) == "+xml" or official == "text/xml" or official == "application/xml":
                return official
            elif php_substr(official, 0, 6) == "image/":
                return_ = self.image()
                if return_:
                    return return_
                else:
                    return official
                # end if
            elif official == "text/html":
                return self.feed_or_html()
            else:
                return official
            # end if
        else:
            return self.unknown()
        # end if
    # end def get_type
    #// 
    #// Sniff text or binary
    #// 
    #// @return string Actual Content-Type
    #//
    def text_or_binary(self):
        
        if php_substr(self.file.body, 0, 2) == "þÿ" or php_substr(self.file.body, 0, 2) == "ÿþ" or php_substr(self.file.body, 0, 4) == "  þÿ" or php_substr(self.file.body, 0, 3) == "ï»¿":
            return "text/plain"
        elif php_preg_match("/[\\x00-\\x08\\x0E-\\x1A\\x1C-\\x1F]/", self.file.body):
            return "application/octect-stream"
        else:
            return "text/plain"
        # end if
    # end def text_or_binary
    #// 
    #// Sniff unknown
    #// 
    #// @return string Actual Content-Type
    #//
    def unknown(self):
        
        ws = strspn(self.file.body, "   \n\r ")
        if php_strtolower(php_substr(self.file.body, ws, 14)) == "<!doctype html" or php_strtolower(php_substr(self.file.body, ws, 5)) == "<html" or php_strtolower(php_substr(self.file.body, ws, 7)) == "<script":
            return "text/html"
        elif php_substr(self.file.body, 0, 5) == "%PDF-":
            return "application/pdf"
        elif php_substr(self.file.body, 0, 11) == "%!PS-Adobe-":
            return "application/postscript"
        elif php_substr(self.file.body, 0, 6) == "GIF87a" or php_substr(self.file.body, 0, 6) == "GIF89a":
            return "image/gif"
        elif php_substr(self.file.body, 0, 8) == "PNG\r\n\n":
            return "image/png"
        elif php_substr(self.file.body, 0, 3) == "ÿØÿ":
            return "image/jpeg"
        elif php_substr(self.file.body, 0, 2) == "BM":
            return "image/bmp"
        elif php_substr(self.file.body, 0, 4) == "   ":
            return "image/vnd.microsoft.icon"
        else:
            return self.text_or_binary()
        # end if
    # end def unknown
    #// 
    #// Sniff images
    #// 
    #// @return string Actual Content-Type
    #//
    def image(self):
        
        if php_substr(self.file.body, 0, 6) == "GIF87a" or php_substr(self.file.body, 0, 6) == "GIF89a":
            return "image/gif"
        elif php_substr(self.file.body, 0, 8) == "PNG\r\n\n":
            return "image/png"
        elif php_substr(self.file.body, 0, 3) == "ÿØÿ":
            return "image/jpeg"
        elif php_substr(self.file.body, 0, 2) == "BM":
            return "image/bmp"
        elif php_substr(self.file.body, 0, 4) == "   ":
            return "image/vnd.microsoft.icon"
        else:
            return False
        # end if
    # end def image
    #// 
    #// Sniff HTML
    #// 
    #// @return string Actual Content-Type
    #//
    def feed_or_html(self):
        
        len = php_strlen(self.file.body)
        pos = strspn(self.file.body, "  \n\r ")
        while True:
            
            if not (pos < len):
                break
            # end if
            for case in Switch(self.file.body[pos]):
                if case("   "):
                    pass
                # end if
                if case("\n"):
                    pass
                # end if
                if case("\r"):
                    pass
                # end if
                if case(" "):
                    pos += strspn(self.file.body, " \n\r ", pos)
                    continue
                # end if
                if case("<"):
                    pos += 1
                    break
                # end if
                if case():
                    return "text/html"
                # end if
            # end for
            if php_substr(self.file.body, pos, 3) == "!--":
                pos += 3
                pos = php_strpos(self.file.body, "-->", pos)
                if pos < len and pos != False:
                    pos += 3
                else:
                    return "text/html"
                # end if
            elif php_substr(self.file.body, pos, 1) == "!":
                pos = php_strpos(self.file.body, ">", pos)
                if pos < len and pos != False:
                    pos += 1
                else:
                    return "text/html"
                # end if
            elif php_substr(self.file.body, pos, 1) == "?":
                pos = php_strpos(self.file.body, "?>", pos)
                if pos < len and pos != False:
                    pos += 2
                else:
                    return "text/html"
                # end if
            elif php_substr(self.file.body, pos, 3) == "rss" or php_substr(self.file.body, pos, 7) == "rdf:RDF":
                return "application/rss+xml"
            elif php_substr(self.file.body, pos, 4) == "feed":
                return "application/atom+xml"
            else:
                return "text/html"
            # end if
        # end while
        return "text/html"
    # end def feed_or_html
# end class SimplePie_Content_Type_Sniffer
