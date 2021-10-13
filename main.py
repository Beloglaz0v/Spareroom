from typing import Union

from environs import Env
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support import ui, expected_conditions as ec


class Spareroom:
    url = "https://www.spareroom.com/roommate/logon.pl?loginfrom_url=/"

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(executable_path='./driver/geckodriver', options=options)
        self.wait = ui.WebDriverWait(self.driver, 10, poll_frequency=1)
        self.login()

    def login(self) -> None:
        self.driver.get(self.url)
        self.driver.find_element_by_id("loginemail").send_keys(self.email)
        self.driver.find_element_by_id("loginpass").send_keys(self.password)
        self.driver.find_element_by_id("sign-in-button").click()

    def search(self, location: str, max_price: Union[int, float, str] = None) -> list:
        self.wait.until(ec.visibility_of_element_located((By.LINK_TEXT, 'Advanced search'))).click()
        self.driver.find_element_by_id("search_by_location_field").send_keys(location)
        if max_price:
            self.driver.find_element_by_id("max-rent").send_keys(max_price)
        self.driver.find_element_by_id("search-button").click()

        data = set()
        while True:
            rooms = self.driver.find_elements_by_class_name('listing-result')
            for room in rooms:
                data.add(room.find_element_by_tag_name('a').get_attribute('href'))
            if not self.next_page:
                break
            self.next_page.click()
        return list(data)

    @property
    def next_page(self) -> FirefoxWebElement:
        try:
            next_page = self.driver.find_element_by_id('paginationNextPageLink')
        except NoSuchElementException:
            next_page = None
        return next_page

    def save(self, data: Union[set, list, str], filename: str = 'data.txt') -> None:
        if isinstance(data, list) or isinstance(data, set):
            data = '\n'.join(data)

        with open(filename, 'w') as f:
            f.write(data)

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    EMAIL = env.str('email')
    PASSWORD = env.str('password')

    assert EMAIL and PASSWORD, 'First you need to add your email and password to the .env file'

    MAX_PRICE = 1000
    LOCATION = 'Brooklyn, Brooklyn, NY'

    spareroom = Spareroom(email=EMAIL, password=PASSWORD)
    rooms = spareroom.search(location=LOCATION, max_price=MAX_PRICE)
    spareroom.save(data=rooms, filename='rooms.txt')
    spareroom.quit()
