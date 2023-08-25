from pdfminer.high_level import extract_text

class LEGO_PDF_Part_Extractor:
    def __init__(self, pdf_location='', start_page='', end_page=''):
        
        if pdf_location == '':
            self.pdf_location = str(input("Insert the file path to the PDF you wish to extract:\n"))
        else:
            self.pdf_location = pdf_location
        # Ensures the pdf_location has a pdf ending and replaces the quote marks if there is some
        if not self.pdf_location.endswith(".pdf"):
            self.pdf_location.join(".pdf")
        self.pdf_location = self.pdf_location.replace('"', '')
        
        if start_page == '' or end_page == '':
            self.start_page, self.end_page = self.pages_to_extract()
        else:
            self.start_page, self.end_page = start_page, end_page
    # Prompts the user to put in the page numbers 
    def pages_to_extract(self):
        start_page = input("Insert the page number that the first page of parts are found on:\n")
        end_page = input("Insert the page number that the last page of parts are found on:\n")

        if not start_page.isnumeric() or not end_page.isnumeric():
            start_page, end_page = self.pages_to_extract()

        return int(start_page), int(end_page)
    
    # Extracts the parts from the given pages and the pdf given
    def extract_parts(self):
        page_numbers = list(range(self.start_page-1,self.end_page))
        page_text = extract_text(self.pdf_location, page_numbers=page_numbers)
        
        sections = page_text.split('\n')

        self.part_dic = {}

        for i, section in enumerate(sections):
            if section.endswith("x") and i + 1 < len(sections):  # Check if the current section is a quantity of parts
                next_section = sections[i + 1]

                if not next_section.endswith("x"): # Remove any issues with the sections repeating (1x 1x 302364) as an example 
                    for index in range(len(section)):
                        if section[index] == 'x':
                            section = section[:index]
                            break
                    if '\x0c' in section:
                        section = section.replace('\x0c', '')
                    self.part_dic[next_section] = section