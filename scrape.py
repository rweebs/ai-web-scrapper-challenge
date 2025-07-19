from selenium.webdriver import Remote, ChromeOptions, Chrome
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
load_dotenv()




def scrape_website(website,state,member,breed):
    print("Connecting to Scraping Browser...")
    chrome_driver_path = "./chromedriver"
    options = ChromeOptions()

    service = Service(executable_path=chrome_driver_path)
    with Chrome(service=service, options=options) as driver:
        driver.get(website)

        input_state = driver.find_element(By.NAME, "stateID")
        state_select = Select(input_state)
        if state != "":
            state_select.select_by_visible_text(state)
        input_member = driver.find_element(By.NAME, "memberID")
        member_select = Select(input_member)
        if member != "":
            member_select.select_by_visible_text(member)
        input_breed = driver.find_element(By.NAME, "breedID")
        breed_select = Select(input_breed)
        if breed != "":
            breed_select.select_by_visible_text(breed)
        input_submit = driver.find_element(By.NAME, "submitButton")
        input_submit.click()
        time.sleep(10)
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html

def scrape_ranch(website,name,city,location):
    print("Connecting to Scraping Browser...")
    chrome_driver_path = "./chromedriver"
    options = ChromeOptions()

    service = Service(executable_path=chrome_driver_path)
    with Chrome(service=service, options=options) as driver:
        driver.get(website)
        input_name = driver.find_element(By.NAME, "ranch_search_val")

        if name != "":
            input_name.send_keys(name)

        input_city = driver.find_element(By.NAME, "ranch_search_city")

        if city != "":
            input_city.send_keys(city)

        input_location = driver.find_element(By.ID, "search-member-location")
        location_select = Select(input_location)
        if location != "":
            location_select.select_by_visible_text(location)
        input_submit = driver.find_element(By.NAME, "btnsubmit")
        input_submit.click()
        time.sleep(10)
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
