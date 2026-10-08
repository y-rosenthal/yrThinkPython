# @title Output
def describe(x):
    if 0 < x < 10:
        print(x, 'is a positive single digit')
    else:
        if x <= 0:
            print(x, 'is not positive')
        else:
            print(x, 'is 10 or more')

describe(5)
describe(-3)
describe(10)
