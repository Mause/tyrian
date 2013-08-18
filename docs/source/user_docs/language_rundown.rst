Language Rundown
================

LISP (LISP Is Syntactically Pure) is what is referred to as a functional
language, in that all data manipulation is done via functions;

.. code-block:: lisp

    (defvar word "word")

    (print word (+ 5 5))

    (defun add_five (num)
        (return (+ num 5))
    )

    (print (add_five 5))

    (let q 5)
    (let q (add_five q))

    (print q)

functions are called via the Polish notation, er, notation.


As this is not intended to be a complete implementation, for ease of
implementation, many features have been left out, such as macros. However,
the truly core features are present;
 * variables
 * a standard library
 * function calling (of course)
 * lisp land function definitions
