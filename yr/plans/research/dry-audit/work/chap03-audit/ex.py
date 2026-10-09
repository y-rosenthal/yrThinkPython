import io,contextlib
sols = {
'underline': "def underline(text):\n    print(text)\n    print('-' * len(text))\n",
'print_right': "def print_right(text, width):\n    print(' ' * (width - len(text)) + text)\n",
'verse': "def verse(animal, sound):\n    print('Old MacDonald had a farm')\n    print('And on that farm he had a', animal)\n    print('With a', sound, sound, 'here')\n",
'pyramid': "def pyramid(char, height):\n    for i in range(height):\n        print(' ' * (height - 1 - i) + char * (2 * i + 1))\n",
'grid': "def print_border(n):\n    print('+---' * n + '+')\ndef print_grid(n):\n    for i in range(n):\n        print_border(n)\n        print('|   ' * n + '|')\n    print_border(n)\n",
'aas': "def add_and_show(a, b):\n    total = a + b\n    print(a, '+', b, '=', total)\n",
'outer': "def inner(value):\n    print(value + 1)\n\ndef outer(value):\n    print('outer got', value)\n    inner(value)\n",
}
calls=[('underline',"underline('Hello')"),('underline',"underline('Python 3')"),
('print_right',"print_right('Monty', 10)\nprint_right('Python', 10)\nprint_right('Flying Circus', 20)"),
('print_right',"print_right('abc', 3)\nprint_right('abc', 4)"),
('verse',"verse('cow', 'moo')"),('verse',"verse('pig', 'oink')"),
('pyramid',"pyramid('*', 3)"),('pyramid',"pyramid('#', 5)"),
('grid',"print_border(3)"),('grid',"print_grid(2)"),('grid',"print_grid(3)"),
('aas',"add_and_show(2, 3)"),('aas',"add_and_show(10, -4)"),('outer',"outer(5)"),('outer',"outer(2.5)")]
for k,c in calls:
    ns={}; exec(sols[k],ns); o=io.StringIO()
    with contextlib.redirect_stdout(o): exec(c,ns)
    print('>>>',c.replace('\n',' ; ')); print(o.getvalue(),end='')
