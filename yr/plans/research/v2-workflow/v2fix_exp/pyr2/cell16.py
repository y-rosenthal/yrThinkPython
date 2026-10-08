def countdown_by_two(n):
    if n == 0:
        print('Blastoff!')
    else:
        countdown_by_two(n - 2)
