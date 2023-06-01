import os
import requests
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


def download_image(image_url, save_dir):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        filename = os.path.join(save_dir, image_url.split("/")[-1])
        with open(filename, 'wb') as out_file:
            out_file.write(response.content)
        print(f"Successfully downloaded {image_url} to {filename}")
    else:
        print(f"Unable to download {image_url}")


def scrape_images(url, save_dir):
    # 初始化webdriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    print(driver)
    time.sleep(40)
    img_tags = driver.find_elements(By.TAG_NAME, "img")
    for img in img_tags:
        image_url = img.get_attribute('src')
        if image_url:
            download_image(image_url, save_dir)


scrape_images(
    'https://m.pgsoft-games.com/74/index.html?l=zh&btt=1&ot=1568a96385dff502c465b940728ce67[…]=m.pg-redirect.net&or=static.pgsoft-games.com&__hv=1fccefd3',
    './images')
