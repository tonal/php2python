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
#// Handles creating objects and calling methods
#// 
#// Access this via {@see SimplePie::get_registry()}
#// 
#// @package SimplePie
#//
class SimplePie_Registry():
    default = Array({"Cache": "SimplePie_Cache", "Locator": "SimplePie_Locator", "Parser": "SimplePie_Parser", "File": "SimplePie_File", "Sanitize": "SimplePie_Sanitize", "Item": "SimplePie_Item", "Author": "SimplePie_Author", "Category": "SimplePie_Category", "Enclosure": "SimplePie_Enclosure", "Caption": "SimplePie_Caption", "Copyright": "SimplePie_Copyright", "Credit": "SimplePie_Credit", "Rating": "SimplePie_Rating", "Restriction": "SimplePie_Restriction", "Content_Type_Sniffer": "SimplePie_Content_Type_Sniffer", "Source": "SimplePie_Source", "Misc": "SimplePie_Misc", "XML_Declaration_Parser": "SimplePie_XML_Declaration_Parser", "Parse_Date": "SimplePie_Parse_Date"})
    classes = Array()
    legacy = Array()
    #// 
    #// Constructor
    #// 
    #// No-op
    #//
    def __init__(self):
        
        pass
    # end def __init__
    #// 
    #// Register a class
    #// 
    #// @param string $type See {@see $default} for names
    #// @param string $class Class name, must subclass the corresponding default
    #// @param bool $legacy Whether to enable legacy support for this class
    #// @return bool Successfulness
    #//
    def register(self, type=None, class_=None, legacy=False):
        
        if (not is_subclass_of(class_, self.default[type])):
            return False
        # end if
        self.classes[type] = class_
        if legacy:
            self.legacy[-1] = class_
        # end if
        return True
    # end def register
    #// 
    #// Get the class registered for a type
    #// 
    #// Where possible, use {@see create()} or {@see call()} instead
    #// 
    #// @param string $type
    #// @return string|null
    #//
    def get_class(self, type=None):
        
        if (not php_empty(lambda : self.classes[type])):
            return self.classes[type]
        # end if
        if (not php_empty(lambda : self.default[type])):
            return self.default[type]
        # end if
        return None
    # end def get_class
    #// 
    #// Create a new instance of a given type
    #// 
    #// @param string $type
    #// @param array $parameters Parameters to pass to the constructor
    #// @return object Instance of class
    #//
    def create(self, type=None, parameters=Array()):
        
        class_ = self.get_class(type)
        if php_in_array(class_, self.legacy):
            for case in Switch(type):
                if case("locator"):
                    #// Legacy: file, timeout, useragent, file_class, max_checked_feeds, content_type_sniffer_class
                    #// Specified: file, timeout, useragent, max_checked_feeds
                    replacement = Array(self.get_class("file"), parameters[3], self.get_class("content_type_sniffer"))
                    array_splice(parameters, 3, 1, replacement)
                    break
                # end if
            # end for
        # end if
        if (not php_method_exists(class_, "__construct")):
            instance = php_new_class(class_, lambda : {**locals(), **globals()}[class_]())
        else:
            reflector = php_new_class("ReflectionClass", lambda : ReflectionClass(class_))
            instance = reflector.newinstanceargs(parameters)
        # end if
        if php_method_exists(instance, "set_registry"):
            instance.set_registry(self)
        # end if
        return instance
    # end def create
    #// 
    #// Call a static method for a type
    #// 
    #// @param string $type
    #// @param string $method
    #// @param array $parameters
    #// @return mixed
    #//
    def call(self, type=None, method=None, parameters=Array()):
        
        class_ = self.get_class(type)
        if php_in_array(class_, self.legacy):
            for case in Switch(type):
                if case("Cache"):
                    #// For backwards compatibility with old non-static
                    #// Cache::create() methods
                    if method == "get_handler":
                        result = php_no_error(lambda: call_user_func_array(Array(class_, "create"), parameters))
                        return result
                    # end if
                    break
                # end if
            # end for
        # end if
        result = call_user_func_array(Array(class_, method), parameters)
        return result
    # end def call
# end class SimplePie_Registry
