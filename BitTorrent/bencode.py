# Written by Petru Paler, Uoti Urpala, Ross Cohen and John Hoffman
# see LICENSE.txt for license information

from types import IntType, LongType, StringType, ListType, TupleType, DictType
try:
    from types import BooleanType
except ImportError:
    BooleanType = None
try:
    from types import UnicodeType
except ImportError:
    UnicodeType = None
from cStringIO import StringIO


class _bdecode:
    def __init__(self, sloppy = False):
        self.decode_func = {}
        self.decode_func['0'] = self.decode_string
        self.decode_func['1'] = self.decode_string
        self.decode_func['2'] = self.decode_string
        self.decode_func['3'] = self.decode_string
        self.decode_func['4'] = self.decode_string
        self.decode_func['5'] = self.decode_string
        self.decode_func['6'] = self.decode_string
        self.decode_func['7'] = self.decode_string
        self.decode_func['8'] = self.decode_string
        self.decode_func['9'] = self.decode_string
        #self.decode_func['u'] = self.decode_unicode
        self.decode_func['l'] = self.decode_list
        self.decode_func['i'] = self.decode_int
        if sloppy:
            self.decode = self.decode_sloppy
            self.decode_func['d'] = self.decode_dict_sloppy
        else:
            self.decode = self.decode_strict
            self.decode_func['d'] = self.decode_dict_strict
        
    def decode_int(self, x, f):
        f += 1
        newf = x.index('e', f)
        try:
            n = int(x[f:newf])
        except:
            n = long(x[f:newf])
        if x[f] == '-':
            if x[f + 1] == '0':
                raise ValueError
        elif x[f] == '0' and newf != f+1:
            raise ValueError
        return (n, newf+1)
      
    def decode_string(self, x, f):
        colon = x.index(':', f)
        try:
            n = int(x[f:colon])
        except (OverflowError, ValueError):
            n = long(x[f:colon])
        if x[f] == '0' and colon != f+1:
            raise ValueError
        colon += 1
        return (x[colon:colon+n], colon+n)

    def decode_unicode(self, x, f):
        s, f = self.decode_string(x, f+1)
        return (s.decode('UTF-8'),f)

    def decode_list(self, x, f):
        r, f = [], f+1
        while x[f] != 'e':
            v, f = self.decode_func[x[f]](x, f)
            r.append(v)
        return (r, f + 1)

    def decode_dict_strict(self, x, f):
        r, f = {}, f+1
        lastkey = None
        while x[f] != 'e':
            k, f = self.decode_string(x, f)
            if lastkey >= k:
                raise ValueError
            lastkey = k
            r[k], f = self.decode_func[x[f]](x, f)
        return (r, f + 1)

    def decode_dict_sloppy(self, x, f):
        r, f = {}, f+1
        while x[f] != 'e':
            k, f = self.decode_string(x, f)
            r[k], f = self.decode_func[x[f]](x, f)
        return (r, f + 1)
  
    def decode_strict(self, x):
        try:
            r, l = self.decode_func[x[0]](x, 0)
        except (IndexError, KeyError, ValueError):
            raise ValueError, "bad bencoded data"
        if l != len(x):
            raise ValueError, "bad bencoded data"
        return r

    def decode_sloppy(self, x):
        try:
            r, l = self.decode_func[x[0]](x, 0)
        except (IndexError, KeyError, ValueError):
            raise ValueError, "bad bencoded data"
        return r


bdecode_strict = _bdecode(sloppy = False).decode
bdecode_sloppy = _bdecode(sloppy = True).decode
bdecode = bdecode_strict
#def bdecode(d, sloppy = False):
#    if sloppy:
#        return bdecode_sloppy(d)
#    return bdecode_strict(d)
        


