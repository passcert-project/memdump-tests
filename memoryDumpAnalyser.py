import csv
from itertools import groupby
import logging
import os
import re
import sys
from natsort import natsorted
from tqdm import tqdm

'''
    TODO: 
        - Perhaps let the user choose which tests they want to make a CSV of (only 1 extension for example)?
        Password/location to save from config file
        Call this script from the tester script at the end maybe?
    '''


def processDumpFile(fileLines, partial_utf8_string, partial_utf16_string, full_utf8, full_utf16):
    n1, n2, n3, n4 = fileLines.count(partial_utf8_string), fileLines.count(partial_utf16_string), fileLines.count(full_utf8), fileLines.count(full_utf16)
    partial_utf8_count = n1 - n3
    partial_utf16_count = n2 - n4
    full_utf8_count = n3
    full_utf16_count = n4

    return (partial_utf8_count, partial_utf16_count, full_utf8_count, full_utf16_count)

def filterFunc(input):
    #Regex expression to match everything up until the test number of the filename and ignoring test step of the filename (test-test_step-etc...)   
    return re.findall("(.+\d*)(?:-\d+)", input)[0]
    
def analyseTests(password, parent_dir):
    logging.basicConfig(level=logging.INFO)

    #Get the enconded strings for look up
    firstpart, _ = password[:len(password)//2], password[len(password)//2:]
    partial_utf8 = firstpart.encode()
    partial_utf16 = firstpart.encode("utf-16-le")
    full_utf8 = password.encode()
    full_utf16 = password.encode("utf-16-le")

    #Get the subdirectories (extension names)
    extension_names = []
    for f in os.scandir(parent_dir):
       if f.is_dir():
           extension_names.append(f.path)
    
    #For every extension, get all the files
    for extension_name in extension_names:       
        files = []
        for f in os.scandir(os.path.join(parent_dir, extension_name)):
            if f.is_file() and os.path.splitext(f.name)[1] in ".dump":
                files.append(f.path)
        
        #Now sort them naturally
        files_natsorted = natsorted(files)

        #Now group all the tests steps by their test number
        grouped_tests_paths = [list(i) for j, i in groupby(files_natsorted, filterFunc)]
        
        #Create CSV, analyse results and write values in CSV
        with open(os.path.join(parent_dir, f"{extension_name}-results.csv"), "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, csv.QUOTE_NONE)
            #Write CSV header for excel compatibility
            csv_writer.writerow(["sep=,"])

            #TODO: Technically you only really need to do this once so move this out of the loop at some point
            #See how many steps each test has (they should all have the same so pick the first one)
            num_steps = len(grouped_tests_paths[0])

            CSV_Header = ["Test number"]
            test_categories = ["Partial UTF-8", "Partial UTF-16", "Full UTF-8", "Full UTF-16"]

            #Group per test step, not by category since it's easier to look at the results and write them in.
            for step in range(num_steps):
                for category in test_categories:
                    CSV_Header.append(category + f" Step {step}") 
            
            #Write the column titles
            csv_writer.writerow(CSV_Header)

            #Now analyse the files
            test_number = 0
            logging.info("Processing tests from extension %s", extension_name)
            for test in tqdm(grouped_tests_paths):
                row_data = [test_number]

                #For each step
                for step_file in tqdm(test, leave=False):
                    #Open the test step file and read the lines
                    with open(step_file, "rb") as dump_file:
                        #Analyse the results
                        dump_file_lines = dump_file.read()
                        (p8, p16, f8, f16) = processDumpFile(dump_file_lines, partial_utf8, partial_utf16, full_utf8, full_utf16)
                        row_data.extend([p8, p16, f8, f16])

                #Once all the steps are done, write the info in the csv :)
                csv_writer.writerow(row_data)

                #Prepare for next test
                row_data.clear()
                test_number += 1

    return

if __name__=="__main__":

    if (len(sys.argv)) < 3:
        sys.exit("Usage: <password> <dir>\npassword: the password to look for\ndir: the directory of the memory dumps")

    analyseTests(sys.argv[1], sys.argv[2])