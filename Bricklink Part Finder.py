from Classes.Bricklink import Bricklink
from Classes.Bricklink_XML_Builder import Bricklink_XML_Builder
import os

if __name__ == "__main__":
    bricklink = Bricklink()

    part_dic = []

    while True:
        part_to_find = input("Part Number (Found on Lego Piece)\nInput 'Exit' to save as XML file\n")

        if part_to_find.upper() == 'EXIT':
            Bricklink_XML_Builder.build_and_save_xml(part_dic)
            break

        colours, part_num = bricklink.get_part_colours(part_to_find)

        if part_num == "":
            new_num = input()
            colours, part_num = bricklink.get_part_colours(new_num)


        i = 0
        for colour in colours:
            print("Press " + str(i) + " for " + colour)
            i+=1
        print("Press " + str(i) + " to return and enter another part") 
        choice = input()

        if choice != str(i):
            was_found = False
            for part in part_dic:
                if part[0] == part_to_find:
                    part[2] += 1
                    was_found = True
                    break
            #Cannot find
            if not was_found:
                part_dic.append([str(part_num),bricklink.colour_to_id(colours[int(choice)]),1])
        os.system('cls')