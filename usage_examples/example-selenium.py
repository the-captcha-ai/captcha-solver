####
# pip install undetected_chromedriver selenium pillow requests flask waitress
# Fill your own UID and API KEY bellow before using.
# Make sure you already have selenium, chrome and undetected_chromedriver installed.
# If you have any issue please create a github issue or you can ask help on Discord https://discord.gg/E7FfzhZqzA
# 
####
# uid="62c6bf7eb1e76d24e366" #Replace with your own UID
# apikey="62d0243f-7107-67ee-f312-09d8f5af84f3" #Replace with your own apikey


uid="" # Change this to correct value
apikey="" #  Change this to correct value
site="demo" # Change demo to corrct value else Free account will be blocked.
sitekey="demo" # Change demo to corrct value else Free account will be blocked.

use_subprocess_error = False # Make it True if you got "got an unexpected keyword argument 'use_subprocess'"

api_url = 'https://free.nocaptchaai.com/api/solve'

from genericpath import exists
import time, platform

import undetected_chromedriver as uc
from selenium import webdriver
import re, requests, json, base64

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementClickInterceptedException,
    WebDriverException,
    TimeoutException,
)

options = webdriver.ChromeOptions()
# options.binary_location = "C:\\Users\\ROG\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
# options.binary_location = "C:\\Users\\ROG\\Documents\\Chromium-Portable-win64-codecs-sync-oracle\\bin\\chrome.exe"
# options.add_argument("start-maximized")
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
if platform.system().startswith('Windows'):
    if use_subprocess_error:
        driver = uc.Chrome(options=options)
    else:
        driver = uc.Chrome(options=options, use_subprocess=True)
else:
    driver = uc.Chrome(options=options)

def main():
    if uid == "" or apikey == "" or site == "demo" or sitekey == "demo": # Do not change this!!!
        print("You need to set => uid => apikey => site and => sitekey first.")
        return False
    driver.get('https://shimuldn.github.io/hcaptcha/2')
    time.sleep(1)
    WebDriverWait(driver, 2, ignored_exceptions=ElementNotVisibleException).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[contains(@title,'checkbox')]")
        )
    )
    
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "checkbox"))).click()
    driver.switch_to.default_content()
    HOOK_CHALLENGE = "//iframe[contains(@title,'content')]"
    WebDriverWait(driver, 15, ignored_exceptions=ElementNotVisibleException).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, HOOK_CHALLENGE))
        )
    time.sleep(1)

    def solve_hcaptcha(driver, EC):
        print("Solving hcaptcha")
        _obj = WebDriverWait(driver, 5, ignored_exceptions=ElementNotVisibleException).until(
            EC.presence_of_element_located((By.XPATH, "//h2[@class='prompt-text']"))
        )
        time.sleep(1)
#         target=re.split(r"containing a", _obj.text)[-1][1:].strip()
        target=_obj.text
        print(f'hcaptcha target {target}')

        WebDriverWait(driver, 10, ignored_exceptions=ElementNotVisibleException).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='task-image']"))
        )
        images_div = driver.find_elements(By.XPATH, "//div[@class='task-image']")

        image_data={}

        # Getting the data for api server format
        user_agent = driver.execute_script("return navigator.userAgent;")
        headers = {
            "Authority": "hcaptcha.com",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://newassets.hcaptcha.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "User-Agent": user_agent,
        }
        for item in images_div:
            name=item.get_attribute("aria-label")
            number=int(name.replace("Challenge Image ", ""))-1
            image_style = item.find_element(By.CLASS_NAME, "image").get_attribute("style")
            url = re.split(r'[(")]', image_style)[2]
            img_base64 = base64.b64encode(requests.get(url, headers = headers).content)
            img_base64_decoded = img_base64.decode('utf-8')
            # print(img_base64_decoded)
            image_data[number]=img_base64_decoded

        # Doing final formating for api by adding mandatory target data_type site_key site and images 
        data_to_send={}
        data_to_send['target']=target
        data_to_send['method']="hcaptcha_base64"
        data_to_send['sitekey']=sitekey
        data_to_send['site']=site
        data_to_send['images']=image_data
        
        full_url=api_url
        

        # Sending the request to api server
        # print(json.dumps(image_data))   # uncomment this to see the request data
        print("Sending request to api server")
        r = requests.post(url = full_url, headers={'Content-Type': 'application/json', 'uid': uid,
        'apikey': apikey}, data = json.dumps(data_to_send))

        if r.json()['status'] == "new":
            time.sleep(2)
            status=requests.get(r.json()['url'])
            if status.json()['status'] == "solved":
                sol=status.json()['solution']
                solInt = list(map(int, sol))
                for item in images_div:
                    name=item.get_attribute("aria-label")
                    nn=int(name.replace("Challenge Image ", ""))-1
                    # print(nn)
                    if nn in solInt:
                        # print(f"Clicking {nn}")
                        item.click()
                        time.sleep(0.2)

                ## clicking the button
                time.sleep(1)
                WebDriverWait(driver, 35, ignored_exceptions=ElementClickInterceptedException).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[@class='button-submit button']"))
                    ).click()

        elif r.json()['status'] == "solved":
                sol=r.json()['solution']
                solInt = list(map(int, sol))
                for item in images_div:
                    name=item.get_attribute("aria-label")
                    nn=int(name.replace("Challenge Image ", ""))-1
                    if nn in solInt:
                        item.click()
                        time.sleep(0.2)

                ## clicking the button
                time.sleep(1)
                WebDriverWait(driver, 35, ignored_exceptions=ElementClickInterceptedException).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[@class='button-submit button']"))
                    ).click()

        time.sleep(2)

        try:
            error_txt=WebDriverWait(driver, 1, 0.1).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='error-text']"))
            )
            print(f'error found {error_txt}')
        except:
            pass


        for i in range(5):
            try:
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='task-image']"))
                )
                solve_hcaptcha(driver, EC)
            except:
                print("hcaptcha Solved successfully")
                break



    def is_challenge_image_clickable(driver):
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='task-image']"))
            )
            return True
        except TimeoutException:
            return False
        

    solve_hcaptcha(driver, EC)


if __name__ == '__main__':
    main()

