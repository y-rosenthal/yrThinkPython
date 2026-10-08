# @title Output
def mystery(n, s):
    print('n =', n, 's =', s)
    if n == 0:
        print('result:', s)
    else:
        mystery(n - 1, s + n)

mystery(3, 0)
