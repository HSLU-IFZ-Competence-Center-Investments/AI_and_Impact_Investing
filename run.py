import pandas as pd
import os
from CODE.chat import main as chat_main
from tqdm import tqdm
import openai, re
from CODE.configs.__config import cfg
import CODE.aggregate_OOP as aggregate
import CODE.results as results
import CODE.cleaning as cleaning
import CODE.website_crawler as websiteCrawler
from config import cfg as cfg_main 

class SDGexpert():
    def __init__(self):
        self.directory_path_chat = cfg.PATH.CODE
        self.directory_path = cfg.PATH.PROJECT
        # print(self.directory_path_chat)
        # print(self.directory_path)

        try:
            self.runs = int(input("How many times should the SDG expert analyse the text files?"))
        except ValueError:
            print("Please enter a valid integer.")
            self.runs = int(input("How many times should the SDG expert analyse the text files?"))

    def API_key(self):
        while True:
            try:
                openai.api_key = open("key.txt", "r").read().strip("\n")
                if re.search('^sk-',openai.api_key) is None:
                    print('Invalid API key.')
                    raise FileNotFoundError
                break
            except FileNotFoundError:
                with open("key.txt", "w") as f:
                    f.write(input("Please enter your OpenAI API key: "))            

    def run_all(self):
        print(self.runs)

        if cfg_main.SCRAPE:

            # Website Crawler
            print('Crawling websites...')
            # path 
            base_path = cfg.PATH.CRAWLER 
            data_path = cfg.PATH.DATA 
            # read websites.csv from data
            websites = pd.read_csv(os.path.join(data_path, 'Fund_1_websites.csv'), sep=';', encoding='utf-8') 
            websites_2 = pd.read_csv(os.path.join(data_path, 'Fund_2_websites.csv'), sep=';', encoding='utf-8') 
            # rename column 0 to Company for both dataframes, then merge
            websites.rename(columns={websites.columns[0]: 'Company'}, inplace=True)
            websites['Fund'] = 'Fund_1'
            websites_2.rename(columns={websites_2.columns[0]: 'Company'}, inplace=True)
            websites_2['Fund'] = 'Fund_2'
            # merge dataframes
            websites = pd.concat([websites, websites_2], ignore_index=True)
            # check website availability
            websites = websiteCrawler.website_availability(websites)
            # save websites to csv
            websites.to_csv(os.path.join(data_path, 'Websites_status.csv'), sep=';', encoding='utf-8', index=False) # PATH
            # run crawler # use vpn to change IP if many 403 errors
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'} # change to your user agent / other if needed
            websiteCrawler.crawler(websites, headers, base_path)
        
            # Cleaning created text files
            print('Cleaning text files...')
            # read websites.csv
            websites = pd.read_csv(os.path.join(data_path, 'Websites_status.csv'), sep=';', encoding='utf-8') 
            # clean documents
            cleaning.cleaning_documents(data_path)
            # create master files
            cleaning.create_master_files(data_path)

        if cfg_main.CHAT:

            # get API key
            self.API_key()
            # # runs chat.py runs times to create the bot's analysis
            print('Running virtual assistant...')
            for _ in tqdm(range(self.runs)):
                chat_main()

        if cfg_main.AGGRAGATE:        
            # run aggregate_OOP.py to aggregate the text files
            print('Aggregating text files...')
            path = cfg.PATH.SDG_OUTPUT
            output_path = cfg.PATH.SDG_OUTPUT_AGGREGATED

            file_counter = aggregate.FileCounter(path)
            min_value, valid_files_dict = file_counter.count_files()
            # min_value = 100 # if fixed number of documents should be considered
            sdg_data_analyzer = aggregate.SDGDataAnalyzer(path, min_value, valid_files_dict)
            sdg_data_analyzer.analyze_data()
            # save to csv
            csv_writer = aggregate.CSVWriter(output_path)
            csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q2, '_Q2')
            csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q3, '_Q3')
            # differences question 2 and question 3
            differences_q2_q3 = pd.DataFrame(sdg_data_analyzer.differences_q2_q3)
            differences_q2_q3.to_csv(os.path.join(output_path, 'differences_q2_q3.csv'))
            # save to txt
            with open(os.path.join(output_path, 'company_dict_q2.txt'), 'w') as f:
                f.write(str(sdg_data_analyzer.company_dict_q2))
            with open(os.path.join(output_path, 'company_dict_q3.txt'), 'w') as f:
                f.write(str(sdg_data_analyzer.company_dict_q3))

        if cfg_main.GENERATE_RESULTS:
            # run results.py to get the final results
            print('Analyzing results...')
            # run information (ideally, save meta information in txt file in output folder / read in later)
            # run_1 = {'run': 1 , 'model':'GPT 3.5 Turbo','path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED_RECENT_RUNS + '/Run_1/SDG_aggregated').replace("\\","/"), 'temperature': 'default'} # example
            # run_2 = {'run': 2, 'model':'GPT 4 Turbo','path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED_RECENT_RUNS + '/Run_2/SDG_aggregated').replace("\\","/"), 'temperature': 'default'} # example
            current_run = {'model':'GPT 3.5 Turbo', 'path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED).replace("\\","/"), 'temperature': 0.01}

            # anonymised graphic current run
            results.grid_graphic()


if __name__ == "__main__":
    # set up expert
    expert = SDGexpert()
    expert.run_all()
