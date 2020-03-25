"""Optional questions for Lab 1"""

# While Loops

def falling(n, k):
    """Compute the falling factorial of n to depth k.

    >>> falling(6, 3)  # 6 * 5 * 4
    120
    >>> falling(4, 3)  # 4 * 3 * 2
    24
    >>> falling(4, 1)  # 4
    4
    >>> falling(4, 0)
    1
    """
    "*** YOUR CODE HERE ***"
    if k < 0:
        return None

    tot = 1
    while k > 0:
        tot *= n
        n -= 1
        k -= 1
    return tot

def double_eights(n):
    """Return true if n has two eights in a row.
    >>> double_eights(8)
    False
    >>> double_eights(88)
    True
    >>> double_eights(2882)
    True
    >>> double_eights(880088)
    True
    >>> double_eights(12345)
    False
    >>> double_eights(80808080)
    False
    """
    "*** YOUR CODE HERE ***"
    if n <= 0:
        return False

    prev = False
    while n > 0:
        rem = n % 10
        n = n // 10
        if prev:
           if rem == 8:
               return True
           else:
               prev = False
        else:
            if rem == 8:
                prev = True
    return False
        