def test_bdecode():
    try:
        bdecode('0:0:')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('ie')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('i341foo382e')
        assert 0
    except ValueError:
        pass
    assert bdecode('i4e') == 4L
    assert bdecode('i0e') == 0L
    assert bdecode('i123456789e') == 123456789L
    assert bdecode('i-10e') == -10L
    try:
        bdecode('i-0e')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('i123')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('i6easd')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('35208734823ljdahflajhdf')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('2:abfdjslhfld')
        assert 0
    except ValueError:
        pass
    assert bdecode('0:') == ''
    assert bdecode('3:abc') == 'abc'
    assert bdecode('10:1234567890') == '1234567890'
    try:
        bdecode('02:xy')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('l')
        assert 0
    except ValueError:
        pass
    assert bdecode('le') == []
    try:
        bdecode('leanfdldjfh')
        assert 0
    except ValueError:
        pass
    assert bdecode('l0:0:0:e') == ['', '', '']
    try:
        bdecode('relwjhrlewjh')
        assert 0
    except ValueError:
        pass
    assert bdecode('li1ei2ei3ee') == [1, 2, 3]
    assert bdecode('l3:asd2:xye') == ['asd', 'xy']
    assert bdecode('ll5:Alice3:Bobeli2ei3eee') == [['Alice', 'Bob'], [2, 3]]
    try:
        bdecode('d')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('defoobar')
        assert 0
    except ValueError:
        pass
    assert bdecode('de') == {}
    assert bdecode('d3:agei25e4:eyes4:bluee') == {'age': 25, 'eyes': 'blue'}
    assert bdecode('d8:spam.mp3d6:author5:Alice6:lengthi100000eee') == {'spam.mp3': {'author': 'Alice', 'length': 100000}}
    try:
        bdecode('d3:fooe')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('di1e0:e')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('d1:b0:1:a0:e')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('d1:a0:1:a0:e')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('i03e')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('l01:ae')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('9999:x')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('l0:')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('d0:0:')
        assert 0
    except ValueError:
        pass
    try:
        bdecode('d0:')
        assert 0
    except ValueError:
        pass

bencached_marker = []

class Bencached:
    def __init__(self, s):
        self.marker = bencached_marker
        self.bencoded = s

BencachedType = type(Bencached('')) # insufficient, but good as a filter

def encode_bencached(x,r):
    assert x.marker == bencached_marker
    r.append(x.bencoded)

def encode_int(x,r):
    r.extend(('i',str(x),'e'))

def encode_bool(x,r):
    encode_int(int(x),r)

def encode_string(x,r):    
    r.extend((str(len(x)),':',x))

def encode_unicode(x,r):
    #r.append('u')
    encode_string(x.encode('UTF-8'),r)

def encode_list(x,r):
        r.append('l')
        for e in x:
            encode_func[type(e)](e, r)
        r.append('e')

def encode_dict(x,r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k,v in ilist:
        r.extend((str(len(k)),':',k))
        encode_func[type(v)](v, r)
    r.append('e')

encode_func = {}
encode_func[BencachedType] = encode_bencached
encode_func[IntType] = encode_int
encode_func[LongType] = encode_int
encode_func[StringType] = encode_string
encode_func[ListType] = encode_list
encode_func[TupleType] = encode_list
encode_func[DictType] = encode_dict
if BooleanType:
    encode_func[BooleanType] = encode_bool
if UnicodeType:
    encode_func[UnicodeType] = encode_unicode
    
def bencode(x):
    r = []
    try:
        encode_func[type(x)](x, r)
    except:
        print "*** error *** could not encode type %s (value: %s)" % (type(x), x)
        assert 0
    return ''.join(r)

def test_bencode():
    assert bencode(4) == 'i4e'
    assert bencode(0) == 'i0e'
    assert bencode(-10) == 'i-10e'
    assert bencode(12345678901234567890L) == 'i12345678901234567890e'
    assert bencode('') == '0:'
    assert bencode('abc') == '3:abc'
    assert bencode('1234567890') == '10:1234567890'
    assert bencode([]) == 'le'
    assert bencode([1, 2, 3]) == 'li1ei2ei3ee'
    assert bencode([['Alice', 'Bob'], [2, 3]]) == 'll5:Alice3:Bobeli2ei3eee'
    assert bencode({}) == 'de'
    assert bencode({'age': 25, 'eyes': 'blue'}) == 'd3:agei25e4:eyes4:bluee'
    assert bencode({'spam.mp3': {'author': 'Alice', 'length': 100000}}) == 'd8:spam.mp3d6:author5:Alice6:lengthi100000eee'
    try:
        bencode({1: 'foo'})
        assert 0
    except AssertionError:
        pass

  
try:
    import psyco
    psyco.bind(bdecode)
    psyco.bind(bencode)
except ImportError:
    pass
