"""Diagrams for the course pages in yr/: the variables of a frame and the objects that they refer to,
drawn in the style of the state and stack diagrams of the book (diagram.py, by Allen B. Downey).

This is a module: a page imports it, and it has no command line.

    from yrdiagram import draw_variables
    draw_variables({'x': x, 'y': y, 'z': z})

The setup cell of the page downloads diagram.py (from Downey's repository) and this file (from the
website, which serves it: jb/_config.yml, html_extra_path). The build gives a copy of this file to each
page (HELPERS in jb/execute_notebooks.py), so a page also runs before the first publish.
"""
from diagram import diagram, Binding, Value, Frame, make_list, make_dict

__all__ = ['draw_variables', 'draw_state', 'make_list', 'make_dict', 'Value']


def draw_state(names, objects, width, height, step=0.3, frame='__main__'):
    """Draw a frame of variables, and an arrow from each variable to the object that it refers to.

    names: a list of (NAME, K): the variable NAME refers to objects[K]. The names are drawn from the
        top down, STEP apart, in a box with the name FRAME at its left (as in a stack diagram).
    objects: a list of (THING, X, Y): THING is a list or a dictionary (made with make_list or make_dict)
        or a Value (a string or a number, for example Value("'cat'")), drawn at X, Y.
    width, height: the size of the picture, in inches.

    Two arrows that go to the same object end side by side, as in the aliasing diagram of Chapter 9.
    """
    ax = diagram(width, height)
    boxes = [thing.draw(ax, x, y) for thing, x, y in objects]
    total = {}
    for name, k in names:
        total[k] = total.get(k, 0) + 1
    done = {}
    x0, y0 = 0.95, height - 0.3
    bindings = []
    for i, (name, k) in enumerate(names):
        y = y0 - step * i
        box = boxes[k]
        n = done.get(k, 0)
        done[k] = n + 1
        target_y = (box.ymin + box.ymax) / 2 + 0.09 * ((total[k] - 1) / 2 - n)
        target_x = box.xmin - 0.04
        bindings.append(Binding(Value(name), draw_value=False, dx=target_x - x0, dy=target_y - y))
    Frame(bindings, dy=-step, name=frame, loc='left').draw(ax, x0, y0)


def _height(value):
    """The height that draw_variables gives to an object."""
    if isinstance(value, (list, tuple, dict)):
        return 0.35 + 0.18 * max(len(value), 1)
    return 0.3


def _thing(value):
    """The drawing of an object: a box with an index or a key for each item, or the value itself."""
    if isinstance(value, list):
        return make_list(value, dy=-0.18, offsetx=0.1)
    if isinstance(value, tuple):
        return make_list(value, name='tuple', dy=-0.18, offsetx=0.1)
    if isinstance(value, dict):
        return make_dict(value, dy=-0.18, offsetx=0.1)
    return Value(repr(value))


def draw_variables(variables, frame='__main__'):
    """Draw the variables of a dictionary NAME -> object, and the objects that they refer to.

    Variables that refer to the same object (the `is` operator is True) get arrows to one drawing of the
    object. Each other object gets its own drawing, below the ones before it. A list, a tuple and a
    dictionary are drawn as boxes, as in the book; another value (a string, a number) as its repr.
    """
    objects, names = [], []
    for name, value in variables.items():
        k = next((i for i, obj in enumerate(objects) if obj is value), None)
        if k is None:
            objects.append(value)
            k = len(objects) - 1
        names.append((name, k))
    gap = 0.2
    height = sum(_height(obj) for obj in objects) + gap * (len(objects) - 1) + 0.3
    height = max(height, 0.3 * len(names) + 0.4)
    width = 3.3 if any(isinstance(obj, dict) for obj in objects) else 2.8
    placed, top = [], height - 0.1
    for obj in objects:
        boxed = isinstance(obj, (list, tuple, dict))
        y = top - (0.3 if boxed else _height(obj) / 2)
        placed.append((_thing(obj), 1.9, y))
        top -= _height(obj) + gap
    step = 0.3 if len(names) < 2 else min(0.55, max(0.3, (height - 0.6) / (len(names) - 1)))
    draw_state(names, placed, width, height, step=step, frame=frame)
