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
    
    credentials = brain.get_credentials()
    
    for link in brain.links_array:
        driver.get(link)
        brain.get_html_information(driver=driver, link=link)
    
    brain.log_in_to_website(credentails=credentials, driver=driver)
    
    try:
        brain.create_folder_and_download(driver=driver, link=link)
    finally:
        driver.close()
    
    driver.quit()


if __name__ == "__main__":
    download_course()