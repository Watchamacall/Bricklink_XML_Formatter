#region Import
import PyPDF2
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#endregion

#region Global Vars
options = webdriver.FirefoxOptions()
options.headless = True
browser = webdriver.Firefox(options=options)
url = "https://www.bricklink.com/v2/search.page?q="
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
                            part_dic[next_section] = section
                            read_brinklink(next_section)

        export_to_spreadsheet(part_dic)

#region Read Bricklink
def read_brinklink(part_number):

    get_url = url + part_number + "#T=A"
    try:
        browser.get(get_url)
        content = browser.find_element(By.ID, "_idItemTableForP")
        print(content.get_attribute("innerHTML"))
        #TODO: Parse through this content.get_attribute and get the Part Colour Code and the Colon showing the number after it
    finally:
        browser.quit()

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
#endregion