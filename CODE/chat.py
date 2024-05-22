from utils.chatutils import AssistantSession
from utils.datamanager import get_companyfilepaths
from datetime import datetime
from configs.misc_config import cfg
import os


# ALL COMPANIES:
company_foldernames = [""]

model = "gpt-3.5-turbo" # "gpt-4-turbo"
gpt_name = "SDG expert"
instruction = "You are a sustainable development goals expert. If asked for, answer questions based on the information in the files provided to you."


if __name__ == "__main__":

    run_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    errors = []

    # with open('./CODE/key.txt', 'r') as file:
    with open('./CODE/key.txt', 'r') as file: # path to the key.txt file
        # Read the entire content of the file
        api_key = file.read()

    for company_foldername in company_foldernames:

        print("-"*6 + f"Processing {company_foldername}..." + "-"*6)
        
        try: 
            file_paths = get_companyfilepaths(company_foldername)
            if len(file_paths) == 0:
                print(f"No files found for {company_foldername}. Skipping.")
                errors.append((company_foldername, "No files found."))
                continue


            assistant_session = AssistantSession(
                gpt_name=gpt_name,
                model=model,
                instructions=instruction,
                tools=[{"type": "retrieval"}],
                file_paths=file_paths,
                api_key=api_key
            )


            assistant_session.chat("Please provide me with a summary of the content of all the files in couple of sentences. I do not wish to go through them one by one.\
                                Just give me a general idea of what they are about.")
            assistant_session.chat("Purely based on the information in the files, which SDGs arguably does the company have in the focus?")
            assistant_session.chat("If you had to, how would you rank these against each other in terms of how prominent they seem to be in the company's self-presentation based on the information provided to you.")
            
            savefolder_path = os.path.join(cfg.PATH.SDG_OUTPUT,company_foldername)
            if not os.path.exists(savefolder_path):
                os.makedirs(savefolder_path)
            assistant_session.save(savefolder_path)
        
        except Exception as e:
            errors.append((company_foldername, e))
            print(f"Error with {company_foldername}: ", e)
            continue

    print("-"*6+"Finished processing all companies."+"-"*6)
    

    err_output_folder = cfg.PATH.ERR_OUTPUT
    if not os.path.exists(err_output_folder):
        os.makedirs(err_output_folder)

    with open(os.path.join(err_output_folder,f"error_log_{run_datetime}.txt"), 'w') as f:
        for error in errors:
            f.write(f"{error[0]}: {error[1]}\n")
    f.close()

    print(f"Error log saved to {err_output_folder}")