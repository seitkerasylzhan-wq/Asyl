#1
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def info(self):
        print(self.name, self.grade)

s1 = Student("Asyl", "A")
s2 = Student("Timur", "B")
s1.info()
s2.info()
