from selenium import webdriver
from selenium.webdriver.firefox.service import Service as firefoxService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
import re
import datetime
import certifi
import random
from dotenv import load_dotenv
import os
import smtplib
import ssl
import threading
import random
import undetected_chromedriver as uc

load_dotenv()

def signup(driver):
    driver.get("https://www.apollo.io/sign-up")
    action = ActionChains(driver)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    element.clear()
    action.send_keys_to_element(element, "luckmanguyen85@gmail.com")
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.PrivateSwitchBase-input'))
    )
    element.clear()
    action.move_to_element(element).click().perform()

def login(driver):
    driver.get("https://app.apollo.io/#/login")
    action = ActionChains(driver)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
    )
    element.clear()
    action.send_keys_to_element(element, os.environ.get("EMAIL")).perform()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
    )
    element.clear()
    action.send_keys_to_element(element, os.environ.get("PASSWORD")).perform()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))
    )
    element.click()

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    login(driver)
    time.sleep(1000)
