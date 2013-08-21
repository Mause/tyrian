(defvar word "word")

(print word (+ 5 5))

(defun add_five (num)
    (return (+ num 5))
)

(print (add_five 5))

(let q 5)
(let q (add_five q))

(print q)
