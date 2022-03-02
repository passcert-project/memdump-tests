import csv
from itertools import groupby
import logging
import os
import re
import sys
import time
from natsort import natsorted
from tqdm import tqdm

'''
    TODO: Password/location to save from config file
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

    extension_names = []
    #Get the subdirectories (extension names)
    for f in os.scandir(parent_dir):
       if f.is_dir():
           extension_names.append(f.path)
    
    all_files = []
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
        
        #And add it to the all files, along with the extension name
        all_files.append((os.path.split(os.path.normpath(extension_name))[1], grouped_tests_paths))
       
    #print(all_files)

    #Get the enconded strings for look up
    firstpart, _ = password[:len(password)//2], password[len(password)//2:]
    partial_utf8 = firstpart.encode()
    partial_utf16 = firstpart.encode("utf-16-le")
    full_utf8 = password.encode()
    full_utf16 = password.encode("utf-16-le")
    
    #Create CSV, analyse results and write values in CSV
    with open(os.path.join(parent_dir, "results.csv"), "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file, csv.QUOTE_NONE)
        #Write CSV header for excel compatibility
        csv_writer.writerow(["sep=,"])

        #Now go through all the stuff in all_files
        for (extension_name, extension_files) in all_files:
            logging.info("Processing tests from extension %s", extension_name)
            csv_writer.writerow([f"Extension Name: {extension_name}"])
            #The files were sorted previously and according to the filename created by the program this solution is fine as they should be sorted by test-step
            test_num = 0
            for test in tqdm(extension_files):
                csv_writer.writerow([f"Test {test_num}. Steps", "Partial UTF-8", "Partial UTF-16", "Full UTF-8", "Full UTF-16"])
                step_num = 0

                for step_file in tqdm(test, leave=False):
                    #Open the test step file and read the lines
                    with open(step_file, "rb") as dump_file:
                        #Analyse the results
                        dump_file_lines = dump_file.read()
                        (p8, p16, f8, f16) = processDumpFile(dump_file_lines, partial_utf8, partial_utf16, full_utf8, full_utf16)

                        csv_writer.writerow([step_num, p8, p16, f8, f16])
                        step_num += 1                       
                test_num += 1
                #logging.info("Percentage of tests completed for extension %s: %f%%.", extension_name, test_num / total_tests * 100)                
    return

if __name__=="__main__":

    time_begin = time.time()
    analyseTests(sys.argv[1], sys.argv[2])
    print("CSV generated in ", time.time() - time_begin, " seconds")