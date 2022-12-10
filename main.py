from config import consts
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.brain import Brain

def download_course():
    
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(consts.PATH), options=options, desired_capabilities=caps)
    
    brain = Brain()
    brain.get_course_links()
    
    for link in brain.links_array:
        brain.log_in_to_website(link=link, credentails={'email': 'martin@xas', 'password': 'ascas'}, driver=driver)
        
        driver.get(link)
        driver.implicitly_wait(5)
        brain.get_html_information(driver=driver, link=link)
        brain.download_videos(driver=driver)
    
    
    driver.quit()


if __name__ == "__main__":
    download_course()