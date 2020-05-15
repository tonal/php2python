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
if php_class_exists("ParagonIE_Sodium_Core32_ChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_ChaCha20
#//
class ParagonIE_Sodium_Core32_ChaCha20(ParagonIE_Sodium_Core32_Util):
    #// 
    #// The ChaCha20 quarter round function. Works on four 32-bit integers.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core32_Int32 $a
    #// @param ParagonIE_Sodium_Core32_Int32 $b
    #// @param ParagonIE_Sodium_Core32_Int32 $c
    #// @param ParagonIE_Sodium_Core32_Int32 $d
    #// @return array<int, ParagonIE_Sodium_Core32_Int32>
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def quarterround(self, a=None, b=None, c=None, d=None):
        
        #// @var ParagonIE_Sodium_Core32_Int32 $a
        #// @var ParagonIE_Sodium_Core32_Int32 $b
        #// @var ParagonIE_Sodium_Core32_Int32 $c
        #// @var ParagonIE_Sodium_Core32_Int32 $d
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a),16);
        a = a.addint32(b)
        d = d.xorint32(a).rotateleft(16)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c),12);
        c = c.addint32(d)
        b = b.xorint32(c).rotateleft(12)
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a), 8);
        a = a.addint32(b)
        d = d.xorint32(a).rotateleft(8)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c), 7);
        c = c.addint32(d)
        b = b.xorint32(c).rotateleft(7)
        return Array(a, b, c, d)
    # end def quarterround
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core32_ChaCha20_Ctx $ctx
    #// @param string $message
    #// 
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def encryptbytes(self, ctx=None, message=""):
        
        bytes = self.strlen(message)
        #// @var ParagonIE_Sodium_Core32_Int32 $x0
        #// @var ParagonIE_Sodium_Core32_Int32 $x1
        #// @var ParagonIE_Sodium_Core32_Int32 $x2
        #// @var ParagonIE_Sodium_Core32_Int32 $x3
        #// @var ParagonIE_Sodium_Core32_Int32 $x4
        #// @var ParagonIE_Sodium_Core32_Int32 $x5
        #// @var ParagonIE_Sodium_Core32_Int32 $x6
        #// @var ParagonIE_Sodium_Core32_Int32 $x7
        #// @var ParagonIE_Sodium_Core32_Int32 $x8
        #// @var ParagonIE_Sodium_Core32_Int32 $x9
        #// @var ParagonIE_Sodium_Core32_Int32 $x10
        #// @var ParagonIE_Sodium_Core32_Int32 $x11
        #// @var ParagonIE_Sodium_Core32_Int32 $x12
        #// @var ParagonIE_Sodium_Core32_Int32 $x13
        #// @var ParagonIE_Sodium_Core32_Int32 $x14
        #// @var ParagonIE_Sodium_Core32_Int32 $x15
        #// 
        #// j0 = ctx->input[0];
        #// j1 = ctx->input[1];
        #// j2 = ctx->input[2];
        #// j3 = ctx->input[3];
        #// j4 = ctx->input[4];
        #// j5 = ctx->input[5];
        #// j6 = ctx->input[6];
        #// j7 = ctx->input[7];
        #// j8 = ctx->input[8];
        #// j9 = ctx->input[9];
        #// j10 = ctx->input[10];
        #// j11 = ctx->input[11];
        #// j12 = ctx->input[12];
        #// j13 = ctx->input[13];
        #// j14 = ctx->input[14];
        #// j15 = ctx->input[15];
        #// 
        #// @var ParagonIE_Sodium_Core32_Int32 $j0
        j0 = ctx[0]
        #// @var ParagonIE_Sodium_Core32_Int32 $j1
        j1 = ctx[1]
        #// @var ParagonIE_Sodium_Core32_Int32 $j2
        j2 = ctx[2]
        #// @var ParagonIE_Sodium_Core32_Int32 $j3
        j3 = ctx[3]
        #// @var ParagonIE_Sodium_Core32_Int32 $j4
        j4 = ctx[4]
        #// @var ParagonIE_Sodium_Core32_Int32 $j5
        j5 = ctx[5]
        #// @var ParagonIE_Sodium_Core32_Int32 $j6
        j6 = ctx[6]
        #// @var ParagonIE_Sodium_Core32_Int32 $j7
        j7 = ctx[7]
        #// @var ParagonIE_Sodium_Core32_Int32 $j8
        j8 = ctx[8]
        #// @var ParagonIE_Sodium_Core32_Int32 $j9
        j9 = ctx[9]
        #// @var ParagonIE_Sodium_Core32_Int32 $j10
        j10 = ctx[10]
        #// @var ParagonIE_Sodium_Core32_Int32 $j11
        j11 = ctx[11]
        #// @var ParagonIE_Sodium_Core32_Int32 $j12
        j12 = ctx[12]
        #// @var ParagonIE_Sodium_Core32_Int32 $j13
        j13 = ctx[13]
        #// @var ParagonIE_Sodium_Core32_Int32 $j14
        j14 = ctx[14]
        #// @var ParagonIE_Sodium_Core32_Int32 $j15
        j15 = ctx[15]
        c = ""
        while True:
            
            if bytes < 64:
                message += php_str_repeat(" ", 64 - bytes)
            # end if
            x0 = copy.deepcopy(j0)
            x1 = copy.deepcopy(j1)
            x2 = copy.deepcopy(j2)
            x3 = copy.deepcopy(j3)
            x4 = copy.deepcopy(j4)
            x5 = copy.deepcopy(j5)
            x6 = copy.deepcopy(j6)
            x7 = copy.deepcopy(j7)
            x8 = copy.deepcopy(j8)
            x9 = copy.deepcopy(j9)
            x10 = copy.deepcopy(j10)
            x11 = copy.deepcopy(j11)
            x12 = copy.deepcopy(j12)
            x13 = copy.deepcopy(j13)
            x14 = copy.deepcopy(j14)
            x15 = copy.deepcopy(j15)
            #// # for (i = 20; i > 0; i -= 2) {
            i = 20
            while i > 0:
                
                #// # QUARTERROUND( x0,  x4,  x8,  x12)
                x0, x4, x8, x12 = self.quarterround(x0, x4, x8, x12)
                #// # QUARTERROUND( x1,  x5,  x9,  x13)
                x1, x5, x9, x13 = self.quarterround(x1, x5, x9, x13)
                #// # QUARTERROUND( x2,  x6,  x10,  x14)
                x2, x6, x10, x14 = self.quarterround(x2, x6, x10, x14)
                #// # QUARTERROUND( x3,  x7,  x11,  x15)
                x3, x7, x11, x15 = self.quarterround(x3, x7, x11, x15)
                #// # QUARTERROUND( x0,  x5,  x10,  x15)
                x0, x5, x10, x15 = self.quarterround(x0, x5, x10, x15)
                #// # QUARTERROUND( x1,  x6,  x11,  x12)
                x1, x6, x11, x12 = self.quarterround(x1, x6, x11, x12)
                #// # QUARTERROUND( x2,  x7,  x8,  x13)
                x2, x7, x8, x13 = self.quarterround(x2, x7, x8, x13)
                #// # QUARTERROUND( x3,  x4,  x9,  x14)
                x3, x4, x9, x14 = self.quarterround(x3, x4, x9, x14)
                i -= 2
            # end while
            #// 
            #// x0 = PLUS(x0, j0);
            #// x1 = PLUS(x1, j1);
            #// x2 = PLUS(x2, j2);
            #// x3 = PLUS(x3, j3);
            #// x4 = PLUS(x4, j4);
            #// x5 = PLUS(x5, j5);
            #// x6 = PLUS(x6, j6);
            #// x7 = PLUS(x7, j7);
            #// x8 = PLUS(x8, j8);
            #// x9 = PLUS(x9, j9);
            #// x10 = PLUS(x10, j10);
            #// x11 = PLUS(x11, j11);
            #// x12 = PLUS(x12, j12);
            #// x13 = PLUS(x13, j13);
            #// x14 = PLUS(x14, j14);
            #// x15 = PLUS(x15, j15);
            #//
            x0 = x0.addint32(j0)
            x1 = x1.addint32(j1)
            x2 = x2.addint32(j2)
            x3 = x3.addint32(j3)
            x4 = x4.addint32(j4)
            x5 = x5.addint32(j5)
            x6 = x6.addint32(j6)
            x7 = x7.addint32(j7)
            x8 = x8.addint32(j8)
            x9 = x9.addint32(j9)
            x10 = x10.addint32(j10)
            x11 = x11.addint32(j11)
            x12 = x12.addint32(j12)
            x13 = x13.addint32(j13)
            x14 = x14.addint32(j14)
            x15 = x15.addint32(j15)
            #// 
            #// x0 = XOR(x0, LOAD32_LE(m + 0));
            #// x1 = XOR(x1, LOAD32_LE(m + 4));
            #// x2 = XOR(x2, LOAD32_LE(m + 8));
            #// x3 = XOR(x3, LOAD32_LE(m + 12));
            #// x4 = XOR(x4, LOAD32_LE(m + 16));
            #// x5 = XOR(x5, LOAD32_LE(m + 20));
            #// x6 = XOR(x6, LOAD32_LE(m + 24));
            #// x7 = XOR(x7, LOAD32_LE(m + 28));
            #// x8 = XOR(x8, LOAD32_LE(m + 32));
            #// x9 = XOR(x9, LOAD32_LE(m + 36));
            #// x10 = XOR(x10, LOAD32_LE(m + 40));
            #// x11 = XOR(x11, LOAD32_LE(m + 44));
            #// x12 = XOR(x12, LOAD32_LE(m + 48));
            #// x13 = XOR(x13, LOAD32_LE(m + 52));
            #// x14 = XOR(x14, LOAD32_LE(m + 56));
            #// x15 = XOR(x15, LOAD32_LE(m + 60));
            #//
            x0 = x0.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 0, 4)))
            x1 = x1.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 4, 4)))
            x2 = x2.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 8, 4)))
            x3 = x3.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 12, 4)))
            x4 = x4.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 16, 4)))
            x5 = x5.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 20, 4)))
            x6 = x6.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 24, 4)))
            x7 = x7.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 28, 4)))
            x8 = x8.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 32, 4)))
            x9 = x9.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 36, 4)))
            x10 = x10.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 40, 4)))
            x11 = x11.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 44, 4)))
            x12 = x12.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 48, 4)))
            x13 = x13.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 52, 4)))
            x14 = x14.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 56, 4)))
            x15 = x15.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 60, 4)))
            #// 
            #// j12 = PLUSONE(j12);
            #// if (!j12) {
            #// j13 = PLUSONE(j13);
            #// }
            #// 
            #// @var ParagonIE_Sodium_Core32_Int32 $j12
            j12 = j12.addint(1)
            if j12.limbs[0] == 0 and j12.limbs[1] == 0:
                j13 = j13.addint(1)
            # end if
            #// 
            #// STORE32_LE(c + 0, x0);
            #// STORE32_LE(c + 4, x1);
            #// STORE32_LE(c + 8, x2);
            #// STORE32_LE(c + 12, x3);
            #// STORE32_LE(c + 16, x4);
            #// STORE32_LE(c + 20, x5);
            #// STORE32_LE(c + 24, x6);
            #// STORE32_LE(c + 28, x7);
            #// STORE32_LE(c + 32, x8);
            #// STORE32_LE(c + 36, x9);
            #// STORE32_LE(c + 40, x10);
            #// STORE32_LE(c + 44, x11);
            #// STORE32_LE(c + 48, x12);
            #// STORE32_LE(c + 52, x13);
            #// STORE32_LE(c + 56, x14);
            #// STORE32_LE(c + 60, x15);
            #//
            block = x0.toreversestring() + x1.toreversestring() + x2.toreversestring() + x3.toreversestring() + x4.toreversestring() + x5.toreversestring() + x6.toreversestring() + x7.toreversestring() + x8.toreversestring() + x9.toreversestring() + x10.toreversestring() + x11.toreversestring() + x12.toreversestring() + x13.toreversestring() + x14.toreversestring() + x15.toreversestring()
            #// Partial block
            if bytes < 64:
                c += self.substr(block, 0, bytes)
                break
            # end if
            #// Full block
            c += block
            bytes -= 64
            if bytes <= 0:
                break
            # end if
            message = self.substr(message, 64)
            
        # end while
        #// end for(;;) loop
        ctx[12] = j12
        ctx[13] = j13
        return c
    # end def encryptbytes
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
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(key, nonce)), php_str_repeat(" ", len))
    # end def stream
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
    def ietfstream(self, len=None, nonce="", key=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core32_ChaCha20_IetfCtx(key, nonce)), php_str_repeat(" ", len))
    # end def ietfstream
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
    def ietfstreamxoric(self, message=None, nonce="", key="", ic=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core32_ChaCha20_IetfCtx(key, nonce, ic)), message)
    # end def ietfstreamxoric
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
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(key, nonce, ic)), message)
    # end def streamxoric
# end class ParagonIE_Sodium_Core32_ChaCha20
