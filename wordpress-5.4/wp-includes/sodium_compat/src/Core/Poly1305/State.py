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
if php_class_exists("ParagonIE_Sodium_Core_Poly1305_State", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_Poly1305_State
#//
class ParagonIE_Sodium_Core_Poly1305_State(ParagonIE_Sodium_Core_Util):
    buffer = Array()
    final = False
    h = Array()
    leftover = 0
    r = Array()
    pad = Array()
    #// 
    #// ParagonIE_Sodium_Core_Poly1305_State constructor.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $key
    #// @throws InvalidArgumentException
    #// @throws TypeError
    #//
    def __init__(self, key=""):
        
        if self.strlen(key) < 32:
            raise php_new_class("InvalidArgumentException", lambda : InvalidArgumentException("Poly1305 requires a 32-byte key"))
        # end if
        #// r &= 0xffffffc0ffffffc0ffffffc0fffffff
        self.r = Array(int(self.load_4(self.substr(key, 0, 4)) & 67108863), int(self.load_4(self.substr(key, 3, 4)) >> 2 & 67108611), int(self.load_4(self.substr(key, 6, 4)) >> 4 & 67092735), int(self.load_4(self.substr(key, 9, 4)) >> 6 & 66076671), int(self.load_4(self.substr(key, 12, 4)) >> 8 & 1048575))
        #// h = 0
        self.h = Array(0, 0, 0, 0, 0)
        #// save pad for later
        self.pad = Array(self.load_4(self.substr(key, 16, 4)), self.load_4(self.substr(key, 20, 4)), self.load_4(self.substr(key, 24, 4)), self.load_4(self.substr(key, 28, 4)))
        self.leftover = 0
        self.final = False
    # end def __init__
    #// 
    #// Zero internal buffer upon destruction
    #//
    def __del__(self):
        
        self.r[0] ^= self.r[0]
        self.r[1] ^= self.r[1]
        self.r[2] ^= self.r[2]
        self.r[3] ^= self.r[3]
        self.r[4] ^= self.r[4]
        self.h[0] ^= self.h[0]
        self.h[1] ^= self.h[1]
        self.h[2] ^= self.h[2]
        self.h[3] ^= self.h[3]
        self.h[4] ^= self.h[4]
        self.pad[0] ^= self.pad[0]
        self.pad[1] ^= self.pad[1]
        self.pad[2] ^= self.pad[2]
        self.pad[3] ^= self.pad[3]
        self.leftover = 0
        self.final = True
    # end def __del__
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @return self
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def update(self, message=""):
        
        bytes = self.strlen(message)
        if bytes < 1:
            return self
        # end if
        #// handle leftover
        if self.leftover:
            want = ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - self.leftover
            if want > bytes:
                want = bytes
            # end if
            i = 0
            while i < want:
                
                mi = self.chrtoint(message[i])
                self.buffer[self.leftover + i] = mi
                i += 1
            # end while
            #// We snip off the leftmost bytes.
            message = self.substr(message, want)
            bytes = self.strlen(message)
            self.leftover += want
            if self.leftover < ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                #// We still don't have enough to run $this->blocks()
                return self
            # end if
            self.blocks(self.intarraytostring(self.buffer), ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
            self.leftover = 0
        # end if
        #// process full blocks
        if bytes >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
            #// @var int $want
            want = bytes & (1 << (ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - 1).bit_length()) - 1 - ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - 1
            if want >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                block = self.substr(message, 0, want)
                if self.strlen(block) >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                    self.blocks(block, want)
                    message = self.substr(message, want)
                    bytes = self.strlen(message)
                # end if
            # end if
        # end if
        #// store leftover
        if bytes:
            i = 0
            while i < bytes:
                
                mi = self.chrtoint(message[i])
                self.buffer[self.leftover + i] = mi
                i += 1
            # end while
            self.leftover = int(self.leftover) + bytes
        # end if
        return self
    # end def update
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param int $bytes
    #// @return self
    #// @throws TypeError
    #//
    def blocks(self, message=None, bytes=None):
        
        if self.strlen(message) < 16:
            message = php_str_pad(message, 16, " ", STR_PAD_RIGHT)
        # end if
        #// @var int $hibit
        hibit = 0 if self.final else 1 << 24
        #// 1 << 128
        r0 = int(self.r[0])
        r1 = int(self.r[1])
        r2 = int(self.r[2])
        r3 = int(self.r[3])
        r4 = int(self.r[4])
        s1 = self.mul(r1, 5, 3)
        s2 = self.mul(r2, 5, 3)
        s3 = self.mul(r3, 5, 3)
        s4 = self.mul(r4, 5, 3)
        h0 = self.h[0]
        h1 = self.h[1]
        h2 = self.h[2]
        h3 = self.h[3]
        h4 = self.h[4]
        while True:
            
            if not (bytes >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE):
                break
            # end if
            #// h += m[i]
            h0 += self.load_4(self.substr(message, 0, 4)) & 67108863
            h1 += self.load_4(self.substr(message, 3, 4)) >> 2 & 67108863
            h2 += self.load_4(self.substr(message, 6, 4)) >> 4 & 67108863
            h3 += self.load_4(self.substr(message, 9, 4)) >> 6 & 67108863
            h4 += self.load_4(self.substr(message, 12, 4)) >> 8 | hibit
            #// h *= r
            d0 = self.mul(h0, r0, 25) + self.mul(s4, h1, 26) + self.mul(s3, h2, 26) + self.mul(s2, h3, 26) + self.mul(s1, h4, 26)
            d1 = self.mul(h0, r1, 25) + self.mul(h1, r0, 25) + self.mul(s4, h2, 26) + self.mul(s3, h3, 26) + self.mul(s2, h4, 26)
            d2 = self.mul(h0, r2, 25) + self.mul(h1, r1, 25) + self.mul(h2, r0, 25) + self.mul(s4, h3, 26) + self.mul(s3, h4, 26)
            d3 = self.mul(h0, r3, 25) + self.mul(h1, r2, 25) + self.mul(h2, r1, 25) + self.mul(h3, r0, 25) + self.mul(s4, h4, 26)
            d4 = self.mul(h0, r4, 25) + self.mul(h1, r3, 25) + self.mul(h2, r2, 25) + self.mul(h3, r1, 25) + self.mul(h4, r0, 25)
            #// (partial) h %= p
            #// @var int $c
            c = d0 >> 26
            #// @var int $h0
            h0 = d0 & 67108863
            d1 += c
            #// @var int $c
            c = d1 >> 26
            #// @var int $h1
            h1 = d1 & 67108863
            d2 += c
            #// @var int $c
            c = d2 >> 26
            #// @var int $h2
            h2 = d2 & 67108863
            d3 += c
            #// @var int $c
            c = d3 >> 26
            #// @var int $h3
            h3 = d3 & 67108863
            d4 += c
            #// @var int $c
            c = d4 >> 26
            #// @var int $h4
            h4 = d4 & 67108863
            h0 += int(self.mul(c, 5, 3))
            #// @var int $c
            c = h0 >> 26
            #// @var int $h0
            h0 &= 67108863
            h1 += c
            #// Chop off the left 32 bytes.
            message = self.substr(message, ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
            bytes -= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE
        # end while
        self.h = Array(int(h0 & 4294967295), int(h1 & 4294967295), int(h2 & 4294967295), int(h3 & 4294967295), int(h4 & 4294967295))
        return self
    # end def blocks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @return string
    #// @throws TypeError
    #//
    def finish(self):
        
        #// process the remaining block
        if self.leftover:
            i = self.leftover
            self.buffer[i] = 1
            i += 1
            while i < ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                
                self.buffer[i] = 0
                i += 1
            # end while
            self.final = True
            self.blocks(self.substr(self.intarraytostring(self.buffer), 0, ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE), ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
        # end if
        h0 = int(self.h[0])
        h1 = int(self.h[1])
        h2 = int(self.h[2])
        h3 = int(self.h[3])
        h4 = int(self.h[4])
        #// @var int $c
        c = h1 >> 26
        #// @var int $h1
        h1 &= 67108863
        #// @var int $h2
        h2 += c
        #// @var int $c
        c = h2 >> 26
        #// @var int $h2
        h2 &= 67108863
        h3 += c
        #// @var int $c
        c = h3 >> 26
        h3 &= 67108863
        h4 += c
        #// @var int $c
        c = h4 >> 26
        h4 &= 67108863
        #// @var int $h0
        h0 += self.mul(c, 5, 3)
        #// @var int $c
        c = h0 >> 26
        #// @var int $h0
        h0 &= 67108863
        #// @var int $h1
        h1 += c
        #// compute h + -p
        #// @var int $g0
        g0 = h0 + 5
        #// @var int $c
        c = g0 >> 26
        #// @var int $g0
        g0 &= 67108863
        #// @var int $g1
        g1 = h1 + c
        #// @var int $c
        c = g1 >> 26
        g1 &= 67108863
        #// @var int $g2
        g2 = h2 + c
        #// @var int $c
        c = g2 >> 26
        #// @var int $g2
        g2 &= 67108863
        #// @var int $g3
        g3 = h3 + c
        #// @var int $c
        c = g3 >> 26
        #// @var int $g3
        g3 &= 67108863
        #// @var int $g4
        g4 = h4 + c - 1 << 26 & 4294967295
        #// select h if h < p, or h + -p if h >= p
        #// @var int $mask
        mask = g4 >> 31 - 1
        g0 &= mask
        g1 &= mask
        g2 &= mask
        g3 &= mask
        g4 &= mask
        #// @var int $mask
        mask = (1 << (mask).bit_length()) - 1 - mask & 4294967295
        #// @var int $h0
        h0 = h0 & mask | g0
        #// @var int $h1
        h1 = h1 & mask | g1
        #// @var int $h2
        h2 = h2 & mask | g2
        #// @var int $h3
        h3 = h3 & mask | g3
        #// @var int $h4
        h4 = h4 & mask | g4
        #// h = h % (2^128)
        #// @var int $h0
        h0 = h0 | h1 << 26 & 4294967295
        #// @var int $h1
        h1 = h1 >> 6 | h2 << 20 & 4294967295
        #// @var int $h2
        h2 = h2 >> 12 | h3 << 14 & 4294967295
        #// @var int $h3
        h3 = h3 >> 18 | h4 << 8 & 4294967295
        #// mac = (h + pad) % (2^128)
        f = int(h0 + self.pad[0])
        h0 = int(f)
        f = int(h1 + self.pad[1] + f >> 32)
        h1 = int(f)
        f = int(h2 + self.pad[2] + f >> 32)
        h2 = int(f)
        f = int(h3 + self.pad[3] + f >> 32)
        h3 = int(f)
        return self.store32_le(h0 & 4294967295) + self.store32_le(h1 & 4294967295) + self.store32_le(h2 & 4294967295) + self.store32_le(h3 & 4294967295)
    # end def finish
    i += 1
# end class ParagonIE_Sodium_Core_Poly1305_State
