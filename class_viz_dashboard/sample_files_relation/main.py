from vehicles import Car, ElectricBicycle
from university import Department, Professor, Student, Course
from house import House
from reporting import Report, HTMLFormatter


def demonstrate_relationships():
    # All original functionality works exactly the same
    car = Car("Toyota", "Camry")
    print(car.drive())

    bike = ElectricBicycle()
    print(bike.drive())

    cs_dept = Department("Computer Science")
    prof = Professor("Dr. Smith")
    cs_dept.add_professor(prof)

    student = Student("Alice")
    math = Course("Calculus")
    student.enroll(math)

    my_house = House("123 Main St")
    my_house.add_room("Living Room")

    report = Report()
    print(report.generate(HTMLFormatter()))


if __name__ == "__main__":
    demonstrate_relationships()