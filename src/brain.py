import urllib
from selenium.webdriver.common.by import By
from .course import Course
import requests
import json
import time
import os

from yt_dlp import YoutubeDL

class Brain:
    links_array = []
    
    def __init__(self):
        self.is_internet_connection()
    
    def is_internet_connection(self, host: str="http://google.com"):
        try:
            urllib.request.urlopen(host)
        except:
            raise Exception("You don't have internet connection!")
    
    def validate_url_address(self, link: str) -> bool:
        
        try:
            r = requests.get(link)
            
        except Exception as e:
            raise ConnectionError(f"Someting is wrong with the url or server!\nurl: {link}")
        
        response = r.status_code
        if 200 <= r.status_code <= 299:
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
    
    def log_in_to_website(self, credentails: dict, driver, log_in_link: str="https://www.cbtnuggets.com/login"):
        
        driver.get(log_in_link)
        driver.implicitly_wait(10)
        
        driver.find_element(By.ID, "email").send_keys(credentails['email'])
        driver.find_element(By.ID, "password").send_keys(credentails['password'])
        time.sleep(4)
        driver.find_element(By.CLASS_NAME, "login-button").click()

    
    def get_html_information(self, driver, link: str):
        
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
        
        driver.implicitly_wait(5)
        
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
                
                
                
    def create_file_structure(self):
        
        path = "Courses\\"
        for course in Course.current_course.keys():
            path = f"Courses\\{course.name} {course.time}"
            os.makedirs(path, exist_ok = True)
            
            for section in Course.current_course[course]:
                path = f"Courses\\{course.name} {course.time}\\{section.name} {section.time}"
                os.makedirs(path, exist_ok = True)
                
                
                # for lecture in Course.current_course[course][section]:
                #     path = f"Courses\\{course.name} {course.time}\\{section.name} {section.time}\\{lecture.name} {lecture.time}"
                #     print(path)
                    # print('\t',lecture.name, lecture.time)
                    # pass
        
        
    
    def download_videos(self, driver):
        
        driver.find_element(By.ID, "overlayPlayButton").click()
        # driver.implicitly_wait(5)
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
            
        ydl_opts = {"outtmpl": "video1"+".%(ext)s", 
                    # 'm3u8': 'ffmpeg', 
                    # "ffmpeg_location": "C:\\yt-dlp\\ffmpeg.exe", 
                    # "prefer_ffmpeg": True, 
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                    }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(m3u8_file)



