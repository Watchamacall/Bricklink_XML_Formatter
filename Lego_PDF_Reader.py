#region Import
import PyPDF2
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time
#endregion

#region Global Vars
colour_options = webdriver.FirefoxOptions()
part_options = webdriver.FirefoxOptions()
colour_options.headless = False
part_options.headless = True

part_tab = webdriver.Firefox(options=part_options)
colour_tab = webdriver.Firefox(options=part_options)

part_url = "https://www.bricklink.com/v2/search.page?q="
colour_url = "https://www.bricklink.com/catalogColors.asp"
expected_title = ["Search result for ", " - BrickLink Search | BrickLink"]
wait_time = 60

page_down_count = 200

colour_to_id_global = []
#endregion

#region Functions
def get_part_details(pdf_path, start_page, end_page):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        if end_page > len(pdf_reader.pages):
            end_page = len(pdf_reader.pages)
        
        part_dic = {}

        for page_num in range(start_page - 1, end_page):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            sections = page_text.split('\n')

            for i, section in enumerate(sections):
                if section.endswith("x"):  # Check if the current section is a quantity of parts
                    if i + 1 < len(sections):  # Ensure there's a next section
                        next_section = sections[i + 1]

                        if not next_section.endswith("x"): # Remove any issues with the sections repeating (1x 1x 302364) as an example 
                            part_dic[next_section] = section.strip('x')
    return part_dic # Return the dictonary of unique part to quantity

#region Read Bricklink
def get_brinklink_item_id_colour(part_dic):
    part_set = []
    for part in part_dic:
        # Setting up the URL and expected Title of URL
        full_part_url = part_url + part + "#T=A"
        new_title = expected_title[0] + part + expected_title[1]

        item_id_and_colour_id = get_brinklink_item_details(full_part_url, new_title)
        part_set.append(('P', item_id_and_colour_id[0], item_id_and_colour_id[1], part_dic[part]))
    
    return part_set


def get_brinklink_item_details(full_url, expected_title):
    part_tab.get(full_url)

    wait = WebDriverWait(part_tab, 20)

    # Wait for new page and element to load
    wait.until(EC.title_contains(expected_title))
    wait.until(EC.presence_of_element_located((By.ID, "_idItemTableForP")))

    item_overview = part_tab.find_element(By.ID, "_idItemTableForP")
    item = item_overview.get_attribute("innerHTML")
    parsed_item = BeautifulSoup(item, "html.parser")

    source_elements = parsed_item.find_all("span", class_=["pspItemCateAndNo", "pspPCC"])
    
    bricklink_item_id = re.search(r':\s*([^\s]+)', source_elements[0].text).group(1)
    base_colour = re.search(r'\((.*)\)', source_elements[1].text).group(1)
    base_colour_id = colour_to_id(base_colour)

    return [bricklink_item_id, base_colour_id]

#region Colours

def cache_colours():

    colour_tab.get(colour_url)

    colour_to_id = {}

    wait = WebDriverWait(colour_tab, wait_time)

    source = colour_tab.page_source

    font_pattern = r"<font.*?>(.*?)</font>" #The pattern for the webpage

    font_elements = re.findall(font_pattern, source)
    for index in range(len(font_elements)):

        if index == 0:
            cur_index = font_elements[0].replace('&nbsp;','')
        else:
            cur_index = next_index

        if index + 1 < len(font_elements) - 1:
            next_index = font_elements[index + 1].replace('&nbsp;','')
            next_index = next_index.replace(' ', '')
            next_index = next_index.replace('-', '')
            next_index = next_index.replace('(', '')
            next_index = next_index.replace(')', '')


        if cur_index.isnumeric() and next_index.isalpha():
            colour_to_id[next_index] = cur_index
    
    colour_tab.quit()
    return colour_to_id

def colour_to_id(colour):
    colour = colour.replace(' ', '')
    colour = colour.replace ('-', '')
    colour = colour.replace ('(', '')
    colour = colour.replace (')', '')

    if colour_to_id_global[colour]:
        return colour_to_id_global[colour]
    
    return 0

#endregion

def read_brinklink(part_number, quantity):

    get_part_url = part_url + part_number + "#T=A"
    part_tab.get(get_part_url)

    wait = WebDriverWait(part_tab, wait_time)
    new_title = expected_title[0] + part_number + expected_title[1]

    # Wait for new page and element to load
    wait.until(EC.title_contains(new_title))
    wait.until(EC.presence_of_element_located((By.ID,"_idItemTableForP")))

    item_overview = part_tab.find_element(By.ID, "_idItemTableForP")
    item = item_overview.get_attribute("innerHTML")
    item = BeautifulSoup(item, "html.parser")

    class_elements = item.find_all("span", class_=["pspItemCateAndNo", "pspPCC"])

    part_spec = 'P'

    bricklink_item_number = re.search(r':\s*([^\s]+)', class_elements[0].text).group(1)

    item_set = (part_spec, bricklink_item_number, part_number, quantity)
    items.append(item_set)
    print(item_set)


def build_bricklink_xml(items):
    final_file = "<INVENTORY>\n"

    for item in items:
        item_type = "\t\t<ITEMTYPE>" + item[0] + "</ITEMTYPE>\n"
        item_id = "\t\t<ITEMID>" + item[1] + "</ITEMID>\n"
        colour_type = "\t\t<COLOR>" + item[2] + "</COLOR>\n"
        quantity = "\t\t<MINQTY>" + item[3] + "</MINQTY>\n"

        new_item = "\t<ITEM>\n" + item_type + item_id + colour_type + quantity + "\t</ITEM>\n"

        final_file += new_item
    
    final_file += "</INVENTORY>"

    save_xml_file(final_file)

def save_xml_file(final_file):
    with open("Extracted_Parts.xml", "w") as f:
        f.write(final_file)
    f.close()
#endregion
#region Spreadsheet Export
def export_dict_to_excel(data_dict, output_file):
    df = pd.DataFrame(data_dict.items(), columns=["Part No", "Quantity"])
    df.to_excel(output_file, index=False)

def export_to_spreadsheet(part_dic):
    output_excel = pdf_path + "_spreadsheet.xlsx"
    export_dict_to_excel(part_dic, output_excel)
#endregion

#endregion
#region Main Items
if __name__ == "__main__":

    colour_to_id_global = cache_colours() #Cache at the start since we need that for later

    #Getting inputted data

    pdf_path = str(input("Please enter the path to the PDF you wish to view (If it is in the same folder just put the name of the folder)\n"))
    
    if not pdf_path.endswith(".pdf"):
        pdf_path.join(".pdf")
    pdf_path = pdf_path.replace('"', '')

    #Start and End page numbers
    start_page = int(input("Enter the start page: \n"))
    end_page = int(input("Enter the end page: \n"))
    
    #Reading the PDF Pages
    #read_pdf_pages(pdf_path, start_page, end_page)

    dic = get_part_details(pdf_path, start_page, end_page) #Get our dictionary of parts from the PDF
    summarised_parts = get_brinklink_item_id_colour(dic) #Summarise the parts ready for XML usage
    build_bricklink_xml(summarised_parts) #Build and save the XML file

    part_tab.quit() #Quit out of the part_tab to save memory
#endregion