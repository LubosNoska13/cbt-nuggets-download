import urllib
from selenium.webdriver.common.by import By
from .course import Course
import requests
import json
import time
import os
import re

from src.logging_setup import logger
from yt_dlp import YoutubeDL

class Brain:
    links_array = []
    
    def __init__(self):
        if self.is_internet_connection():
            logger.info("You have access to the internet.")
    
    def is_internet_connection(self, host: str="http://google.com") -> bool:
        try:
            urllib.request.urlopen(host)
        except:
            logger.exception("You don't have internet connection!")
            raise

        return True
    
    
    def validate_url_address(self, link: str) -> bool:
        
        try:
            r = requests.get(link)
            
        except Exception as e:
            raise ConnectionError(f"Someting is wrong with the url or server!\nurl: {link}")
        
        response = r.status_code
        if 200 <= r.status_code <= 299:
            logger.info(f"Url address is valid: {link}")
            return True
        else:
            logger.exception(f"[{response} Error]: {link}")
            raise
        
        
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
                    logger.exception(f"Something is wrong with the url address! {url}")
                    raise
                
            if n_links == 0:
                logger.exception("File 'course_links.txt' is empty!")
                raise
                
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
                logger.exception("Email or Password keyword is missing in 'credentials.txt' file!")
                raise
            
            for line in file_content:
                
                if not (set(line) == set(" ") or line == ""):
                    
                    if not ":" in line:
                        logger.exception(f"Missing ':' in line> {line}")
                        raise
                    
                    line = line.split(":")
                    
                    if line[0] == "email":
                        if not (set(line[1]) == set(" ") or line[1] == ""):
                            if validate_email(line[1].strip()):
                                email = line[1].strip()
                            else:
                                logger.exception("Email address is invalid!")
                                raise
                        else:
                            logger.exception("Email placeholder is empty in file 'credentials.txt'!")
                            raise
                        
                    if line[0] == "password":
                        if not (set(line[1]) == set(" ") or line[1] == ""):
                            password = line[1].strip()
                        else:
                            logger.exception("Password placeholder is empty in file 'credentials.txt'!")
                            raise
                            
            return {"email": email, "password": password}
                    
                    
    
    def log_in_to_website(self, credentails: dict, driver, log_in_link: str="https://www.cbtnuggets.com/login") -> None:
        
        logger.info(f"Logging into website: {log_in_link}")
        
        driver.get(log_in_link)
        time.sleep(5)
        
        driver.find_element(By.ID, "email").send_keys(credentails['email'])
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(credentails['password'])
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, "login-button").click()
        
        time.sleep(6)
        logger.info("Logging in successfully.")

    
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
        
        # Validate url address
        if self.validate_url_address(link=link):
            pass
        
        time.sleep(5)
        logger.info(f"Start scraping website: {link}")
        
        # Find course name
        course_name = driver.find_element(By.TAG_NAME, "h1").get_attribute('innerHTML')
        
        # Reset variable value
        course_time = 0
        
        # Store informations about course
        course = Course(name=course_name, time='', link=link)
        
        driver.implicitly_wait(2)
        
        # Find all sections
        all_sections = driver.find_elements(By.CLASS_NAME, "SkillListItem-sc-pqcd25-1")
        for section_idx, section in enumerate(all_sections):
            
            # Reset variable value
            section_time = 0

            # Find section name
            section_name = section.find_element(By.CLASS_NAME, "SkillListItemHeaderHeading-sc-pqcd25-5").get_attribute('innerHTML')
            section_name = section_name[section_name.rfind('>')+1:].strip()
            section_name = get_rid_of_special_characters(section_name)
            
            # Section index starts at 1
            section_idx += 1
            
            # Store all information about section
            section_instance = course.add_section(section_name=f"{section_idx}-{section_name}", section_time='')
            
            # Find all lectures that belongs current section
            lecture_arr = section.find_elements(By.CLASS_NAME, "VideoListItemCopy-sc-1rxkvjw-4")
            for lecture_idx, lecture in enumerate(lecture_arr):
                
                # Find lecture name 
                lecture_name = lecture.find_element(By.TAG_NAME, "span").get_attribute("innerHTML")
                lecture_name = lecture_name[lecture_name.rfind('>')+1:]
                lecture_name = get_rid_of_special_characters(lecture_name)
                lecture_name = lecture_name.replace("&amp", "&")
                
                # Find lecture time
                lecture_time_str = lecture.find_element(By.TAG_NAME, "div").get_attribute("innerHTML").replace('mins', 'min').strip().replace(' ', '')
                lecture_time_str = get_rid_of_special_characters(lecture_time_str)
                
                # Convert time value to integer number
                lecture_time = int(lecture_time_str[:lecture_time_str.find('m')])
                
                # Count the time
                section_time += lecture_time
                course_time += lecture_time
                
                # Lecture index starts at 1
                lecture_idx += 1
                
                # Store all lecture information
                course.add_lecture(section_instance=section_instance, lecture_name=f"{lecture_idx}-{lecture_name}", lecture_time=lecture_time_str)
            
            # Get better section time in format (3h6m)
            section_time = get_better_time(section_time)
            driver.implicitly_wait(3)
            
            # Store the section time
            for course_n in Course.all_courses.keys():
                for section in Course.all_courses[course]:
                    if section == section_instance:
                        section.time = section_time
            
            # Get Better course time in format (3h6m)
        course_time = get_better_time(course_time)
        
        # Store the course time
        for course_n in Course.all_courses.keys():
            if course == course_n:
                course_n.time = course_time
                
        logger.info("Have html information.")
                
    
    def create_folder_and_download(self, driver, link: str) -> None:
        
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
        
        
        for (course, all_sections), link in zip(Course.all_courses.items(), Brain.links_array):
            
            # Check that the url address are the same
            if course.link == link:
                pass
            else:
                continue
            
            # Go to the website
            driver.get(link)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Create a course directory
            path = f"Courses/{course.name} {course.time}"
            create_folder(path=path)
            
            # Reset the variable value
            sec_idx = 0
            
            # Find all sections
            sections_click = driver.find_elements(By.CSS_SELECTOR, ".padding-20 > div:nth-child(3) > div")
            for section, sec_click in zip(all_sections.keys(), sections_click):
                
                # Create a section directory
                path = f"Courses/{course.name} {course.time}/{section.name} ({section.time})"
                create_folder(path=path)
                
                # Scroll to the section
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sec_click)
                
                # Expand the section bar
                if len(sec_click.find_elements(By.CLASS_NAME, "video-titles")) == 0:
                    sec_click.click()
                    time.sleep(1)
                    
                logger.info(f"Looking at section: {section.name}")
                
        #         lecture_items = sec_click.find_elements(By.CLASS_NAME, "course-video-information")
        #         for lecture, lec_item in zip(all_sections[section], lecture_items):
                    
        #             if not has_dir_all_lectures(path=path, lecture_list=lecture_items):
        #                 if f"{lecture.name} ({lecture.time}).mp4" not in os.listdir(path):
                            
        #                     if len(lec_item.find_elements(By.CLASS_NAME, "active-video")) == 0:
        #                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lec_item)
                                
        #                         lec_click = lec_item.find_element(By.CLASS_NAME, "video-list-title")

        #                         time.sleep(3)
        #                         lec_click.click()
                            
        #                     else:
        #                         time.sleep(1)
        #                         driver.find_element(By.ID, "playButton").click()
                                
                            
        #                     time.sleep(3)
        #                     driver.execute_script("window.scrollTo(0, 0);")
                            
        #                     self.download_video(driver=driver, name=f"{lecture.name} ({lecture.time})", path=path)
        #                     logger.info(f"Downloaded lecture: {lecture.name}")
        #                 else:
        #                     logger.info(f"Lecture: '{lecture.name} {lecture.time}' has already been downloaded.")
        #             else:
        #                 logger.info(f"Section: '{section.name}' has all video downloaded.")
        #                 break
                    
                    
        #         sec_idx += 1
            
        #     logger.info(f"Course: '{course.name}' was succeffully downloaded.")
            
    def download_video(self, driver, name: str, path: str) -> None:
        
        try:
            driver.find_element(By.ID, "overlayPlayButton").click()
        except:
            pass
            # logger.exception(f"Lecture: '{name}' don't have play button!")
            # raise
            
        time.sleep(1)

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
                
                if "master" in url and "token" in url:
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
        
        logger.info(f"Start downloading lecture {name}")
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(m3u8_file)