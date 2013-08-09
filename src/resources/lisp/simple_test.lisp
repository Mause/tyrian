(defparameter "five" 5)
(print "five," 5)

(print "result:" (+ five 5))

(defun hello_world ()
    (print "hello")
    (print "world"))

(defun ppprint (arg)
    (print five)
    (print arg)
)


(defun test ()
    (print (list (range 0 10)))
)

(test)

(ppprint "world")

(hello_world)
