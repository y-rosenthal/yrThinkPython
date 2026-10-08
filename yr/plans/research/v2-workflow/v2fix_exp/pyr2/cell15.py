# @title Output
def up_down(n):
    if n > 0:
        print('*' * n)
        up_down(n - 1)
        print('*' * n)

up_down(3)
