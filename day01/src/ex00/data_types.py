def data_types():
    i = 4
    s = "Hello"
    f = 2.0
    b = True
    l = [1, 2, "three"]
    d = {"Skyrim": 2011}
    t = (1, 2, "three")
    st = {1, 2, 3}
    data = [i, s, f, b, l, d, t,  st]
    types = [type(elem).__name__ for elem in data]
    print(types)


if __name__ == '__main__':
    data_types()