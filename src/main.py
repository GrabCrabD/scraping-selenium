from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from bs4 import BeautifulSoup
import time
import pickle
import os

# url = "https://moskva.mts.ru/personal"
url = "https://moskva.mts.ru/personal/mobilnaya-svyaz/tarifi/vse-tarifi/dla-smartfona"


def get_cards_online():
    options = webdriver.ChromeOptions()
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url=url)

        # element = driver.find_element(
        #     By.XPATH, '/html/body/div[2]/div/div[1]/mts-main-page/mts-widget-zone[1]/mts-navigation-widget/section/div/div/div/a[1]').click()

        driver.execute_script("window.scrollBy(0,3300)")

        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/div[1]/section/div/div/mts-tariffs-page/div[2]/div/div/div/mts-tariffs-actual/div/div[2]/mts-tariffs/div[2]/button').click()

        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'lxml')
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    return soup.findAll('div', class_='tariff-list__item')


# def get_cards():
#     if os.path.isfile('cached_cards.pkl'):
#         with open('cached_cards.pkl', 'r') as file:
#             info_cards = pickle.load(file)
#     else:
#         info_cards = get_cards_online()
#         with open('cached_cards.pkl', 'w') as file:
#             pickle.dump(info_cards, file)
#     return info_cards

def parse_elem(element):
    if element is None:
        return ''
    return element.get_text("|", strip=True)


info_cards = get_cards_online()

mapping = {
    'title': 'tariff-card__title',
    'description': 'tariff-card__text',
    'info': 'tariff-card__content',
    'price': 'tariff-card__price',
}
data = [
    {
        key: parse_elem(info.find(class_=class_name))
        for key, class_name in mapping.items()
    }
    for info in info_cards
]

print(data)
