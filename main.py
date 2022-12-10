from config import consts
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from src.brain import Brain

def download_course():

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(consts.PATH), options=options)
    driver.get("https://www.cbtnuggets.com/it-training/linux/lpic-1")
    driver.maximize_window()
    
    brain = Brain()
    brain.get_html_information(driver)
    
    driver.quit()


if __name__ == "__main__":
    download_course()