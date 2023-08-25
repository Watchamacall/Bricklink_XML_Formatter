from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class Rebrickable:
    def __init__(self, browser_type="Firefox", debug=False, max_wait_time = 60):
        if browser_type.lower() == "firefox":
            self.browser_options = webdriver.FirefoxOptions()
            self.browser_options.headless = not debug
            self.browser = webdriver.Firefox(self.browser_options)
        elif browser_type.lower() == "chrome":
            self.browser_options = webdriver.ChromeOptions()
            self.browser_options.headless = not debug
            self.browser = webdriver.Chrome(self.browser_options)
        elif browser_type.lower() == "edge":
            self.browser_options = webdriver.EdgeOptions()
            self.browser_options.headless = not debug
            self.browser = webdriver.Edge(self.browser_options)

        self.part_url = ["https://rebrickable.com/parts/?get_drill_downs=&q=","&part_cat="]
        self.max_wait_time = max_wait_time

    def get_bricklink_id_and_colour(self, part_number):
        full_url = self.part_url[0] + part_number + self.part_url[1]

        self.browser.get(full_url)

        wait = WebDriverWait(self.browser, self.max_wait_time)

        part_unique_id = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        part_colour_table = wait.until(EC.presence_of_element_located((By.ID, 'colors_table')))

        unique_id_inner = part_unique_id.get_attribute("innerHTML")

        colour_table_inner = part_colour_table.get_attribute("innerHTML")

        unique_id_soup = BeautifulSoup(unique_id_inner, "html.parser")
        colour_table_soup = BeautifulSoup(colour_table_inner, "html.parser")

        id_soup_array = unique_id_soup.find_all("td")
        table_soup_array = colour_table_soup.find_all("td")
        #TODO: Too Many Values to unpack (expected 2) error fix!!
        for index, td in id_soup_array:
            if 'Bricklink' in td:
                bricklink_id = id_soup_array[index + 1]
                break
        for index, td in table_soup_array:
            if part_number in td:
                colour_name = td[index - 1]

        return (bricklink_id, colour_name)