from dataclasses import dataclass, asdict
import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# url = "https://moskva.mts.ru/personal"
url = "https://moskva.mts.ru/personal/mobilnaya-svyaz/tarifi/vse-tarifi/dla-smartfona"


@dataclass(frozen=True)
class Plan:
    name: str
    price: int
    descrip: Optional[str] = None
    sms: Optional[int] = None
    calls: Optional[int] = None
    internet: Optional[int] = None


def get_cards_online():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url=url)

        # element = driver.find_element(
        #     By.XPATH, '/html/body/div[2]/div/div[1]/mts-main-page/mts-widget-zone[1]/mts-navigation-widget/section/div/div/div/a[1]').click()

        # driver.execute_script("window.scrollBy(0,3300)")

        # driver.find_element(
        #     By.XPATH, '/html/body/div[2]/div/div[1]/section/div/div/mts-tariffs-page/div[2]/div/div/div/mts-tariffs-actual/div/div[2]/mts-tariffs/div[2]/button').click()

        # time.sleep(3)
        titles = []
        for title in driver.find_elements(By.CLASS_NAME, "tariff-card__title"):
            titles.append(title.text.strip())

        descrips = []
        for descrip in driver.find_elements(By.CLASS_NAME, "tariff-card__text"):
            descrips.append(descrip.text.strip())

        soup = BeautifulSoup(driver.page_source, 'lxml')

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    cards = [i.text for i in soup.findAll('div', class_='tariff-list__item')]

    return cards, titles, descrips


def make_plan(card: str, title: str, descrip: str) -> Optional[Plan]:

    # убираем лишние символы переноса строк, пробелов и тп
    card = ' '.join(card.split())
    price = parse_price(card)

    internet = parse_internet(card)
    calls, sms = parse_sms_and_calls(card)

    return Plan(title, price, descrip, internet=internet, sms=sms, calls=calls)


def parse_internet(card) -> Optional[int]:
    internet_match = re.search(
        pattern=r'(?i)(\d+)\sГБ',
        string=card
    )
    if internet_match:
        return int(internet_match.group(1))
    return


def parse_sms_and_calls(card) -> tuple[Optional[int], Optional[int]]:
    sms_and_call_special = re.search(
        pattern=r'(?i)минуты и sms(\d+)/(\d+)',
        string=card
    )
    if sms_and_call_special:
        return tuple(int(x) for x in sms_and_call_special.groups())

    sms = None
    sms_match = re.search(
        pattern=r'(?i)(\d+)\ssms|Сообщения(\d\d)|SMS(\d+)',
        string=card
    )
    if sms_match:
        sms = find_number(sms_match.groups())

    calls = None
    calls_match = re.search(
        pattern=r'(?i)(\d+)\sминут|Минуты(\d+)|(\d+)\sмин',
        string=card
    )
    if calls_match:
        calls = find_number(calls_match.groups())

    return calls, sms


def parse_price(card) -> Optional[int]:
    price_match = re.search(
        pattern=r'(?i)(\d+)\s₽/мес|(\d+)\sруб\./мес\.',
        string=card
    )
    price = None
    if price_match:
        price = find_number(price_match.groups())
    return price


def find_number(a):
    for i in a:
        if str(i).isnumeric():
            return int(i)


def main():
    info_cards, titles, descrips = get_cards_online()

    result = []
    for card, title, description in zip(info_cards, titles, descrips):
        # import ipdb
        # ipdb.set_trace()
        plan = make_plan(card, title, description)
        if plan is not None:
            result.append(asdict(plan))

    with open('result.json', 'w', encoding='utf8') as file:
        json.dump(result, file, ensure_ascii=False,
                  indent=2)


# __ - dunders`
if __name__ == '__main__':
    main()
