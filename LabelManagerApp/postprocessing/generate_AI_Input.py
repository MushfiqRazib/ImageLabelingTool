import sys, os
import psycopg2
import psycopg2.extras
import string
import re  #d

# from LabelManagerApp.settings import Configuration_Settings
from settings import Configuration_Settings

class Query_Tool(object):
    def __init__(self):
        self.configuration_obj = Configuration_Settings()
        self.DATABASE_NAME = self.configuration_obj.DATABASE_NAME
        self.USER = self.configuration_obj.DATABASE_USER
        self.HOST = self.configuration_obj.DATABASE_HOST
        self.PASSWORD = self.configuration_obj.DATABASE_PASSWORD
        self.PORT = self.configuration_obj.DATABASE_PORT

    def Cycle_through_images(self):
        # init list of quality labeled images
        qualityLabels = []
        # cycle through entries
        connection = psycopg2.connect(user=self.USER,
                              password=self.PASSWORD,
                              host=self.HOST,
                              port=self.PORT,
                              database=self.DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('select "Image_Id","Quality_Labeling" from "public"."Image_Details"')
        for i in cursor:
            i = list(i)
            if i[1] != 0:
                qualityLabels.append(i[1])
        return qualityLabels

    def Cycle_through_labels(self, qualityLabels, label_to_search):
        # cycle through entries
        connection = psycopg2.connect(user=self.USER,
                              password=self.PASSWORD,
                              host=self.HOST,
                              port=self.PORT,
                              database=self.DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('select "Label_Id","Image_Id","Label_Details" from "public"."Label_Details"')
        num_written = 0
        for i in cursor:
            i = list(i)
            if i[0] in qualityLabels:
                # get quality label
                label = str(i[2])
                # check quality label for keyword
                for keyword in label_to_search:
                    i_start = label.find(keyword)
                    i_end = label.find("}]}]",i_start)
                    while (label.find("geometry", i_start, i_end)) != -1:
                        indx = label.find("geometry", i_start)
                        indx_end = label.find("]", indx)
                        substring = label[indx:indx_end]
                        #x,y,x,y...
                        coord_list = [float(s) for s in re.findall(r'-?\d+\.?\d*', substring)]
                        y = coord_list[1::2] # Elements from list1 starting from 1 iterating by 2
                        x = coord_list[0::2] # Elements from list1 starting from 0 iterating by 2
                        xmin = min(x)
                        xmax = max(x)
                        ymin = min(y)
                        ymax = max(y)
                        with open('AI_input.txt', 'a') as file:
                            line = ",".join([i[1],str(xmin),str(ymin),str(xmax),str(ymax),keyword])
                            file.write(line+ '\n')
                            num_written += 1
                        i_start = indx_end
        # feedback to user
        if num_written == 0:
            print("\nNo such label categories have been found amongst the quality labels.")
        else:
            print("\nDesired quality labels have been written to AI_input.txt")

if __name__ == '__main__':
    # Search label for keyword
    input_string = input("What label(s) are you searching for?\n"
                        "Be careful, this input is case sensitive: ")
    label_to_search = [x.strip() for x in input_string.split(',')]
    # list all quality labeled images
    QT = Query_Tool()
    qualityLabels = QT.Cycle_through_images()
    QT.Cycle_through_labels(qualityLabels, label_to_search)
