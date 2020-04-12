;;;;;;;;;;;;;;;
;; Questions ;;
;;;;;;;;;;;;;;;

; Scheme

(define (cddr s)
  (cdr (cdr s)))

(define (cadr s)
  (car (cdr s)))

(define (caddr s)
  'YOUR-CODE-HERE
  (car (cdr (cdr s)))
)

(define (sign x)
  'YOUR-CODE-HERE
  (if (> x 0) 1 (if (= x 0) 0 -1))
)

(define (square x) (* x x))

(define (pow b n)
  'YOUR-CODE-HERE
  (if (= n 0) 
      1 
  (if (even? n) (square (pow b (/ n 2)))
  (* b (pow b (- n 1)))))
)

(define (unique s)
  'YOUR-CODE-HERE
  (if (null? s) 
      ()
  (cons (car s)
        (unique (filter (lambda (x) (not (eq? x (car s)))) (cdr s)))))
)