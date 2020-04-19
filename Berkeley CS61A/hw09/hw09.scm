
; Tail recursion

(define (replicate x n)
  'YOUR-CODE-HERE
  (begin (define (replicate-tail lst num acc) (if (= num 0) acc (replicate-tail lst (- num 1) (cons lst acc))))
         (replicate-tail x n '()))
  )

(define (accumulate combiner start n term)
  (if (= n 0) start
    (combiner (term n) (accumulate combiner start (- n 1) term)))
)

(define (accumulate-tail combiner start n term)
  (begin (define (accumulate-acc combiner n term acc)
           (if (= n 0) acc
           (accumulate-acc combiner (- n 1) term (combiner (term n) acc))))
         (accumulate-acc combiner n term start))
)

; Streams

(define (map-stream f s)
    (if (null? s)
    	nil
    	(cons-stream (f (car s)) (map-stream f (cdr-stream s)))))

(define (naturals n)
  (cons-stream n (naturals (+ n 1))))


(define multiples-of-three
  (map-stream (lambda (x) (* x 3)) (naturals 1))
)

(define (append-one lst ele)
  (if (null? lst) (cons ele nil)
    (cons (car lst) (append-one (cdr lst) ele))))

(define (nondecreastream s)
  (begin (define (nondecreastream-tail s lst prev)
           (cond [(null? s) (cons-stream lst nil)]
                 [(<= prev (car s)) (nondecreastream-tail (cdr-stream s) (append-one lst (car s)) (car s))]
                 [else (cons-stream lst (nondecreastream-tail (cdr-stream s) `(,(car s)) (car s)))]))
         (if (null? s) nil (nondecreastream-tail s nil 0)))
  )

(define finite-test-stream
    (cons-stream 1
        (cons-stream 2
            (cons-stream 3
                (cons-stream 1
                    (cons-stream 2
                        (cons-stream 2
                            (cons-stream 1 nil))))))))

(define infinite-test-stream
    (cons-stream 1
        (cons-stream 2
            (cons-stream 2
                infinite-test-stream))))
