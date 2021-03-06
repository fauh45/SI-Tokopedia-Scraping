from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import json
import datetime

SELLER_ID = "wardah-official"

driver = webdriver.Edge("drivers/msedgedriver.exe")
driver.get("https://www.tokopedia.com/" + SELLER_ID + "/page/1")

seller_name = ""
products = []

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
    seller_name = driver.find_element_by_css_selector("h1").text

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

            product_link = title_elem.get_attribute("href")
            product_link = urljoin(product_link, urlparse(product_link).path)

            reviews = []

            # Open a new tab
            try:
                driver.execute_script(
                    f'window.open("{product_link}", "_blank")')
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

                driver.switch_to.window(driver.window_handles[1])

                WebDriverWait(driver, 25).until(EC.presence_of_element_located((
                    By.XPATH, '//h1[@data-testid="lblPDPDetailProductName"]')))

                while True:
                    driver.find_element_by_css_selector(
                        "body").send_keys(Keys.CONTROL, Keys.END)

                    next_review_page_button = None

                    try:
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                            (By.XPATH, '//button[contains(@aria-label, "Halaman berikutnya")]')))

                        next_review_page_button = driver.find_element_by_xpath(
                            '//button[contains(@aria-label, "Halaman berikutnya")]')

                        ActionChains(driver).move_to_element(
                            next_review_page_button).perform()
                    except Exception as e:
                        print("[Status] Review are less than 2 page long (10=<)")

                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="pdp_comp-review"]/div[@class="css-1jetg87"]')))
                    review_wrapper_elems = driver.find_elements_by_xpath(
                        '//*[@id="pdp_comp-review"]/div[@class="css-1jetg87"]')

                    for review_elem in review_wrapper_elems:
                        review_text_elem = review_elem.find_element_by_xpath(
                            './/p[contains(@data-testid, "txtReviewFilter")]')
                        rating_elem = review_elem.find_element_by_xpath(
                            './/div[contains(@data-testid, "icnGivenRatingFilter")]')
                        date_elem = review_elem.find_element_by_xpath(
                            './/p[contains(@data-testid, "txtDateGivenReviewFilter")]')

                        reviews.append({
                            "review": review_text_elem.text,
                            "rating": rating_elem.get_attribute("data-testid")[-1],
                            "update_date": date_elem.text,
                            "current_date": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                        })

                    if not next_review_page_button is None:
                        ActionChains(driver).move_to_element(
                            next_review_page_button).perform()
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                            (By.XPATH, '//button[contains(@aria-label, "Halaman berikutnya")]')))
                        next_review_page_button.click()
                    else:
                        break
            except Exception as e:
                print("[Status] Getting review error", str(e))
            finally:
                driver.switch_to.window(driver.window_handles[0])

                curr_window = driver.current_window_handle
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    if handle != curr_window:
                        driver.close()

                driver.switch_to.window(curr_window)
                print(f"Got total review of : {len(reviews)}")

            products.append({"link": product_link,
                             "title": title_elem.get_attribute("title"),
                             "active": active,
                             "reviews": reviews})

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
        json.dump({"id": SELLER_ID, "name": seller_name,
                  "products": products}, file, indent=4)

    print(f"Total data : {len(products)}")
    driver.quit()
