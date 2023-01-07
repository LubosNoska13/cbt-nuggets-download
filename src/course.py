
class CourseSkeleton:
    all_courses = {}
    
    def __init__(self, name: str, time: str) -> None:
        assert isinstance(name, str), f"Name: {name} must be string type."
        assert isinstance(time, str), f"Time: {time} must be string type."
        
        self.name = name
        self.time = time
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name, self.time})"


class Course(CourseSkeleton):
    def __init__(self, name: str, time: str, link: str) -> None:
        super().__init__(name, time)
        
        assert isinstance(link, str), f"Link {link} must be string type."
        
        self.link = link
        self.add_course()
    
    def add_course(self):
        self.all_courses[self] = {}
        
    def add_section(self, section_name, section_time):
        section_instance = Section(section_name, section_time)
        self.all_courses[self][section_instance] = []
        return section_instance
        
    def add_lecture(self, section_instance, lecture_name, lecture_time):
        lecture = Lecture(lecture_name, lecture_time)
        self.all_courses[self][section_instance].append(lecture)
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.time}, {self.link})"
        
        
class Section(CourseSkeleton):
    pass
    
    
class Lecture(CourseSkeleton):
    pass
    


# /*** How to use that ***/ #
# course = Course('Linux', '6h30min', 'http://asxnaisnx')
# section = course.add_section('section1', '1h40min')
# course.add_lecture(section, 'lecture1', '4min')
# course.add_lecture(section, 'lecture2', '10min')


# section2 = course.add_section('section2', '2h30min')
# course.add_lecture(section2, 'lecture1', '8min')
# course.add_lecture(section2, 'lecture2', '1min')


# course = Course('Cisco', '10h30min', 'http://asxnasaxaacafv')
# section = course.add_section('section1', '1h40min')
# course.add_lecture(section, 'lecture1', '4min')
# course.add_lecture(section, 'lecture2', '1min')


# for course, all_section in Course.courses.items():
#     print(course.name)
#     for section in all_section.keys():
#         print(section.name)
        
#         print(all_section[section])
#         for lecture in all_section[section]:
#             print(lecture.name)