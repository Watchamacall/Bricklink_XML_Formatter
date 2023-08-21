#region Import
import PyPDF2
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
#endregion

#region Global Vars
options = webdriver.FirefoxOptions()
options.headless = True
browser = webdriver.Firefox(options=options)
url = "https://www.bricklink.com/v2/search.page?q="
element_locator = (By.ID, "_idItemTableForP")
expected_title = ["Search result for ", " - BrickLink Search | BrickLink"]

items = []
#endregion

#region Functions
def read_pdf_pages(pdf_path, start_page, end_page):
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
                if section.endswith("x"):  # Check if the section contains 'x'
                    if i + 1 < len(sections):  # Ensure there's a next section
                        next_section = sections[i + 1]
                        if not next_section.endswith("x"):
                            quant = section.strip('x')
                            part_dic[next_section] = quant
                            read_brinklink(next_section, quant)

        build_bricklink_xml(items)
        #export_to_spreadsheet(part_dic)

#region Read Bricklink
def read_brinklink(part_number, quantity):

    get_url = url + part_number + "#T=A"
    browser.get(get_url)

    wait = WebDriverWait(browser, 20)
    new_title = expected_title[0] + part_number + expected_title[1]

    # Wait for new page and element to load
    wait.until(EC.title_contains(new_title))
    wait.until(EC.presence_of_element_located(element_locator))

    item_overview = browser.find_element(By.ID, "_idItemTableForP")
    item = item_overview.get_attribute("innerHTML")
    item = BeautifulSoup(item, "html.parser")

    class_elements = item.find_all("span", class_=["pspItemCateAndNo", "pspPCC"])

    #TODO: Add a gear version to this

    part_spec = 'P'

    bricklink_item_number = re.search(r':\s*([^\s]+)', class_elements[0].text).group(1)

    item_set = (part_spec, bricklink_item_number, part_number, quantity)
    items.append(item_set)
    print(item_set)

    #TODO: Parse through this content.get_attribute and get the Part Colour Code and the Colon showing the number after it

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

    pdf_path = input("Please enter the path to the PDF you wish to view (If it is in the same folder just put the name of the folder)")
    if not pdf_path.endswith(".pdf"):
        pdf_path.join(".pdf")
    pdf_path = pdf_path.strip('"')

    start_page = int(input("Enter the start page: "))
    end_page = int(input("Enter the end page: "))
    
    read_pdf_pages(pdf_path, start_page, end_page)

    browser.quit()
#endregion