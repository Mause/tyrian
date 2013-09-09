Tyrian

Tyrian is a simplistic LISP to Python Bytecode compiler.

Example;

This LISP code;

```lisp
(print "world")
```

is translated into this python bytecode;

```bytecode
<snip>
LOAD_GLOBAL              6 (print)
LOAD_CONST              13 ('world')
CALL_FUNCTION            1 (1 positional, 0 keyword pair)
POP_TOP
<snip>
```

The Compiler subsection of tyrian makes heavy use of module known as

`peak.util.assembler`, AKA BytecodeAssembler


Quick explanation;
in c, you write this;

```c
int main(int argc, char *argv[]) {
    printf("%s", "String!");
    return 0;
}
```

and your compiler of choice outputs the assembly required for your machine, which is then linked with whatever libraries it requires, before being assembled by the assembler into machine code.

This is what is referred to as a compiled language.


Python is not like this. Python is largely referred to as an interpreted language, though that definition is debatable.

An interpreted language is one that is not run directly on the hardware; rather, it is simply translated into a series of tokens (as in BASIC), or bytecode, as in many others, including Python.

Quick summary of LISP;
LISP is what is referred to as a purely functional language, in that everything is a function call. Variable assignment, imports, et cetera, et cetera.
