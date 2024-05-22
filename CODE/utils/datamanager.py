 
import os
# from configs.misc_config import cfg # only if run alone

company_foldernames = ["anticimex.com", "anybotics.com", "beekeeper.io", "bloomfreshglobal.com", "cfp.energy",
                        "cycle0.com", "distran.swiss",
                        "fotokite.com", "frigoveneta.it", "generainc.com", "getyourguide.com", "medimapsgroup.com", "medtrace.dk",
                        "memo-therapeutics.com", "nagibio.ch", "nilt.com", "oncodna.com", "previero.it", "rentcompany.nl",
                        "shl-medical.com", "sulzerschmid.ch", "swissto12.com", "tado.com", "vacuumschmelze.com", 
                        "varjo.com"]

carbon_fund = ['Tado', 'Anticimex', 'SHL Medical', 'BLOOM', 'Previero', 'The rent company', 
                        'Frigoventa', 'CFP Energy', 'CycleO', 'Genera', 'Vacuumschmelze']
growth_fund = ['GetYourGuide', 'Swissto12', 'Beekeeper', 'Onco DNA', 'Varjo', 
                    'Memo Therapeutics', 'NIL Technology', 'Sulzer & Schmid Lab.', 'Fotokite',
                        'MedTrace Pharma', 'Medimaps Group', 'Ecorobotix', 'ANYbotics', 'Distran', 'Nagi Bioscience']

company_website_to_name = {
    "anticimex.com": "Anticimex",
    "anybotics.com": "ANYbotics",
    "beekeeper.io": "Beekeeper",
    "bloomfreshglobal.com": "BLOOM",
    "cfp.energy": "CFP Energy",
    "cycle0.com": "CycleO",
    "distran.swiss": "Distran",
    "fotokite.com": "Fotokite",
    "frigoveneta.it": "Frigoventa",
    "generainc.com": "Genera",
    "getyourguide.com": "GetYourGuide",
    "medimapsgroup.com": "Medimaps Group",
    "medtrace.dk": "MedTrace Pharma",
    "memo-therapeutics.com": "Memo Therapeutics",
    "nagibio.ch": "Nagi Bioscience",
    "nilt.com": "NIL Technology",
    "oncodna.com": "Onco DNA",
    "previero.it": "Previero",
    "rentcompany.nl": "The rent company",
    "shl-medical.com": "SHL Medical",
    "sulzerschmid.ch": "Sulzer & Schmid Lab.",
    "swissto12.com": "Swissto12",
    "tado.com": "Tado",
    "vacuumschmelze.com": "Vacuumschmelze",
    "varjo.com": "Varjo",
    "ecorobotix.com": "Ecorobotix"
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
    for root, dirs, files in os.walk(cfg.PATH.CRAWLER+ f"/{company_foldername}"):
        for file in files:
            file_paths.append(os.path.join(root, file))

    # if folder 1_master_files exists, search for company file 
    if os.path.exists(cfg.PATH.CRAWLER+ "/1_master_files"):
        # check for txt file of company_foldername in 1_master_files (+"txt")
        for root, dirs, files in os.walk(cfg.PATH.CRAWLER+ "/1_master_files"):
            for file in files:
                if company_foldername in file:
                    # overwrite file_paths with the file path of the company_foldername
                    file_paths = [os.path.join(root, file)]

    return file_paths

