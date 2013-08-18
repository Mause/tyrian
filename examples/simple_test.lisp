(defparameter five 5)
(print "five:" five)

(defun ppprint (arg numb)
    (print arg)
    (print five)
    (print numb)
    (let non_exis "world")
    (let numberz (+ 5 5 numb))
    (print "non_exis" non_exis)
)

(ppprint "bgggg" 20)

(defun function () ())

(callfunc function)
