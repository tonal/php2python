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
if php_class_exists("ParagonIE_Sodium_Core32_XChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_XChaCha20
#//
class ParagonIE_Sodium_Core32_XChaCha20(ParagonIE_Sodium_Core32_HChaCha20):
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $len
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def stream(self, len=64, nonce="", key=""):
        
        if self.strlen(nonce) != 24:
            raise php_new_class("SodiumException", lambda : SodiumException("Nonce must be 24 bytes long"))
        # end if
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(self.hchacha20(self.substr(nonce, 0, 16), key), self.substr(nonce, 16, 8))), php_str_repeat(" ", len))
    # end def stream
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param string $nonce
    #// @param string $key
    #// @param string $ic
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def streamxoric(self, message=None, nonce="", key="", ic=""):
        
        if self.strlen(nonce) != 24:
            raise php_new_class("SodiumException", lambda : SodiumException("Nonce must be 24 bytes long"))
        # end if
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(self.hchacha20(self.substr(nonce, 0, 16), key), self.substr(nonce, 16, 8), ic)), message)
    # end def streamxoric
# end class ParagonIE_Sodium_Core32_XChaCha20
