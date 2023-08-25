# Need a browser version (Firefox, Edge, Chrome)
# Debug Headless option
# Manual URL which can be changed by clicking into the Bricklink file itself
# Same for Expected Title
# 

# region Imports
# Web Browser identification
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#OS calls
import os
# Regular Expressions
import re
# Beautiful Soup html parser
from bs4 import BeautifulSoup
#endregion

class Bricklink:
    # Initalising the class
    def __init__(self, browser_type="Firefox", debug=False, cache_colours = True):

        # Defining the URLs
        self.part_url = "https://www.bricklink.com/v2/search.page?q=" # The URL that you search for using the parts (Bricklink URL minus the part number you search for)
        self.colour_url = "https://www.bricklink.com/catalogColors.asp" # The URL that you search for to cache the colours

        # Expected Title
        self.expected_title = ["Search result for ", " - BrickLink Search | BrickLink"] # The title that appears when you search using the part_url

        # Wait Time
        self.max_wait_time = 60 # The maximum wait time for finding the URL items

        # Part Detail Element ID
        self.part_detail_element_id = "_idItemTableForP"
        self.part_detail_classes = ["pspItemCateAndNo", "pspPCC", "pspItemNameLink"]

        # Part Set array (0 = Item Type (Part), 1 = Item ID (Unique ID for Bricklink), 2 = Colour (The unique colour Bricklink uses), 3 = Quantity (The number of the parts needed for the set))
        self.part_set = []

        # Browsers
        match browser_type.lower():
            case "firefox":
                self.browser_options = webdriver.FirefoxOptions()
                self.browser_options.headless=debug
                self.browser = webdriver.Firefox(self.browser_options)
            case "chrome":
                self.browser_options = webdriver.ChromeOptions()
                self.browser_options.headless=debug
                self.browser = webdriver.Chrome(self.browser_options)
            case "edge":
                self.browser_options = webdriver.EdgeOptions()
                self.browser_options.headless=debug
                self.browser = webdriver.Edge(self.browser_options)
        
        if cache_colours:
            self.cache_colours()

    def __del__(self):
        self.browser.quit()

    # Caches the colours from the colour_url webpage specially designed for the Bricklink Colour Guide
    def cache_colours(self):
        print("Caching Colours from Bricklink Website")

        self.browser.get(self.colour_url)

        self.colour_id_dict = {}

        wait = WebDriverWait(self.browser, self.max_wait_time)

        source = self.browser.page_source

        font_pattern = r"<font.*?>(.*?)</font>" #The pattern for the webpage

        font_elements = re.findall(font_pattern, source)

        for index in range(len(font_elements)):

            if index == 0:
                cur_index = font_elements[0].replace('&nbsp;','') # Sets the cur_index on inital value increment
            else:
                cur_index = next_index

            if index + 1 < len(font_elements) - 1:
                next_index = self.strip_characters(font_elements[index + 1])

            if cur_index.isnumeric() and next_index.isalpha():
                print("Caching: " + next_index)
                self.colour_id_dict[next_index] = cur_index

        os.system('cls')

        print("Finished Caching Colours\n\n")

    # Returns the unique Bricklink Colour ID based on the inputted colour
    def colour_to_id(self, colour):
        colour = self.strip_characters(colour)

        if self.colour_id_dict[colour]:
            return self.colour_id_dict[colour]
        
        return None # Returns None if the colour inputted is an invalid colour according to Bricklink
    
    #Takes out the characters in characters_to_strip from string_to_strip
    def strip_characters(self, string_to_strip, characters_to_strip=['&nbsp;',' ', '-', '(', ')']):
        for character in characters_to_strip:
            string_to_strip = string_to_strip.replace(character, '')
        return string_to_strip
    
    # Gets details on all parts in part_dic and returns the 
    def get_part_details(self, part_dic):
        self.part_details = []

        for part in part_dic:
            self.browser.get(self.part_url + part)

            wait = WebDriverWait(self.browser, self.max_wait_time)

            # Wait for new page and element to load
            wait.until(EC.title_contains((self.expected_title[0] + part + self.expected_title[1])))
            item_overview = wait.until(EC.presence_of_element_located((By.ID, self.part_detail_element_id)))

            # item_overview = self.browser.find_element(By.ID, "_idItemTableForP")
            item = item_overview.get_attribute("innerHTML")
            parsed_item = BeautifulSoup(item, "html.parser")

            source_elements = parsed_item.find_all("span", class_=self.part_detail_classes)
            item_name = parsed_item.find_all("a", class_=self.part_detail_classes)

            print("Getting Detail on " + part + " (" + item_name[0].text + ")")
            
            bricklink_item_id = re.search(r':\s*([^\s]+)', source_elements[0].text).group(1)
            base_colour = re.search(r'\((.*)\)', source_elements[1].text).group(1)
            base_colour_id = self.colour_to_id(base_colour)
            self.part_details.append([bricklink_item_id, base_colour_id, part_dic[part]])
        
