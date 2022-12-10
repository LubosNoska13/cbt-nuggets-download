
#! Check that the arguments are of the required type
#! Represation

class CourseSkeleton:
    all_courses = {}
    
    def __init__(self, name: str, time: str) -> None:
        self.name = name
        self.time = time


class Course(CourseSkeleton):
    def __init__(self, name: str, time: str, link: str) -> None:
        super().__init__(name, time)
        self.link = link
        self.add_course()
    
    def add_course(self):
        self.all_courses[self.name] = {}
        
    def add_section(self, section_name, section_time):
        section_instance = Section(section_name, section_time)
        self.all_courses[self.name][section_instance] = []
        return section_instance
        
    def add_lecture(self, section_instance, lecture_name, lecture_time):
        lecture = Lecture(lecture_name, lecture_time)
        self.all_courses[self.name][section_instance].append(lecture)
        
        
class Section(CourseSkeleton):
    pass
    
    
class Lecture(CourseSkeleton):
    pass
    
    
# course = Course('Linux', '6h30min', 'http://asxnaisnx')
# section = course.add_section('section1', '1h40min')
# course.add_lecture(section, 'lecture1', '4min')
# course.add_lecture(section, 'lecture2', '10min')


# section = course.add_section('section2', '2h30min')
# course.add_lecture(section, 'lecture1', '8min')
# course.add_lecture(section, 'lecture2', '1min')


# course = Course('Cisco', '10h30min', 'http://asxnasaxaacafv')
# section = course.add_section('section1', '1h40min')
# course.add_lecture(section, 'lecture1', '4min')
# course.add_lecture(section, 'lecture2', '1min')




# print(course.all_courses)

# for section in course.all_courses['Linux']:
#     print(section.name, section.time)
    
#     for lecture in course.all_courses['Linux'][section]:
#         print(lecture.name, lecture.time)