(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement.

(define (cons-all first rests)
  (map (lambda (x) (cons first x)) rests)
  )

(define (zip pairs)
  'replace-this-line
  `(,(map (lambda (x) (car x)) pairs) ,(map (lambda (x) (car (cdr x))) pairs)))

;; Problem 17
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 17
  'replace-this-line
  (begin (define (recurse x cur) (if (null? x) x (cons (cons cur (cons (car x) nil)) (recurse (cdr x) (+ cur 1)))))
         (recurse s 0))
  )
  ; END PROBLEM 17

;; Problem 18
;; List all ways to make change for TOTAL with DENOMS

(define (list-change total denoms)
  ; BEGIN PROBLEM 18
  'replace-this-line
  (cond ((null? denoms) '())
        ((= total 0) '(()))
        ((< total (car denoms)) (list-change total (cdr denoms)))
        ((>= total (car denoms)) (append (cons-all (car denoms) (list-change (- total (car denoms)) denoms)) (list-change total (cdr denoms))))
        (else nil))
  )
  ; END PROBLEM 18


;; Problem 19
;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let?    (check-special 'let))

;; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
  (cond ((atom? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((quoted? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((or (lambda? expr)
             (define? expr))
         (let ((form   (car expr))
               (params (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (cons form (cons params (let-to-lambda body)))
           ; END PROBLEM 19
           ))
        ((let? expr)
         (let ((values (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (cons (cons 'lambda (cons (car (zip (let-to-lambda values)))
                                     (let-to-lambda body)))
                 (cadr (zip (let-to-lambda values))))
           ; END PROBLEM 19
           ))
        (else
         ; BEGIN PROBLEM 19
         (map let-to-lambda expr)
         ; END PROBLEM 19
         )))
