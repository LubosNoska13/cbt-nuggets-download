import urllib
from selenium.webdriver.common.by import By
from .course import Course


class Brain:
    links_array = []
    
    def __init__(self):
        self.is_internet_connection()
    
    def is_internet_connection(self, host="http://google.com"):
        try:
            urllib.request.urlopen(host)
        except:
            raise Exception("You don't have internet connection!")
        
    def get_course_links(self) -> bool:
        with open("course_links.txt", 'r') as file:
            n_links = 0
            file_content = file.read().splitlines()
            for url in file_content:
                
                if "http" in url or "https" in url:
                    n_links += 1
                    self.links_array.append(url)
                elif set(url) == set(' ') or url == '':
                    pass
                else:
                    print(url)
                    raise Exception("Something is wrong with the url address!")
                
            if n_links == 0:
                raise Exception("File 'course_links.txt' is empty!")
                
        return True
    
    def get_html_information(self, driver):
        
        def get_rid_of_special_characters(element: str) -> str:
            return "".join([x for x in element if x not in "/><:\"#\\|?!*,%[].'';:"])
        

        course_name = driver.find_element(By.TAG_NAME, "h1").get_attribute('innerHTML')
        
        course_time = driver.find_element(By.CLASS_NAME, "CourseOverviewItemAmount-sc-11d3cub-4").get_attribute('innerHTML')
        course_time = course_time[:course_time.find('<')] + 'hours'
        course_time = get_rid_of_special_characters(course_time)
        
        #
        course = Course(name=course_name, time=course_name, link='https://www.cbtnuggets.com/it-training/linux/lpic-1')
        
        driver.implicitly_wait(10)

        all_sections = driver.find_elements(By.CLASS_NAME, "SkillListItem-sc-pqcd25-1")
        
        section_idx = 0
        
        for section in all_sections:
            section_time = 0

            section_name = section.find_element(By.CLASS_NAME, "SkillListItemHeaderHeading-sc-pqcd25-5").get_attribute('innerHTML')
            section_name = section_name[section_name.rfind('>')+1:]
            section_name = get_rid_of_special_characters(section_name)

            section_idx += 1
            lecture_arr = section.find_elements(By.CLASS_NAME, "VideoListItemCopy-sc-1rxkvjw-4")
            
            #
            section_instance = course.add_section(section_name=f"{section_idx}-{section_name}", section_time='')
            
            lecture_idx = 0
            for lecture in lecture_arr:
                lecture_name = lecture.find_element(By.TAG_NAME, "span").get_attribute("innerHTML")
                lecture_name = lecture_name[lecture_name.rfind('>')+1:]
                lecture_name = get_rid_of_special_characters(lecture_name)
                
                
                lecture_time_str = lecture.find_element(By.TAG_NAME, "div").get_attribute("innerHTML")[1:-1].replace(' ','')
                lecture_time_str = get_rid_of_special_characters(lecture_time_str)
                
                lecture_time = int(lecture_time_str[:lecture_time_str.find('m')])
                
                section_time += lecture_time
                lecture_idx += 1
                
                course.add_lecture(section_instance=section_instance, lecture_name=f"{lecture_idx}-{lecture_name}", lecture_time=lecture_time_str)
                
        for section in course.all_courses[course_name]:
            print(section.name, section.time)
            
            for lecture in course.all_courses[course_name][section]:
                print('\t',lecture.name, lecture.time)


