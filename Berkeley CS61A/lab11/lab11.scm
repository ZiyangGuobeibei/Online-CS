(define (repeatedly-cube n x)
    (if (zero? n)
        x
        (let
            ((y (repeatedly-cube (- n 1) x)))
            (* y y y))))


(define-macro (def func bindings body)
              (list 'define func (list 'lambda bindings body))
              )

(define-macro (make-lambda expr)
              (list 'lambda '() expr)
              )

(define (replicate x n)
  (if (= n 0) nil
    (cons x (replicate x (- n 1)))))

(define-macro (repeat-n expr n)
              (cons 'begin (replicate expr n)))
