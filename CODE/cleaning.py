import os
import pandas as pd
from tqdm import tqdm
import re
import pdfkit
from bs4 import BeautifulSoup
import gzip
# from configs.__config import cfg


def cleaning_documents(data_path):
    directory = os.path.join(data_path, '3_Websites', 'Texts')
    # list folders in directory
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    # create directory for cleaned folders; r'C:\Users\levin\Documents\IFZ\AI_Impact\3_Websites\Texts_cleaned'
    cleaned_directory = os.path.join(data_path, '3_Websites', 'Texts_cleaned')
    if not os.path.exists(cleaned_directory):
        os.makedirs(cleaned_directory)

    # loop through folders
    for folder in tqdm(folders[7:8]):
        print(folder)
        # created folder in cleaned directory
        if not os.path.exists(os.path.join(cleaned_directory, folder)):
            os.makedirs(os.path.join(cleaned_directory, folder))
        # get all files in folder
        files = [f for f in os.listdir(os.path.join(directory, folder)) if os.path.isfile(os.path.join(directory, folder, f))]
        # print(files)
        # loop through 
        for file in tqdm(files):
            # open file
            with open(os.path.join(directory, folder, file), 'r', encoding='utf-8') as f:
                # read file
                text = f.read()

                # if file is empty, skip
                if len(text) == 0:
                    continue
                else:
                    subpages = []
                    lines = text.splitlines()
                    for i in range(len(lines) - 1):
                        line = lines[i]
                        next_line = lines[i + 1]
                        if len(line.split()) < 4 and len(next_line.split()) < 4:
                            subpages.append(line)
                    # replace only the current occurrence of subpages
                    for subpage in subpages:
                        text = text.replace(subpage, '', 1)
                    # count occurrences of subpages standing alone on a line
                    # subpages = {subpage: text.count(subpage)}
                        
                    # replace consecutive spaces with a single space
                    text = re.sub(' +', ' ', text)
                    # remove leading and trailing whitespaces
                    text = text.strip()
                    # consective tabs
                    text = re.sub('\t+', '\t', text)     
                    # replace consecutive newlines with a single newline
                    text = re.sub(r'\n\s*\n', '\n\n', text)    

                    # save to cleaned folder
                    with open(os.path.join(cleaned_directory, folder, file), 'w', encoding='utf-8') as f:
                        f.write(text)
                    # count occurences of subpages standing alone on a line
                    # subpages = {subpage: text.count(subpage) for subpage in subpages}
    
                    # save to cleaned folder
                    with open(os.path.join(cleaned_directory, folder, file), 'w', encoding='utf-8') as f:
                        f.write(text)
                    # close file
                    f.close()
    return cleaned_directory

def create_master_files(data_path):
    cleaned_directory = os.path.join(data_path, '3_Websites/Texts_cleaned')
    # create master_files folder in cleaned directory
    if not os.path.exists(os.path.join(cleaned_directory, '1_master_files')):
        os.makedirs(os.path.join(cleaned_directory, '1_master_files'))
    # loop trough folders in cleaned directory and create master pdfs
    folders = [f for f in os.listdir(cleaned_directory) if os.path.isdir(os.path.join(cleaned_directory, f))]
    for folder in tqdm(folders):
        # master file
        master_file = ""
        # get all files in folder
        files = [f for f in os.listdir(os.path.join(cleaned_directory, folder)) if os.path.isfile(os.path.join(cleaned_directory, folder, f))]
        # sort files by characters before the first underline
        files_keys = [int(file.split('_')[0]) for file in files]
        files = [file for _, file in sorted(zip(files_keys, files))]
        # loop through 
        for file in files:
            # check if file is empty
            if os.stat(os.path.join(cleaned_directory, folder, file)).st_size == 0:
                continue
            # get filename
            filename = os.path.splitext(file)[0].upper()
            # open file
            with open(os.path.join(cleaned_directory, folder, file), 'r', encoding='utf-8') as f:
                # read file
                text = f.read()
                # add text to master file
                master_file += "\n\n" + filename + "\n\n" + text + "\n\n"
                # close file
                f.close()
            # create master file folder
            if not os.path.exists(os.path.join(cleaned_directory, folder)):
                os.makedirs(os.path.join(cleaned_directory, folder))
            # save the master file in 1_master_files folder
            with open(os.path.join(cleaned_directory, '1_master_files', folder + '.txt'), 'w', encoding='utf-8') as f:
                f.write(master_file)
                f.close()

if __name__ == '__main__':

    data_path = cfg.PATH.DATA 
    # read websites.csv
    websites = pd.read_csv(os.path.join(data_path, 'Fund_1_websites.csv'), sep=';', encoding='utf-8') # Fund 1 or 2
    # drop rows with NaN values
    websites = websites.dropna()
    # clean documents
    cleaning_documents(data_path)
    # create master files
    create_master_files(data_path)

