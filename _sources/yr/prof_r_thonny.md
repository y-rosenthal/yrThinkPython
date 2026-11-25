# Another Note From Prof. Rosenthal: Using Thonny

The pages of this book are Jupyter notebooks: you run them on Colab, one cell at a time. In my class, you
also write and run whole Python programs on your own computer. For that we use **Thonny**, a free program for
writing and running Python. Thonny is made for beginners. It has a **debugger** that runs a program one step
at a time and shows the value of each variable, so you can see what your code does.

This page tells you how to install and start Thonny, what the two parts of its window do, and how to change
the code of the book so that it works in Thonny. The pages "3c. Additions: More About for Loops" and
"11c. Additions: The Thonny Debugger" show how to use the debugger.

## Install Thonny

1. Go to [thonny.org](https://thonny.org).
2. At the top of the page, point to the link for your computer, and click the installer:
   - **Windows:** the installer is a `.exe` file. Run it, and accept the default choices.
   - **Mac:** the installer is a `.pkg` file. Open it, and follow the steps. Thonny goes into the
     **Applications** folder.
   - **Linux:** the page gives the commands. For example, `pip install thonny`. Many Linux systems also have a
     package (on Ubuntu: `sudo apt install thonny`), but that version can be older.
3. Thonny comes with its own copy of Python. You do not need to install Python separately.

## Start Thonny

- **Windows:** click **Start**, and type `Thonny`.
- **Mac:** open the **Applications** folder, and double-click **Thonny**.
- **Linux:** find Thonny in the menu of applications, or type `thonny` in a terminal.

The first time that Thonny starts, it asks for a language and for the initial settings. Choose
**Standard**, not Raspberry Pi.

## The two parts of the Thonny window

The Thonny window has two main parts, one above the other.

**The top part is the editor.** Here you write a **program**: a file of Python code. Python does not run the
code while you type it. To run the whole program, click the green **Run** button (a white triangle on a
green circle), or press **F5**. Thonny asks you to save the file first: give it a name that ends with `.py`,
for example `hello.py`. Each file that you open has its own tab in the editor.

**The bottom part is the Shell.** It shows the prompt `>>>`. Type a line of Python after the prompt and
press **Enter**: Python runs the line at once and shows the result. The Shell is good for small tests: to try
an expression, to check what a function returns, or to look at a variable. When a line starts a block (it ends
with a colon, as `for i in range(3):` does), the Shell waits for the lines of the block. Press **Enter** on an
empty line to run the block.

When you run a program from the editor, the Shell shows what the program displays. Thonny first shows a line
such as `%Run hello.py`, and then the output of the program. After the program ends, the Shell still knows
the program's variables and functions: type the name of a variable at the `>>>` prompt to see its value, or
call one of the program's functions.

To see the values of all the variables in a separate area, click **View**, then **Variables**.

:::{note}
Do not give your program the name of a Python module, for example `random.py`, `math.py` or `turtle.py`.
When your program imports that module, Python finds your file first, and the import does not work as you
expect.
:::

## What is displayed: the Shell and a program

**In the Shell, you see the value of each expression that you type.** You do not need `print`:

```
>>> 2 + 3
5
>>> 'hello'
'hello'
>>> print('hello')
hello
```

The value of a string shows with quotes, as Python writes it. `print` shows the text without quotes. Some
statements show nothing in the Shell:

- An assignment, such as `x = 5`, shows nothing. To see the value, type `x` on the next line.
- A call of a function that returns no value (the value `None`), such as `print_twice('Spam')` from
  Chapter 3, shows only what the function displays with `print`. The Shell does not show `None`.

**In a program, you see only what `print` displays.** When you run a program from the editor, Python does
not show the value of an expression on its own line. This program displays nothing at all:

```python
2 + 3
'hello'
```

To see the values, use `print`:

```python
print(2 + 3)
print('hello')
```

## The code of the book in Thonny

The book's code was written for Jupyter notebooks (Colab), and a notebook works like the Shell, with one
difference: **a notebook cell shows the value of its last line only**, if the last line is an expression. It
does not show the value of each line. For example, this cell shows only `5`:

```python
'hello'
2 + 3
```

So the book often puts an expression on the last line of a cell, without `print`, to show its value. Many
other lines of the book use `print`. When you copy the book's code into a program in the Thonny editor, add
`print` to each line whose value you want to see:

| In a notebook cell of the book | In a program in the Thonny editor |
|---|---|
| `n = 17`<br>`n + 25` | `n = 17`<br>`print(n + 25)` |
| `'Spam, ' * 4` | `print('Spam, ' * 4)` |

You do not need to add `print` when you type the code in the Shell.

**Some lines of the book work only in a notebook.** Leave them out in Thonny:

- Lines that start with `%` or `%%`, for example `%%expect TypeError`. They are commands for Jupyter, not
  Python code. In Thonny they cause a `SyntaxError`.
- The setup cells that download files, the lines `import thinkpython` and `import diagram`, and the module
  `jupyturtle` of Chapter 4. These modules are made for notebooks. For a file that the book reads, such as
  `words.txt`, download the file to your computer and give its path to `open`: see "7c. Additions: File
  Paths and for Loops".

-Prof. Rosenthal
