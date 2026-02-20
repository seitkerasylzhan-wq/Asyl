#1 
def show(**info):
    for k, v in info.items():
        print(k, ":", v)

show(name="Asyl", age=18)


#2
def get_city(**info):
    print(info.get("city", "No city"))

get_city(city="Zhanik")
get_city(name="Akni")
