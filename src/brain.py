import urllib
from selenium.webdriver.common.by import By
from .course import Course
import requests
import json
import time
import os
import re

from yt_dlp import YoutubeDL

class Brain:
    links_array = []
    
    def __init__(self):
        if self.is_internet_connection():
            pass
    
    def is_internet_connection(self, host: str="http://google.com") -> bool:
        try:
            urllib.request.urlopen(host)
        except:
            raise Exception("You don't have internet connection!")

        return True
    
    
    def validate_url_address(self, link: str) -> bool:
        
        try:
            r = requests.get(link)
            
        except Exception as e:
            raise ConnectionError(f"Someting is wrong with the url or server!\nurl: {link}")
        
        response = r.status_code
        if 200 <= r.status_code <= 299:
            print(f"Url address is valid: {link}")
            return True
        else:
            raise Exception(f"[{response} Error]: {link}")
        
        
    def get_course_links(self) -> bool:
        
        with open("course_links.txt", 'r') as file:
            n_links = 0
            file_content = file.read().splitlines()
            
            for url in file_content:
                
                if "http" in url or "https" in url:
                    if self.validate_url_address(link=url):
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
    
    
    def get_credentials(self) -> dict:
        
        
        def validate_email(email: str):
            email_pattern =  r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (re.fullmatch(email_pattern, email)):
                return True
            return False
        
        with open("credentials.txt", 'r') as file:
            file_content = file.read().splitlines()
            
            if not all(["email" in ''.join(file_content), "password" in ''.join(file_content)]):
                raise Exception("Email or Password keyword is missing")
            
            for line in file_content:
                
                if not (set(line) == set(" ") or line == ""):
                    
                    if not ":" in line:
                        raise Exception(f"Missing ':' in line> {line}")
                    
                    line = line.split(":")
                    
                    if line[0] == "email":
                        if not (set(line[1]) == set(" ") or line[1] == ""):
                            if validate_email(line[1].strip()):
                                email = line[1].strip()
                            else:
                                raise Exception("Email address is invalid")
                        else:
                            raise Exception("Email placeholder is empty")
                        
                    if line[0] == "password":
                        if not (set(line[1]) == set(" ") or line[1] == ""):
                            password = line[1].strip()
                        else:
                            raise Exception("Password placeholder is empty")
            return {"email": email, "password": password}
                    
                    
    
    def log_in_to_website(self, credentails: dict, driver, log_in_link: str="https://www.cbtnuggets.com/login") -> None:
        
        driver.get(log_in_link)
        time.sleep(5)
        
        driver.find_element(By.ID, "email").send_keys(credentails['email'])
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(credentails['password'])
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, "login-button").click()

    
    def get_html_information(self, driver, link: str) -> None:
        
        def get_rid_of_special_characters(element: str) -> str:
            return "".join([x for x in element if x not in "/><:\"#\\|?!*,%[].'';:"])
        
        def get_better_time(time: int) -> str:
            better_time = ''
            if time // 60 != 0:
                better_time += f"{time // 60}h"
            if time % 60 != 0:
                better_time += f"{time % 60}m"
            return better_time
        
        if self.validate_url_address(link=link):
            pass
        
        print('Waiting for website.')
        time.sleep(5)
        
        course_name = driver.find_element(By.TAG_NAME, "h1").get_attribute('innerHTML')
        
        # course_time = driver.find_element(By.CLASS_NAME, "CourseOverviewItemAmount-sc-11d3cub-4").get_attribute('innerHTML')
        # course_time = course_time[:course_time.find('<')] + 'hours'
        # course_time = get_rid_of_special_characters(course_time)
        
        #! Link, is necessary
        Course.current_course = {}
        course_time = 0
        
        course = Course(name=course_name, time='', link=link)
        
        driver.implicitly_wait(3)

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
                if "min" not in lecture_time_str:
                    lecture_time_str += 'n'
                
                lecture_time = int(lecture_time_str[:lecture_time_str.find('m')])
                
                section_time += lecture_time
                course_time += lecture_time
                lecture_idx += 1
                
                course.add_lecture(section_instance=section_instance, lecture_name=f"{lecture_idx}-{lecture_name}", lecture_time=lecture_time_str)
            
            section_time = get_better_time(section_time)
            driver.implicitly_wait(3)
            
            for course_n in Course.current_course.keys():
                for section in Course.current_course[course]:
                    if section == section_instance:
                        section.time = section_time
            
        course_time = get_better_time(course_time)
            
        for course_n in Course.current_course.keys():
            if course == course_n:
                course_n.time = course_time
                
        print("Have html information.")
                
    # def create_file_structure(self):
        
    #     for course in Course.current_course.keys():
    #         path = os.path.normpath(f"Courses/{course.name} {course.time}")
    #         # path = f"Courses\\{course.name} {course.time}"
    #         os.makedirs(path, exist_ok = True)
            
    #         for section in Course.current_course[course]:
    #             path = os.path.normpath(f"Courses/{course.name} {course.time}/{section.name} {section.time}")
    #             # path = f"Courses\\{course.name} {course.time}\\{section.name} {section.time}"
    #             os.makedirs(path, exist_ok = True)
                
    #             # for lecture in Course.current_course[course][section]:
    #             #     pass
            
    # def create_file_structure(self, path: str):
    #     path = os.path.normpath(path)
        
    #     if not os.path.exists(path):
    #         try:
    #             os.makedirs(path)
    #             return True
    #         except OSError:
    #             raise Exception(f"Creation of the directory {path} failed")
                # return False
        # else:
        #     if path != "Courses/":
        #         logger.info(f"Course already downloaded. Skipped course - {path}")
        #     return False
    
    
    def create_folder_and_download(self, driver) -> None:
        
        def has_dir_all_lectures(path: str, lecture_list: list) -> bool:
            if os.path.exists(path):
                if len(os.listdir(path)) == len(lecture_list):
                    return True
                return False
        
        
        def create_folder(path: str) -> bool:
            path = os.path.normpath(path)
            
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                    return True
                except OSError:
                    raise Exception(f"Creation of the directory {path} failed")
        
        
        sections_click = driver.find_elements(By.CLASS_NAME,  "SkillListItemHeader-sc-pqcd25-2")
        lecture_list_click = driver.find_elements(By.CLASS_NAME, "StyledVideoList-sc-1rxkvjw-0")
        
        
        for course in Course.current_course.keys():
            
            path = f"Courses/{course.name} {course.time}"

            create_folder(path=path)
            print("Start creating file structure.")
            
            sec_idx = 0
            for section, sec_click, all_lectures_click in zip(Course.current_course[course], sections_click, lecture_list_click):
                path = f"Courses/{course.name} {course.time}/{section.name} {section.time}"

                create_folder(path=path)
                
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sec_click)
                
                if sec_idx >= 1:
                    time.sleep(2)
                    sec_click.click()
                
                come_section = True
                lectures_click = all_lectures_click.find_elements(By.CLASS_NAME, "VideoListItem-sc-1rxkvjw-1")
                
                for lecture, lec_click in zip(Course.current_course[course][section], lectures_click):
                    # path = f"Courses/{course.name} {course.time}/{section.name} {section.time}/{lecture.name} {lecture.time}"
                    
                    if not has_dir_all_lectures(path=path, lecture_list=lectures_click):
                        
                        if f"{lecture.name} {lecture.time}" not in os.listdir(path):
                            
                            if come_section:
                                print(f'Starting with section: {section.name}')
                                come_section = False
                                
                            
                            time.sleep(2)
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lec_click)

                            time.sleep(2)
                            lec_click.click()
                            time.sleep(1)
                            driver.execute_script("window.scrollTo(0, 0);")
                            
                            self.download_video(driver=driver, name=f"{lecture.name} {lecture.time}", path=path)
                            # print('')
                            # os.makedirs(os.path.normpath(f"{path}/{lecture.name} {lecture.time}"))
                            print(f"Download lecture: {lecture.name}")
                    else:
                        print(f"Section: {section.name} has all video downloaded.")
                        break
                    
                    
                    time.sleep(2)
                    
                sec_idx += 1
        
    
    # def click_to_sections_and_download(self, driver):
    #     time.sleep(6)
        
    #     sections = driver.find_elements(By.CLASS_NAME,  "SkillListItemHeader-sc-pqcd25-2")
    #     lecture_list = driver.find_elements(By.CLASS_NAME, "StyledVideoList-sc-1rxkvjw-0")
        
    #     idx = 0
    #     for section, all_lectures in zip(sections, lecture_list):
    #         time.sleep(1)
    #         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section)
            
    #         if idx>= 1:
    #             time.sleep(2)
    #             section.click()
            
    #         lectures = all_lectures.find_elements(By.CLASS_NAME, "VideoListItem-sc-1rxkvjw-1")
            
    #         for lecture in lectures:
    #             time.sleep(2)
    #             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lecture)
                
    #             time.sleep(2)
    #             lecture.click()
                
    #             time.sleep(3)
    #             # self.download_videos(driver, 'video', 'Courses\\')
                
    #         idx+=1
            
            
    def download_video(self, driver, name: str, path: str) -> None:
        
        driver.find_element(By.ID, "overlayPlayButton").click()
        time.sleep(5)


        logs = driver.get_log("performance")
    
        # Opens a writable JSON file and writes the logs in it
        with open("network_log.json", "w", encoding="utf-8") as f:
            f.write("[")
    
            # Iterates every logs and parses it using JSON
            for log in logs:
                network_log = json.loads(log["message"])["message"]
    
                # Checks if the current 'method' key has any
                # Network related value.
                if("Network.response" in network_log["method"]
                        or "Network.request" in network_log["method"]
                        or "Network.webSocket" in network_log["method"]):
    
                    # Writes the network log to a JSON file by
                    # converting the dictionary to a JSON string
                    # using json.dumps().
                    f.write(json.dumps(network_log)+",")
            f.write("{}]")
    
        #print("Written json file")
    
        # Read the JSON File and parse it using
        # json.loads() to find the urls containing images.
        json_file_path = "network_log.json"
        with open(json_file_path, "r", encoding="utf-8") as f:
            logs = json.loads(f.read())
    
        # Iterate the logs
        for log in logs:
    
            # Except block will be accessed if any of the
            # following keys are missing.
            try:
                # URL is present inside the following keys
                url = log["params"]["request"]["url"]
                
                if "master" in url and "origin" in url and "token" in url:
                    m3u8_file = url
                    
            except Exception as e:
                pass
            
        path = os.path.normpath(f"{path}/{name}")
        ydl_opts = {"outtmpl": path+".%(ext)s", 
                    # 'm3u8': 'ffmpeg', 
                    # "ffmpeg_location": "C:\\yt-dlp\\ffmpeg.exe", 
                    # "prefer_ffmpeg": True, 
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                    }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(m3u8_file)



