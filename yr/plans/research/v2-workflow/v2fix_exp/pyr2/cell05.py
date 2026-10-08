# @title Output
def grade(score):
    if score >= 60:
        print('pass')
    elif score >= 90:
        print('excellent')
    else:
        print('fail')

grade(95)
grade(70)
grade(30)
