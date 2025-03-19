def some_fun(x):
    try:
        print(f"x = {x}")
        a = 1/x
    except ZeroDivisionError:
        print("Whoops!")
        return float('Inf')
    finally:
        print("Fin")
    return 0

a = some_fun(0)
print(f"a = {a}")
