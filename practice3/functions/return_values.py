#1
def is_positive(x):
    return x > 0

print(is_positive(5))
print(is_positive(-2))


#2
def make_squares(nums):
    squares = []
    for n in nums:
        squares.append(n * n)
    return squares

result = make_squares([1, 2, 3, 4])
print(result)

