import os
import re
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from itertools import cycle
from datetime import datetime
import random
import string


def get_proxy_pool(proxylist_url="https://www.proxyscan.io/download?last_check=3800&uptime=50&ping=600&limit=30&type=http,https"):
    try:
        timestamp = os.path.getmtime('proxy-list.txt')
        time_delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
        if time_delta.minutes < 90:
            with open("proxy-list.txt", 'r') as file:
                proxy_file = file.read()
            proxy_list = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', proxy_file)
            proxy_pool = cycle(proxy_list)
            return proxy_pool
        else:
            raise ValueError
    except:
        response = requests.get(proxylist_url)
        if response.status_code == 200:
            with open("proxy-list.txt", "w") as file:
                file.write(response.text)
            proxy_list = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text)
            proxy_pool = cycle(proxy_list)
            return proxy_pool
        else:
            print("Failed to retrieve the text from the URL")


def get_driver(proxypool=None, visible=None):
    chrome_options = webdriver.ChromeOptions()
    if proxypool:
        proxy = next(proxypool)
        chrome_options.add_argument(f'--proxy-server={proxy}')
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    chrome_options.add_argument(f"user-agent={useragent}")
    chrome_options.add_extension('venomvallet.crx')
    if not visible:
        chrome_options.add_argument("-headless")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)


key = os.environ.get("WALLET_SEED")


with get_driver(visible='yes') as driver:
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[0])
    div_element = driver.find_element(
        By.XPATH, "//div[contains(text(), 'Sign in with seed phrase')]")
    button = div_element.find_element(By.XPATH, "./ancestor::button")
    button.click()
    time.sleep(0.5)
    word_list = key.split()
    input_fields = driver.find_elements(
        By.XPATH, "//input[starts-with(@name, 'word-')]")
    for i, word in enumerate(word_list):
        input_fields[i].send_keys(word)
    confirm_button = driver.find_element(By.ID, "confirm")
    confirm_button.click()
    time.sleep(1)
    password = random.choices(string.ascii_uppercase, k=10)
    password_input = driver.find_element(
        By.CSS_SELECTOR, "input[name='password']")
    confirm_input = driver.find_element(
        By.CSS_SELECTOR, "input[name='passwordConfirm']")
    password_input.send_keys(password)
    confirm_input.send_keys(password)
    sign_in_button = driver.find_element(
        By.XPATH, "//button[contains(., 'Sign in the wallet')]")
    sign_in_button.click()
    time.sleep(1)
    driver.get('https://venom.network/tasks')
    connect_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div[3]/section/div/div[1]/div/div[1]/span"))
    )
    connect_button.click()
    ext_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/a/div/div/div[2]/div"))
    )
    ext_button.click()
    time.sleep(1)
    extension_window_handle = driver.window_handles[-1]
    driver.switch_to.window(extension_window_handle)
    connect_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div/footer/div[2]/button"))
    )
    connect_button.click()
    main_window_handle = driver.window_handles[0]
    driver.switch_to.window(main_window_handle)
    time.sleep(10)
