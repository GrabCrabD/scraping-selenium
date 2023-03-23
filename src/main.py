from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional
import re
import json

# url = "https://moskva.mts.ru/personal"
url = "https://moskva.mts.ru/personal/mobilnaya-svyaz/tarifi/vse-tarifi/dla-smartfona"


@dataclass(frozen=True)
class Plan:
    name: str
    price: int
    descrip: Optional[str] = None
    sms: str = None
    calls: str = None
    internet: str = None


def get_cards_online():
    options = webdriver.ChromeOptions()
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15")
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

    return soup.findAll('div', class_='tariff-list__item'), titles, descrips


def make_plan(card: str, title, description) -> Optional[Plan]:

    all_words = card.split()

    name = title
    # убираем лишние символы переноса строк
    descrip = re.sub(pattern='\n', repl=' ', string=description)
    price = None
    calls = "No info"
    internet = "No info"
    sms = "No info"
    for index, word in enumerate(all_words):
        internet_match = re.search(
            flags=0,
            pattern=r'(?i)(\d+)\sГБ',
            string=card
        )
        if internet_match:
            internet = internet_match.group()

        if name == 'Тарифище':  # дикий костыль
            sms = '700 SMS'
            calls = '700 минут'
            print(all_words)
        else:
            sms_match = re.search(
                flags=0,
                pattern=r'(?i)(\d+)\ssms|Сообщения(\d+)|SMS(\d+)',
                string=card
            )
            if sms_match:
                sms = sms_match.group()

            calls_match = re.search(
                flags=0,
                pattern=r'(?i)(\d+)\sминут|Минуты(\d+)|(\d+)\sмин',
                string=card
            )
            if calls_match:
                calls = calls_match.group()

        # if '/мес' in x:
        if word in ('₽/мес', 'руб./мес.'):
            price = int(all_words[index-1])
            break

    if price is None:
        return

    return Plan(name, price, descrip, internet=internet, sms=sms, calls=calls)


def main():
    info_cards, titles, descrips = get_cards_online()
    # list_of_blocks: list[tuple(str, str)] = parse_into_blocks(info_cards)
    # [
    #     (title, other),
    #     (title, other),
    #     (title, other),
    #     (title, other),
    #     (title, other),
    # ]
    # for title, other in list_of_blocks:
    #     kwargs = parse_other(other)
    #     plan = Plan(
    #        title=title,
    #        **kwargs
    #     )

    # with open('soup_log.txt', 'w') as file:
    #     for l in info_cards:
    #         file.writelines(l)
    #         file.write('\n')

    with open('soup_log.txt', 'r') as file:
        info_cards = file.readlines()

    result = []
    for index, card in enumerate(info_cards):
        plan = make_plan(card, titles[index], descrips[index])
        if plan is not None:
            result.append(asdict(plan))

    with open('result.json', 'w', encoding='utf8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


# __ - dunders
# Executes only for `python -m kokolala.py`
if __name__ == '__main__':
    main()
