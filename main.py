#region PIP Setup
#chromedriver-py
#schedule
#selenium
#endregion
import selenium.common
#region Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import schedule
import time
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
#endregion

#region Global Parameters
wait = WebDriverWait(None,0)
driver = webdriver.Chrome()
totalFavoriteRestaurantInOnePage = 5
#endregion

#region Custom Input Parameters
phoneNumberToLogin = "531[replace_with_your_number]"
testEnvironment = True
#endregion

#region Selenium XPath, CSS Selector, TAG & Name
loginPage_phoneNumberInputArea_Name = "gsm"
loginPage_confirmSMSCode_CSS = "body > div  > div  > div > div > div> form > div > div > div > div > input"

favoritesPage_container_XPath = "div > main > div > div > section > div:last-child > div:last-child"
favoritesPage_container_CSS = "div > main > div > div > section > div > div > nav > ul"
favoritesPage_container_next_page_CSS = "div > main > div > div > section > div > div > nav > ul > li:last-child"
favoritesPage_container_item_CSS = "div > main > div > div > section > div:last-child > div:last-child > article:nth-child(INDEX) > div > div > div > div > a"
favoritesPage_container_item_isOpen_CSS = "div > main > div > div > section > div:last-child > div:last-child > article:nth-child(INDEX) > div > div > div:nth-child(2) > div:nth-child(2) > div"
#endregion

#region Flow
def login():
    if driver.current_url == "https://getir.com/yemek/":
        print("Input Area Waiting")
        wait.until(EC.visibility_of_element_located((By.NAME, loginPage_phoneNumberInputArea_Name))).send_keys(phoneNumberToLogin+Keys.ENTER)
        print("Phone Number Entered")
        print("Waiting for SMS Code to Enter Manually")
        print("Waiting for Main Page to Load")
        print(driver.find_element(By.CSS_SELECTOR, loginPage_confirmSMSCode_CSS).get_attribute("value"))
        while(len(driver.find_element(By.CSS_SELECTOR, loginPage_confirmSMSCode_CSS).get_attribute("value")) != 4):
            continue
        driver.find_element(By.CSS_SELECTOR, loginPage_confirmSMSCode_CSS).send_keys(Keys.ENTER)

        wait.until(EC.url_to_be("https://getir.com/yemek/restoranlar/"))
    else:
        print("Already Logged In")

    driver.get("https://getir.com/hesap/favori-restoranlarim/")

def get_favorite_restaurant_count():
    totalFavoriteRestaurant = 0
    driver.implicitly_wait(3)

    try:
        paginationSection = driver.find_element(By.CSS_SELECTOR, favoritesPage_container_CSS)
        driver.implicitly_wait(150000)

        print("Favorite restaurants got multiple pages")
        totalPageCount = int(paginationSection.get_attribute("childElementCount")) - 2
        print("Favorite restaurants total page count: " + str(totalPageCount))
        pages = paginationSection.find_elements(By.XPATH, '*')
        lastPage = pages[len(pages) - 2]
        nextPage = pages[len(pages) - 1]
        print("Last Page is: " + lastPage.text)
        lastPageClickItem = lastPage.find_elements(By.XPATH, '*')[0]
        driver.execute_script("arguments[0].click();", lastPageClickItem)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                   favoritesPage_container_next_page_CSS)))  # sections are reloading after pagination clicks. We have to wait for page to load
        nextPage = driver.find_element(By.CSS_SELECTOR,
                                       favoritesPage_container_next_page_CSS)  # we must update the webelement param in order to might use

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, favoritesPage_container_XPath)))
        favorites_section = driver.find_element(By.CSS_SELECTOR, favoritesPage_container_XPath)
        lastPageFavoriteRestaurantCount = int(favorites_section.get_attribute(
            "childElementCount")) - 1  # we subtract 1 for the pagination div to not count
        print("Last page's favorite restaurant count is: " + str(lastPageFavoriteRestaurantCount))
        totalFavoriteRestaurant = (totalFavoriteRestaurantInOnePage * (
                    totalPageCount - 1)) + lastPageFavoriteRestaurantCount
    except selenium.common.NoSuchElementException:
        driver.implicitly_wait(150000)
        print("Favorite restaurants got only 1 page")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, favoritesPage_container_XPath)))
        favorites_section = driver.find_element(By.CSS_SELECTOR, favoritesPage_container_XPath)
        totalFavoriteRestaurant = favorites_section.get_attribute("childElementCount")


    print("Favorite restaurant count is: " + str(totalFavoriteRestaurant))

    return str(totalFavoriteRestaurant)

def choose_random_restaurant(favorite_count):
    if int(favorite_count) > 0:
        if (int(favorite_count) > totalFavoriteRestaurantInOnePage):
            #TODO: go to the related page first, then choose random. Gonna find which page is that randomly chosen is in it
        else:
            randomly_chosen_restaurant = str(random.randint(1, int(favorite_count)))
            print("Randomly Chosen Restaurant Index: " + randomly_chosen_restaurant)
            is_open = driver.find_element(By.CSS_SELECTOR, favoritesPage_container_item_isOpen_CSS.replace("INDEX", randomly_chosen_restaurant))
            is_open = bool(is_open.get_attribute("textContent") == "")
            print("Is Open?: " + str(is_open))

            if is_open:
                restaurant_click = driver.find_element(By.CSS_SELECTOR, favoritesPage_container_item_CSS.replace("INDEX", randomly_chosen_restaurant))
                random_link = restaurant_click.get_attribute("href")
                print("Random Link: " + random_link)
                driver.execute_script('''window.open("''' + random_link + '''","_blank");''')
                driver.switch_to.window(driver.window_handles[-1])
            else:
                print("Selected restaurant is not open. Choosing another one.")
                choose_random_restaurant(favorite_count)
    else:
        print("No favorite restaurant found. Quitting...")

#endregion

#region Initializers
def main():
    global driver
    driver = initialize_driver()

    global wait
    wait = WebDriverWait(driver, 150)

    driver.implicitly_wait(150000)

    orderRandomFood()

def orderRandomFood():
    driver.get("https://getir.com/yemek/restoranlar/")

    login()

    favorite_count = get_favorite_restaurant_count()

    choose_random_restaurant(favorite_count)
    print("Random Selected Restaurant: " + driver.title)

    # TODO: select food by presets for specific restaurant. For example, in Unkapanı Pilavıcısı, Select Tavuklu Pilav to the shopping cart with 1 portion
    # TODO: After selections has been done, go through shoppnig cart section and make an order

    #driver.quit()

def initialize_driver():
    svc = webdriver.ChromeService(executable_path=binary_path)
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=browser_cache")
    return webdriver.Chrome(service=svc, options=chrome_options)
#endregion

if __name__ == "__main__":
    main()