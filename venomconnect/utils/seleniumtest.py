import os
import time
import random
import string
import zipfile
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_driver(proxy_params=None, visible=True):
    chrome_options = webdriver.ChromeOptions()
    os.environ['WDM_SSL_VERIFY'] = '0'
    if proxy_params:
        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = proxy_params
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 3,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "webRequest",
                "webRequestAuthProvider"
                ],
            "host_permissions": [
                "<all_urls>"
            ],
            "background": {
                "service_worker": "background.js"
            },
            "minimum_chrome_version":"22.0.0"
        }
                """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "https",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        pluginfile = 'venomconnect/utils/proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    chrome_options.add_argument(f"user-agent={useragent}")
    chrome_options.add_extension('venomvallet.crx')
    if not visible:
        chrome_options.add_argument('--headless')
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)


def connect_venom_vallet(seed_key, proxy_params=None):
    with get_driver(proxy_params) as driver:
        time.sleep(random.randint(15, 20))
        driver.switch_to.window(driver.window_handles[0])
        button = driver.find_element(
            By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div/div[3]/div/div[2]/button/div")
        button.click()
        time.sleep(random.randint(1, 3))
        word_list = seed_key.split()
        input_fields = driver.find_elements(
            By.XPATH, "//input[starts-with(@name, 'word-')]")
        for i, word in enumerate(word_list):
            input_fields[i].send_keys(word)
        confirm_button = driver.find_element(By.ID, "confirm")
        confirm_button.click()
        time.sleep(random.randint(1, 3))
        password = random.choices(string.ascii_uppercase, k=10)
        password_input = driver.find_element(
            By.CSS_SELECTOR, "input[name='password']")
        confirm_input = driver.find_element(
            By.CSS_SELECTOR, "input[name='passwordConfirm']")
        password_input.send_keys(password)
        confirm_input.send_keys(password)
        time.sleep(random.randint(1, 2))
        sign_in_button = driver.find_element(
            By.XPATH, "//button[contains(., 'Sign in the wallet')]")
        sign_in_button.click()
        time.sleep(random.randint(3, 5))
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
        time.sleep(random.randint(2, 3))
        extension_window_handle = driver.window_handles[-1]
        driver.switch_to.window(extension_window_handle)
        connect_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div/div/div/footer/div[2]/button"))
        )
        connect_button.click()
        main_window_handle = driver.window_handles[0]
        driver.switch_to.window(main_window_handle)
        time.sleep(random.randint(2, 4))
