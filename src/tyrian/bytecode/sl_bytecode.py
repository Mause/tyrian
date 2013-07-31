# import dis
import imp
import time
import types

import struct
import marshal


class BytecodeAuthor(object):
    def __init__(self):
        self.object = None
        self.magic = imp.get_magic()

    def setup_object(self):
        self.object = type('Object', (type,), {})


def load(filename):
    with open(filename, 'rb') as fh:
        magic = fh.read(4)
        moddate = fh.read(4)

        modtime = struct.unpack('L', moddate)[0]
        modtime = time.localtime(modtime)
        modtime = time.asctime(modtime)

        data = marshal.loads(fh.read())

    return magic, moddate, modtime, data


def main():
    args = [
        ('co_argcount', 0),             # number of arguments (not including * or ** args)
        ('co_cellvars', 0),
        ('co_code', b''),               # string of raw compiled bytecode
        ('co_consts', ('const',)),      # tuple of constants used in the bytecode
        ('co_filename', ''),            # name of file in which this code object was created
        ('co_firstlineno', 0),          # number of first line in Python source code
        ('co_flags', 0),                # bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
        ('co_lnotab', b''),             # encoded mapping of line numbers to bytecode indices
        ('co_name', ''),                # name with which this code object was defined
        ('co_names', ('name',)),        # tuple of names of local variables
        ('co_nlocals', 1),              # number of local variables
        ('co_stacksize', 1),            # virtual machine stack space required
        ('co_varnames', ('arg',)),      # tuple of names of arguments and local variables
    ]

    print(len(args))

    # codeobj = codeobj_const()
    # with open('test.py') as fh:
    #     codeobj = codeop.compile_command(fh.read(), filename="test.py")

    args = [x[1] for x in args]

    global codeobj
    codeobj = types.CodeType(*args)

    print(codeobj)

    # dis.dis(d)
    # b = BytecodeAuthor()
    # b.setup_object()
    # print(b.object)

if __name__ == '__main__':
    main()
