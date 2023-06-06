bases = []

for base in range(8, 37):
    number = int(str(72), base)
    if number % 10 == 3:
        bases.append(str(base))

result = ", ".join(bases)
print(result)
