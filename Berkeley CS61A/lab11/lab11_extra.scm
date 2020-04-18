(define-macro (switch expr cases)
              (list 'eval (list 'car (list 'cdr (list 'car (list 'filter (list 'lambda (list 'not_allowed) (list 'equal? (list 'car 'not_allowed) expr)) (list 'quote cases))))))
)

(define (flatmap f x)
  'YOUR-CODE-HERE)

(define (expand lst)
  'YOUR-CODE-HERE)

(define (interpret instr dist)
  'YOUR-CODE-HERE)

(define (apply-many n f x)
  (if (zero? n)
      x
      (apply-many (- n 1) f (f x))))

(define (dragon n d)
  (interpret (apply-many n expand '(f x)) d))
