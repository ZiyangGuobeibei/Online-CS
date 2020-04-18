; Macros

(define-macro (for sym val arg)
              (list 'map (list 'lambda (list sym) val) arg)
              )

(define-macro (list-of map-expr for var in lst if filter-expr)
              (list 'for var map-expr (list 'filter (list 'lambda (list var) filter-expr) lst))
)

(define-macro (list-of map-expr for var in lst)
              (list 'for var map-expr lst)
              )


