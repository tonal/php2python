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
if php_class_exists("ParagonIE_Sodium_Core_Salsa20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_Salsa20
#//
class ParagonIE_Sodium_Core_Salsa20(ParagonIE_Sodium_Core_Util):
    ROUNDS = 20
    #// 
    #// Calculate an salsa20 hash of a single block
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $in
    #// @param string $k
    #// @param string|null $c
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def core_salsa20(self, in_=None, k=None, c=None):
        
        if self.strlen(k) < 32:
            raise php_new_class("RangeException", lambda : RangeException("Key must be 32 bytes long"))
        # end if
        if c == None:
            j0 = x0
            j5 = x5
            j10 = x10
            j15 = x15
        else:
            j0 = x0
            j5 = x5
            j10 = x10
            j15 = x15
        # end if
        j1 = x1 = self.load_4(self.substr(k, 0, 4))
        j2 = x2 = self.load_4(self.substr(k, 4, 4))
        j3 = x3 = self.load_4(self.substr(k, 8, 4))
        j4 = x4 = self.load_4(self.substr(k, 12, 4))
        j6 = x6 = self.load_4(self.substr(in_, 0, 4))
        j7 = x7 = self.load_4(self.substr(in_, 4, 4))
        j8 = x8 = self.load_4(self.substr(in_, 8, 4))
        j9 = x9 = self.load_4(self.substr(in_, 12, 4))
        j11 = x11 = self.load_4(self.substr(k, 16, 4))
        j12 = x12 = self.load_4(self.substr(k, 20, 4))
        j13 = x13 = self.load_4(self.substr(k, 24, 4))
        j14 = x14 = self.load_4(self.substr(k, 28, 4))
        i = self.ROUNDS
        while i > 0:
            
            x4 ^= self.rotate(x0 + x12, 7)
            x8 ^= self.rotate(x4 + x0, 9)
            x12 ^= self.rotate(x8 + x4, 13)
            x0 ^= self.rotate(x12 + x8, 18)
            x9 ^= self.rotate(x5 + x1, 7)
            x13 ^= self.rotate(x9 + x5, 9)
            x1 ^= self.rotate(x13 + x9, 13)
            x5 ^= self.rotate(x1 + x13, 18)
            x14 ^= self.rotate(x10 + x6, 7)
            x2 ^= self.rotate(x14 + x10, 9)
            x6 ^= self.rotate(x2 + x14, 13)
            x10 ^= self.rotate(x6 + x2, 18)
            x3 ^= self.rotate(x15 + x11, 7)
            x7 ^= self.rotate(x3 + x15, 9)
            x11 ^= self.rotate(x7 + x3, 13)
            x15 ^= self.rotate(x11 + x7, 18)
            x1 ^= self.rotate(x0 + x3, 7)
            x2 ^= self.rotate(x1 + x0, 9)
            x3 ^= self.rotate(x2 + x1, 13)
            x0 ^= self.rotate(x3 + x2, 18)
            x6 ^= self.rotate(x5 + x4, 7)
            x7 ^= self.rotate(x6 + x5, 9)
            x4 ^= self.rotate(x7 + x6, 13)
            x5 ^= self.rotate(x4 + x7, 18)
            x11 ^= self.rotate(x10 + x9, 7)
            x8 ^= self.rotate(x11 + x10, 9)
            x9 ^= self.rotate(x8 + x11, 13)
            x10 ^= self.rotate(x9 + x8, 18)
            x12 ^= self.rotate(x15 + x14, 7)
            x13 ^= self.rotate(x12 + x15, 9)
            x14 ^= self.rotate(x13 + x12, 13)
            x15 ^= self.rotate(x14 + x13, 18)
            i -= 2
        # end while
        x0 += j0
        x1 += j1
        x2 += j2
        x3 += j3
        x4 += j4
        x5 += j5
        x6 += j6
        x7 += j7
        x8 += j8
        x9 += j9
        x10 += j10
        x11 += j11
        x12 += j12
        x13 += j13
        x14 += j14
        x15 += j15
        return self.store32_le(x0) + self.store32_le(x1) + self.store32_le(x2) + self.store32_le(x3) + self.store32_le(x4) + self.store32_le(x5) + self.store32_le(x6) + self.store32_le(x7) + self.store32_le(x8) + self.store32_le(x9) + self.store32_le(x10) + self.store32_le(x11) + self.store32_le(x12) + self.store32_le(x13) + self.store32_le(x14) + self.store32_le(x15)
    # end def core_salsa20
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
    def salsa20(self, len=None, nonce=None, key=None):
        
        if self.strlen(key) != 32:
            raise php_new_class("RangeException", lambda : RangeException("Key must be 32 bytes long"))
        # end if
        kcopy = "" + key
        in_ = self.substr(nonce, 0, 8) + php_str_repeat(" ", 8)
        c = ""
        while True:
            
            if not (len >= 64):
                break
            # end if
            c += self.core_salsa20(in_, kcopy, None)
            u = 1
            #// Internal counter.
            i = 8
            while i < 16:
                
                u += self.chrtoint(in_[i])
                in_[i] = self.inttochr(u & 255)
                u >>= 8
                i += 1
            # end while
            len -= 64
        # end while
        if len > 0:
            c += self.substr(self.core_salsa20(in_, kcopy, None), 0, len)
        # end if
        try: 
            ParagonIE_Sodium_Compat.memzero(kcopy)
        except SodiumException as ex:
            kcopy = None
        # end try
        return c
    # end def salsa20
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $m
    #// @param string $n
    #// @param int $ic
    #// @param string $k
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def salsa20_xor_ic(self, m=None, n=None, ic=None, k=None):
        
        mlen = self.strlen(m)
        if mlen < 1:
            return ""
        # end if
        kcopy = self.substr(k, 0, 32)
        in_ = self.substr(n, 0, 8)
        #// Initialize the counter
        in_ += ParagonIE_Sodium_Core_Util.store64_le(ic)
        c = ""
        while True:
            
            if not (mlen >= 64):
                break
            # end if
            block = self.core_salsa20(in_, kcopy, None)
            c += self.xorstrings(self.substr(m, 0, 64), self.substr(block, 0, 64))
            u = 1
            i = 8
            while i < 16:
                
                u += self.chrtoint(in_[i])
                in_[i] = self.inttochr(u & 255)
                u >>= 8
                i += 1
            # end while
            mlen -= 64
            m = self.substr(m, 64)
        # end while
        if mlen:
            block = self.core_salsa20(in_, kcopy, None)
            c += self.xorstrings(self.substr(m, 0, mlen), self.substr(block, 0, mlen))
        # end if
        try: 
            ParagonIE_Sodium_Compat.memzero(block)
            ParagonIE_Sodium_Compat.memzero(kcopy)
        except SodiumException as ex:
            block = None
            kcopy = None
        # end try
        return c
    # end def salsa20_xor_ic
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def salsa20_xor(self, message=None, nonce=None, key=None):
        
        return self.xorstrings(message, self.salsa20(self.strlen(message), nonce, key))
    # end def salsa20_xor
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $u
    #// @param int $c
    #// @return int
    #//
    @classmethod
    def rotate(self, u=None, c=None):
        
        u &= 4294967295
        c %= 32
        return int(4294967295 & u << c | u >> 32 - c)
    # end def rotate
# end class ParagonIE_Sodium_Core_Salsa20
