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
#// "Inline" diff renderer.
#// 
#// Copyright 2004-2010 The Horde Project (http://www.horde.org/)
#// 
#// See the enclosed file COPYING for license information (LGPL). If you did
#// not receive this file, see http://opensource.org/licenses/lgpl-license.php.
#// 
#// @author  Ciprian Popovici
#// @package Text_Diff
#// 
#// Text_Diff_Renderer
#// WP #7391
php_include_file(php_dirname(php_dirname(__FILE__)) + "/Renderer.php", once=True)
#// 
#// "Inline" diff renderer.
#// 
#// This class renders diffs in the Wiki-style "inline" format.
#// 
#// @author  Ciprian Popovici
#// @package Text_Diff
#//
class Text_Diff_Renderer_inline(Text_Diff_Renderer):
    _leading_context_lines = 10000
    _trailing_context_lines = 10000
    _ins_prefix = "<ins>"
    _ins_suffix = "</ins>"
    _del_prefix = "<del>"
    _del_suffix = "</del>"
    _block_header = ""
    _split_characters = False
    _split_level = "lines"
    def _blockheader(self, xbeg=None, xlen=None, ybeg=None, ylen=None):
        
        return self._block_header
    # end def _blockheader
    def _startblock(self, header=None):
        
        return header
    # end def _startblock
    def _lines(self, lines=None, prefix=" ", encode=True):
        
        if encode:
            array_walk(lines, Array(self, "_encode"))
        # end if
        if self._split_level == "lines":
            return php_implode("\n", lines) + "\n"
        else:
            return php_implode("", lines)
        # end if
    # end def _lines
    def _added(self, lines=None):
        
        array_walk(lines, Array(self, "_encode"))
        lines[0] = self._ins_prefix + lines[0]
        lines[php_count(lines) - 1] += self._ins_suffix
        return self._lines(lines, " ", False)
    # end def _added
    def _deleted(self, lines=None, words=False):
        
        array_walk(lines, Array(self, "_encode"))
        lines[0] = self._del_prefix + lines[0]
        lines[php_count(lines) - 1] += self._del_suffix
        return self._lines(lines, " ", False)
    # end def _deleted
    def _changed(self, orig=None, final=None):
        
        #// If we've already split on characters, just display.
        if self._split_level == "characters":
            return self._deleted(orig) + self._added(final)
        # end if
        #// If we've already split on words, just display.
        if self._split_level == "words":
            prefix = ""
            while True:
                
                if not (orig[0] != False and final[0] != False and php_substr(orig[0], 0, 1) == " " and php_substr(final[0], 0, 1) == " "):
                    break
                # end if
                prefix += php_substr(orig[0], 0, 1)
                orig[0] = php_substr(orig[0], 1)
                final[0] = php_substr(final[0], 1)
            # end while
            return prefix + self._deleted(orig) + self._added(final)
        # end if
        text1 = php_implode("\n", orig)
        text2 = php_implode("\n", final)
        #// Non-printing newline marker.
        nl = " "
        if self._split_characters:
            diff = php_new_class("Text_Diff", lambda : Text_Diff("native", Array(php_preg_split("//", text1), php_preg_split("//", text2))))
        else:
            #// We want to split on word boundaries, but we need to preserve
            #// whitespace as well. Therefore we split on words, but include
            #// all blocks of whitespace in the wordlist.
            diff = php_new_class("Text_Diff", lambda : Text_Diff("native", Array(self._splitonwords(text1, nl), self._splitonwords(text2, nl))))
        # end if
        #// Get the diff in inline format.
        renderer = php_new_class("Text_Diff_Renderer_inline", lambda : Text_Diff_Renderer_inline(php_array_merge(self.getparams(), Array({"split_level": "characters" if self._split_characters else "words"}))))
        #// Run the diff and get the output.
        return php_str_replace(nl, "\n", renderer.render(diff)) + "\n"
    # end def _changed
    def _splitonwords(self, string=None, newlineEscape="\n"):
        
        #// Ignore \0; otherwise the while loop will never finish.
        string = php_str_replace(" ", "", string)
        words = Array()
        length = php_strlen(string)
        pos = 0
        while True:
            
            if not (pos < length):
                break
            # end if
            #// Eat a word with any preceding whitespace.
            spaces = strspn(php_substr(string, pos), " \n")
            nextpos = strcspn(php_substr(string, pos + spaces), " \n")
            words[-1] = php_str_replace("\n", newlineEscape, php_substr(string, pos, spaces + nextpos))
            pos += spaces + nextpos
        # end while
        return words
    # end def _splitonwords
    def _encode(self, string=None):
        
        string = htmlspecialchars(string)
    # end def _encode
# end class Text_Diff_Renderer_inline
