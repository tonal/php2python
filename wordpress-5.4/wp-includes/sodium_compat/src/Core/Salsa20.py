#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
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
    def core_salsa20(self, in_=None, k_=None, c_=None):
        if c_ is None:
            c_ = None
        # end if
        
        if self.strlen(k_) < 32:
            raise php_new_class("RangeException", lambda : RangeException("Key must be 32 bytes long"))
        # end if
        if c_ == None:
            j0_ = x0_
            j5_ = x5_
            j10_ = x10_
            j15_ = x15_
        else:
            j0_ = x0_
            j5_ = x5_
            j10_ = x10_
            j15_ = x15_
        # end if
        j1_ = x1_ = self.load_4(self.substr(k_, 0, 4))
        j2_ = x2_ = self.load_4(self.substr(k_, 4, 4))
        j3_ = x3_ = self.load_4(self.substr(k_, 8, 4))
        j4_ = x4_ = self.load_4(self.substr(k_, 12, 4))
        j6_ = x6_ = self.load_4(self.substr(in_, 0, 4))
        j7_ = x7_ = self.load_4(self.substr(in_, 4, 4))
        j8_ = x8_ = self.load_4(self.substr(in_, 8, 4))
        j9_ = x9_ = self.load_4(self.substr(in_, 12, 4))
        j11_ = x11_ = self.load_4(self.substr(k_, 16, 4))
        j12_ = x12_ = self.load_4(self.substr(k_, 20, 4))
        j13_ = x13_ = self.load_4(self.substr(k_, 24, 4))
        j14_ = x14_ = self.load_4(self.substr(k_, 28, 4))
        i_ = self.ROUNDS
        while i_ > 0:
            
            x4_ ^= self.rotate(x0_ + x12_, 7)
            x8_ ^= self.rotate(x4_ + x0_, 9)
            x12_ ^= self.rotate(x8_ + x4_, 13)
            x0_ ^= self.rotate(x12_ + x8_, 18)
            x9_ ^= self.rotate(x5_ + x1_, 7)
            x13_ ^= self.rotate(x9_ + x5_, 9)
            x1_ ^= self.rotate(x13_ + x9_, 13)
            x5_ ^= self.rotate(x1_ + x13_, 18)
            x14_ ^= self.rotate(x10_ + x6_, 7)
            x2_ ^= self.rotate(x14_ + x10_, 9)
            x6_ ^= self.rotate(x2_ + x14_, 13)
            x10_ ^= self.rotate(x6_ + x2_, 18)
            x3_ ^= self.rotate(x15_ + x11_, 7)
            x7_ ^= self.rotate(x3_ + x15_, 9)
            x11_ ^= self.rotate(x7_ + x3_, 13)
            x15_ ^= self.rotate(x11_ + x7_, 18)
            x1_ ^= self.rotate(x0_ + x3_, 7)
            x2_ ^= self.rotate(x1_ + x0_, 9)
            x3_ ^= self.rotate(x2_ + x1_, 13)
            x0_ ^= self.rotate(x3_ + x2_, 18)
            x6_ ^= self.rotate(x5_ + x4_, 7)
            x7_ ^= self.rotate(x6_ + x5_, 9)
            x4_ ^= self.rotate(x7_ + x6_, 13)
            x5_ ^= self.rotate(x4_ + x7_, 18)
            x11_ ^= self.rotate(x10_ + x9_, 7)
            x8_ ^= self.rotate(x11_ + x10_, 9)
            x9_ ^= self.rotate(x8_ + x11_, 13)
            x10_ ^= self.rotate(x9_ + x8_, 18)
            x12_ ^= self.rotate(x15_ + x14_, 7)
            x13_ ^= self.rotate(x12_ + x15_, 9)
            x14_ ^= self.rotate(x13_ + x12_, 13)
            x15_ ^= self.rotate(x14_ + x13_, 18)
            i_ -= 2
        # end while
        x0_ += j0_
        x1_ += j1_
        x2_ += j2_
        x3_ += j3_
        x4_ += j4_
        x5_ += j5_
        x6_ += j6_
        x7_ += j7_
        x8_ += j8_
        x9_ += j9_
        x10_ += j10_
        x11_ += j11_
        x12_ += j12_
        x13_ += j13_
        x14_ += j14_
        x15_ += j15_
        return self.store32_le(x0_) + self.store32_le(x1_) + self.store32_le(x2_) + self.store32_le(x3_) + self.store32_le(x4_) + self.store32_le(x5_) + self.store32_le(x6_) + self.store32_le(x7_) + self.store32_le(x8_) + self.store32_le(x9_) + self.store32_le(x10_) + self.store32_le(x11_) + self.store32_le(x12_) + self.store32_le(x13_) + self.store32_le(x14_) + self.store32_le(x15_)
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
    def salsa20(self, len_=None, nonce_=None, key_=None):
        
        
        if self.strlen(key_) != 32:
            raise php_new_class("RangeException", lambda : RangeException("Key must be 32 bytes long"))
        # end if
        kcopy_ = "" + key_
        in_ = self.substr(nonce_, 0, 8) + php_str_repeat(" ", 8)
        c_ = ""
        while True:
            
            if not (len_ >= 64):
                break
            # end if
            c_ += self.core_salsa20(in_, kcopy_, None)
            u_ = 1
            #// Internal counter.
            i_ = 8
            while i_ < 16:
                
                u_ += self.chrtoint(in_[i_])
                in_[i_] = self.inttochr(u_ & 255)
                u_ >>= 8
                i_ += 1
            # end while
            len_ -= 64
        # end while
        if len_ > 0:
            c_ += self.substr(self.core_salsa20(in_, kcopy_, None), 0, len_)
        # end if
        try: 
            ParagonIE_Sodium_Compat.memzero(kcopy_)
        except SodiumException as ex_:
            kcopy_ = None
        # end try
        return c_
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
    def salsa20_xor_ic(self, m_=None, n_=None, ic_=None, k_=None):
        
        
        mlen_ = self.strlen(m_)
        if mlen_ < 1:
            return ""
        # end if
        kcopy_ = self.substr(k_, 0, 32)
        in_ = self.substr(n_, 0, 8)
        #// Initialize the counter
        in_ += ParagonIE_Sodium_Core_Util.store64_le(ic_)
        c_ = ""
        while True:
            
            if not (mlen_ >= 64):
                break
            # end if
            block_ = self.core_salsa20(in_, kcopy_, None)
            c_ += self.xorstrings(self.substr(m_, 0, 64), self.substr(block_, 0, 64))
            u_ = 1
            i_ = 8
            while i_ < 16:
                
                u_ += self.chrtoint(in_[i_])
                in_[i_] = self.inttochr(u_ & 255)
                u_ >>= 8
                i_ += 1
            # end while
            mlen_ -= 64
            m_ = self.substr(m_, 64)
        # end while
        if mlen_:
            block_ = self.core_salsa20(in_, kcopy_, None)
            c_ += self.xorstrings(self.substr(m_, 0, mlen_), self.substr(block_, 0, mlen_))
        # end if
        try: 
            ParagonIE_Sodium_Compat.memzero(block_)
            ParagonIE_Sodium_Compat.memzero(kcopy_)
        except SodiumException as ex_:
            block_ = None
            kcopy_ = None
        # end try
        return c_
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
    def salsa20_xor(self, message_=None, nonce_=None, key_=None):
        
        
        return self.xorstrings(message_, self.salsa20(self.strlen(message_), nonce_, key_))
    # end def salsa20_xor
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $u
    #// @param int $c
    #// @return int
    #//
    @classmethod
    def rotate(self, u_=None, c_=None):
        
        
        u_ &= 4294967295
        c_ %= 32
        return php_int(4294967295 & u_ << c_ | u_ >> 32 - c_)
    # end def rotate
# end class ParagonIE_Sodium_Core_Salsa20
