import os
import requests
import random
import string
import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class InstaDown:
    def __init__(self, headless=False, download_dir=None, username=None, password=None):
        self.driver = None
        if download_dir:
            self.download_dir = download_dir
        else:
            self.download_dir = os.path.join(os.getcwd(), 'downloads')
        self.current_profile = None
        self._initialize_driver(headless)

        if username and password:
            self.login_to_instagram(username, password)

    def _initialize_driver(self, headless=False):
        # Setup Chrome
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
        options.add_argument("--disable-gpu")  # Fixes some headless issues
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    @staticmethod
    def __remove_duplicates(_list):
        hashset = set(_list)
        return list(hashset)

    @staticmethod
    def __generate_random_filename(extension='jpg'):
        random_str = ''.join(
            random.choices(string.ascii_letters + string.digits, k=10))
        return f"{random_str}.{extension}"

    def __create_download_dir(self, profile_username):
        download_dir = os.path.join(self.download_dir, profile_username)
        os.makedirs(download_dir, exist_ok=True)

    def login_to_instagram(self, username, password):
        self.driver.get("https://www.instagram.com/accounts/login/")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        # Enter login details
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._aagv"))
        )

    def load_target_profile(self, profile_username):
        self.driver.get(f"https://www.instagram.com/{profile_username}/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._aagv"))
        )
        download_dir = os.path.join(self.download_dir, profile_username)
        os.makedirs(download_dir, exist_ok=True)
        self.current_profile = profile_username

    def get_image_links(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        urls = []
        while True:
            while True:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '[data-visualcompletion="loading-state"]')
                except:
                    break

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, "a")
                image_urls = [img.get_attribute("href") for img in image_elements]
                urls.append(image_urls)
            except:
                pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Exit loop if no new content loads
            last_height = new_height

        counter = 0
        filtered_urls = []
        for arr in urls:
            for url in arr:
                if url.__contains__('/p/'):
                    filtered_urls.append(url)
                    counter += 1

        filtered_urls = self.__remove_duplicates(filtered_urls)
        print(f"Found: {len(filtered_urls)} unique urls")
        return filtered_urls

    def get_reel_links(self, profile_username):
        self.driver.get(f"https://www.instagram.com/{profile_username}/reels")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._ac7v"))
        )
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        urls = []
        while True:
            while True:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '[data-visualcompletion="loading-state"]')
                except:
                    break

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, "a")
                image_urls = [img.get_attribute("href") for img in image_elements]
                urls.append(image_urls)
            except:
                pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Exit loop if no new content loads
            last_height = new_height

        counter = 0
        filtered_urls = []
        for arr in urls:
            for url in arr:
                if url.__contains__('/reel/'):
                    filtered_urls.append(url)
                    counter += 1
        print(counter)

        filtered_urls = self.__remove_duplicates(filtered_urls)
        print(len(filtered_urls))
        return filtered_urls

    def _download_only_images_and_carousels(self, all_image_urls, save_dir_name="default"):
        for current_image in all_image_urls:
            self.download_from_url(current_image, save_dir_name)

    def download_video_from_url(self, url, save_dir_name="default"):
        fixed_url = url.replace('reel', 'p')
        if not fixed_url.endswith('/'):
            fixed_url = fixed_url + '/'

        response = requests.get(f'{fixed_url}?__a=1&__d=dis')

        if response.status_code != 200:
            print("Failed to get data from url, check if the url is correct.")
            return

        try:
            data = json.loads(response.text)
            video_req = requests.get(data['graphql']['shortcode_media']['video_url'])
            video_data = video_req.content
            with open(f"{self.download_dir}/{save_dir_name}/{self.__generate_random_filename('mp4')}", "wb") as file:
                print("Video downloaded successfully.")
                file.write(video_data)
        except:
            print("Failed to download video, check if the url is correct, or if it is a reel.")

    def download_only_pics(self, target_profile):
        # Load profile
        try:
            self.load_target_profile(target_profile)
        except:
            pass
        # Get image links
        links = self.get_image_links()
        # Download images
        self._download_only_images_and_carousels(links)

    def download_only_reels(self, target_profile):
        # Get reel links
        links = self.get_reel_links(target_profile)
        # Download reels
        for link in links:
            self.download_video_from_url(link, target_profile)

    def download_from_url(self, url, save_dir_name="default"):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._aagv img"))
        )

        curr = self.driver.find_element(By.CSS_SELECTOR, "main > div > div:last-child")
        self.driver.execute_script("arguments[0].remove();", curr)

        button = None
        images = []
        is_carousel = True
        # check if carousel
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
        except NoSuchElementException:
            # not carousel, download the single image
            print("Single Image")
            single_image = self.driver.find_element(By.CSS_SELECTOR, "._aagv img")
            images.append(single_image.get_attribute('src'))
            is_carousel = False

        # carousel, find and get all images.
        while is_carousel:
            try:
                button.click()
            except:
                break
            image_dwd_elements = self.driver.find_elements(By.CSS_SELECTOR, "._aagv img")
            image_dwd_urls = [img.get_attribute("src") for img in image_dwd_elements]
            for url in image_dwd_urls:
                images.append(url)

        # remove dups, if there are any
        images = self.__remove_duplicates(images)

        # create a download path
        self.__create_download_dir(profile_username=save_dir_name)
        # download all images
        for image in images:
            image_name = self.__generate_random_filename("jpg")
            image_path = os.path.join(f'{self.download_dir}/{save_dir_name}', image_name)
            response = requests.get(image)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                print(f"Image downloaded successfully: {image_name}")
            else:
                print(f"Failed to download image. Status code: {response.status_code}")