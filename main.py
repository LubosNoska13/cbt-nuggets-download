from config import consts
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
import os
import pprint
# os.environ['PATH'] += consts.PATH

options = webdriver.ChromeOptions()

options.add_experimental_option('excludeSwitches', ['enable-logging'])


options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(consts.PATH), options=options)

driver.get("https://www.cbtnuggets.com/it-training/linux/lpic-1")
driver.maximize_window()

print(driver.find_element(By.TAG_NAME, "h1").text)

driver.implicitly_wait(10)

# all_sections_bar = driver.find_element(By.CLASS_NAME, "StyledSkillList-sc-pqcd25-0")

# all_sections = driver.find_element(By.CLASS_NAME, "StyledSkillList-sc-pqcd25-0").get_attribute("innerHTML")

all_sections = driver.find_elements(By.CLASS_NAME, "SkillListItem-sc-pqcd25-1")

print(all_sections)

for section in all_sections:
    # pprint.pprint(section.get_attribute("innerHTML"))
    # pprint.pprint(section)
    section_name = section.find_element(By.CLASS_NAME, "SkillListItemHeaderHeading-sc-pqcd25-5").get_attribute('innerHTML')
    section_name = section_name[section_name.rfind('>')+1:]
    # print('----->',section_name)
    
    
    lecture_arr = section.find_elements(By.CLASS_NAME, "VideoListItemCopy-sc-1rxkvjw-4")
    
    for lecture in lecture_arr:
        lecture_name = lecture.find_element(By.TAG_NAME, "span").get_attribute("innerHTML")
        lecture_name = lecture_name[lecture_name.rfind('>')+1:]
        
        lecture_time = lecture.find_element(By.TAG_NAME, "div").get_attribute("innerHTML")
        pprint.pprint(lecture_time)
    # pprint.pprint(section_name)
    
    
    # SkillListItemHeader-sc-pqcd25-2
# all_lectures = all_sections_bar.find_elements(By.CLASS_NAME, "VideoListItem-sc-1rxkvjw-1")

# arr_lectures = []

# idx = 0

# for section in all_sections:
#     idx+=1
    
#     if idx >= 2:
#         section.click()
#         all_lectures = all_sections_bar.find_elements(By.CLASS_NAME, "VideoListItem-sc-1rxkvjw-1")
        
#     time.sleep(2)
#     # driver.implicitly_wait(10)

# # print(all_sections_bar)

# # print(all_lectures)
# # # driver.implicitly_wait(10)


#     for lecture in all_lectures:
        
#         # lecture.find_element(By.CLASS_NAME, "SkillListItemHeader-sc-pqcd25-2").click()
            
#         time.sleep(2)
#         lecture_name = lecture.find_element(By.TAG_NAME, "span").text
#         # lecture_name = ''.join(i for i in lecture_name if type(i) == str)
        
#         if lecture_name != " ":
#             arr_lectures.append(lecture_name)
#     print(arr_lectures)
# driver.implicitly_wait(5)

# for section in all_sections:
#     # section.find_element(By.TAG_NAME, "span").text
#     print("--------------------")
#     print(section.find_element(By.XPATH, "//span").text)
#     print("--------------------")

# for section in all_sections:
#     print(section.

# print(all_sections)

driver.quit()