import os
from CODE.configs.__config import cfg

company_foldernames = ["Company 1", "Company 2", "Company 3", "Company 4"]

fund_1 = ["Company 1", "Company 3"] 
fund_2 = ["Company 2", "Company 4"] 

company_website_to_name = {
    "Website 1": "Company 1",
    "Website 2": "Company 2",
    "Website 3": "Company 3",
    "Website 4": "Company 4"
}

def from_companyname_to_website(company_name):
    for website, name in company_website_to_name.items():
        if name == company_name:
            return website
    return None

def from_website_to_companyname(website):
    return company_website_to_name[website]


def get_companyfilepaths(company_foldername):
    file_paths = []
    # for root, dirs, files in os.walk(cfg.PATH.CRAWLER+ f"/{company_foldername}"):
    #     for file in files:
    #         file_paths.append(os.path.join(root, file))

    # if folder 1_master_files exists, search for company file 
    if os.path.exists(os.path.join(cfg.PATH.CRAWLER, "1_master_files")): # os.path.join(cleaned_directory, '1_master_files')
        # print("1_master_files exists")
        # check for txt file of company_foldername in 1_master_files (+"txt")
        for root, dirs, files in os.walk(os.path.join(cfg.PATH.CRAWLER, "1_master_files")):
            for file in files:
                if company_foldername in file:
                    # overwrite file_paths with the file path of the company_foldername
                    file_paths = [os.path.join(root, file)]
    return file_paths
