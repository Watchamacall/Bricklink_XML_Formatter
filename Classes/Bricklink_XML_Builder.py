class Bricklink_XML_Builder:
    # Builds the XML File and returns it only
    def build_xml(part_details):
        print("Building XML File")

        final_file = "<INVENTORY>\n"

        for part in part_details:
            print("Adding Item: " + part[0])

            item_type = "\t\t<ITEMTYPE>" + 'P' + "</ITEMTYPE>\n"
            item_id = "\t\t<ITEMID>" + part[0] + "</ITEMID>\n"
            colour_type = "\t\t<COLOR>" + part[1] + "</COLOR>\n"
            quantity = "\t\t<MINQTY>" + part[2] + "</MINQTY>\n"

            new_item = "\t<ITEM>\n" + item_type + item_id + colour_type + quantity + "\t</ITEM>\n"

            final_file += new_item
        
        final_file += "</INVENTORY>"

        return final_file
    # Only saves the XML file based on the inputted dats
    def save_xml(final_file, file_name = "Extracted Files"):
        if not file_name.endswith('.xml'):
            file_name += '.xml'
        with open(file_name, "w") as f:
            f.write(final_file)
            print("Saved XML as: " + file_name)
        f.close()

    # Build and saves the XML file based on the inputted data
    def build_and_save_xml(part_details, file_name = "Extracted Files"):
        Bricklink_XML_Builder.save_xml(Bricklink_XML_Builder.build_xml(part_details), file_name)
