(defparameter "five" 5)
(print "five," 5)

(print "result:" (+ five 5))

(defun ppprint (arg)
    (print five)
    (let non_exis "world")
    (print "non_exis" non_exis)
    (print arg)
)




(defun test ()
    (print (list (range 0 10)))
)

(test)

(ppprint "world")
