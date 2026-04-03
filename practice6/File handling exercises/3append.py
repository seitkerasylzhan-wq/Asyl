with open("data.txt", "a") as f:
    f.write("New line\n")

with open("data.txt", "r") as f:
    print(f.read())