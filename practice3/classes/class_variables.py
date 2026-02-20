#1
class Car:
    wheels = 4

    def __init__(self, brand):
        self.brand = brand

car1 = Car("Toyota")
car2 = Car("BMW")

print(car1.wheels)
print(car2.brand)

