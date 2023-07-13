import random
import string
import time
import zipfile
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class VenomAgent:
    def __init__(self, proxy_params=None):
        self.proxy_params = proxy_params
        self.driver = None

    def __enter__(self):
        self.driver = self._get_driver()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()

    def _get_driver(self):
        chrome_options = webdriver.ChromeOptions()
        if self.proxy_params:
            PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = self.proxy_params
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
            chrome_options.add_argument(
                '--ignore-certificate-errors-spki-list')
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        chrome_options.add_argument(f"user-agent={useragent}")
        try:
            chrome_options.add_extension('venomconnect/utils/venomvallet.crx')
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        except:
            raise Exception(
                "venomvallet.crx extension file not found in venomconnect/utils path location")

    def _wait_and_click_element(self, locator):
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(locator)).click()

    def _send_seed(self, seed_key):
        word_list = seed_key.split()
        input_fields = self.driver.find_elements(
            By.XPATH, "//input[starts-with(@name, 'word-')]")
        for i, word in enumerate(word_list):
            input_fields[i].send_keys(word)
        self.driver.implicitly_wait(random.randint(1, 3))
        self._wait_and_click_element((By.ID, "confirm"))

    def _sign_in_wallet(self):
        password = random.choices(string.ascii_uppercase, k=10)
        self.driver.find_element(
            By.CSS_SELECTOR, "input[name='password']").send_keys(password)
        self.driver.find_element(
            By.CSS_SELECTOR, "input[name='passwordConfirm']").send_keys(password)
        self.driver.implicitly_wait(random.randint(1, 3))
        self._wait_and_click_element(
            (By.XPATH, "//button[contains(., 'Sign in the wallet')]"))

    def _connect_to_venom_network(self):
        self._wait_and_click_element(
            (By.XPATH, "/html/body/div[1]/div/div[3]/section/div/div[1]/div/div[1]/span"))
        self._wait_and_click_element(
            (By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/a/div/div/div[2]/div"))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self._wait_and_click_element(
            (By.XPATH, "/html/body/div/div/div/footer/div[2]/button"))

    def connect_wallet(self, seed_key):
        self.driver.switch_to.window(self.driver.window_handles[0])
        self._wait_and_click_element(
            (By.XPATH,
             "/html/body/div/div[1]/div/div[2]/div/div/div[3]/div/div[2]/button/div")
        )
        self._send_seed(seed_key)
        self._sign_in_wallet()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Congratulations!')]")))
        self.driver.get('https://venom.network/tasks')
        self._connect_to_venom_network()
        self.driver.switch_to.window(self.driver.window_handles[0])
        done_button = self.driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[3]/section/div/div[1]/div/div[1]/button")
        if done_button.text == "Done":
            print("Wallet successfully connected")
        else:
            raise Exception("Connect on the wallet failed")


def connect_venom_vallet(seed_key, proxy_params=None, max_retries=2):
    for attempt in range(max_retries):
        try:
            with VenomAgent(proxy_params) as agent:
                agent.connect_wallet(seed_key)
            return  # connection successful, exit the loop and function
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {str(e)}")
            if attempt+1 < max_retries:
                print("Retrying...")

    raise Exception(
        "Failed to connect with VenomAgent after multiple attempts")
