import math


def square(a):
    all_diag = set()
    for x in range(1, a + 1):
        for y in range(1, a + 1):
            h = math.sqrt(x * x + y * y)
            if h % 1 == 0:
                all_diag.add(h)

    if all_diag == set():
        return 0, 0

    return max(all_diag), len(all_diag)


if __name__ == '__main__':
    a = int(input())
    if a < 0 or a > 20000:
        pass

    print(square(a))
