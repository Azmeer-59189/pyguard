# Sample Python file with intentional issues for testing PyGuard

x = 10  # Global variable


def calculate_sum(a, b):
    x = 5  # Shadowed variable
    if a > 0:
        if b > 0:
            if a > b:
                if b < 10:
                    return a + b  # Deep nesting
    return 0


def unused_function():
    return 42
    print("This is dead code")  # Unreachable code


def complex_function(n):
    if n > 0:
        if n % 2 == 0:
            if n % 3 == 0:
                if n % 5 == 0:
                    return "divisible by 30"
                return "divisible by 6"
            return "even"
        return "odd"
    return "zero"


class BadClass:
    def method1(self):
        if True:
            if True:
                if True:
                    pass  # Deep nesting