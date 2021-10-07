from os import link
from typing import cast
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import json

driver = webdriver.Edge("drivers/msedgedriver.exe")
driver.get("https://www.tokopedia.com/wardah-official/page/1")

datas = []

try:
    while(True):
        body = driver.find_element_by_css_selector("body")
        body.send_keys(Keys.CONTROL, Keys.END)

        next_button_exist = False

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@data-testid="btnShopProductPageNext"]')))
            next_button_elem = driver.find_element_by_xpath(
                '//a[@data-testid="btnShopProductPageNext"]')

            next_button_exist = True

            ActionChains(driver).move_to_element(next_button_elem).perform()
        except:
            next_button_exist = False
            print("[Status] Next Button not found, Trying back button instead")

            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@data-testid="btnShopProductPagePrevious"]')))
                before_button_elem = driver.find_element_by_xpath(
                    '//a[@data-testid="btnShopProductPagePrevious"]')

                ActionChains(driver).move_to_element(
                    before_button_elem).perform()
            except:
                print("[Status] Back button not found, fall back to CTRL+END")

                body.send_keys(Keys.CONTROL, Keys.END)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@data-testid="divProductWrapper"]')))
        wrapper_elems = driver.find_elements_by_xpath(
            '//div[@data-testid="divProductWrapper"]')

        for elem in wrapper_elems:
            title_elem = elem.find_element_by_xpath('.//a[@href][@title]')
            active = True

            try:
                status_elem = elem.find_element_by_xpath(
                    './/div[contains(@aria-label, "status label")]')
                print(f"Product Status : {status_elem.text}")

                active = not "Stok Habis" in status_elem.text
            except Exception as e:
                print("Product Status : Not found")

            print(f'Product Title : {title_elem.get_attribute("title")}')

            datas.append({"link": title_elem.get_attribute("href"),
                         "title": title_elem.get_attribute("title"),
                          "active": active})

            print("-------")

        if next_button_exist:
            ActionChains(driver).move_to_element(next_button_elem).perform()
            next_button_elem.click()
        else:
            print("[Status] Scraping links done")
            break
except Exception as e:
    print("Error", str(e))
finally:
    with open("data.json", "w") as file:
        json.dump(datas, file, indent=4)

    print(f"Total data : {len(datas)}")
    driver.quit()
