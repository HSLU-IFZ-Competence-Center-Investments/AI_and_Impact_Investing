import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
from tqdm import tqdm
import openai, re
from CODE.configs.__config import cfg
from CODE.utils.datamanager import company_foldernames, carbon_fund, growth_fund, company_website_to_name
from CODE.utils.datamanager import from_companyname_to_website, from_website_to_companyname, get_companyfilepaths
from CODE.utils.plotter import plotter
import CODE.website_crawler as websiteCrawler
import CODE.cleaning as cleaning
import CODE.aggregate_OOP as aggregate
import CODE.results as results

class SDGexpert():
    def __init__(self):
        self.directory_path_chat = cfg.PATH.CODE
        self.directory_path = cfg.PATH.PROJECT
        print(self.directory_path_chat)
        print(self.directory_path)

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

        # get API key
        self.API_key()
        # # runs chat.py runs times to create the bot's analysis
        print('Running virtual assistant...')
        for _ in tqdm(range(self.runs)):
            subprocess.run(["python", self.directory_path_chat + "chat.py", self.directory_path], input=self.directory_path.encode())
        
        # # # run aggregate_OOP.py to aggregate the text files
        # print('Aggregating text files...')
        # path = cfg.PATH.SDG_OUTPUT
        # output_path = cfg.PATH.SDG_OUTPUT_AGGREGATED

        # file_counter = aggregate.FileCounter(path)
        # min_value, valid_files_dict = file_counter.count_files()
        # # min_value = 100 # if fixed number of documents should be considered
        # sdg_data_analyzer = aggregate.SDGDataAnalyzer(path, min_value, valid_files_dict)
        # sdg_data_analyzer.analyze_data()
        # # save to csv
        # csv_writer = aggregate.CSVWriter(output_path)
        # csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q2, '_Q2')
        # csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q3, '_Q3')
        # # differences question 2 and question 3
        # differences_q2_q3 = pd.DataFrame(sdg_data_analyzer.differences_q2_q3)
        # differences_q2_q3.to_csv(os.path.join(output_path, 'differences_q2_q3.csv'))
        # # save to txt
        # with open(os.path.join(output_path, 'company_dict_q2.txt'), 'w') as f:
        #     f.write(str(sdg_data_analyzer.company_dict_q2))
        # with open(os.path.join(output_path, 'company_dict_q3.txt'), 'w') as f:
        #     f.write(str(sdg_data_analyzer.company_dict_q3))

        # # # run results.py to get the final results
        # print('Analyzing results...')
        # # run information (ideally, save meta information in txt file in output folder / read in later)
        # run_1 = {'run': 1 , 'model':'GPT 3.5 Turbo','path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED_RECENT_RUNS + '/Run_1/SDG_aggregated').replace("\\","/"), 'temperature': 'default'}
        # run_2 = {'run': 2, 'model':'GPT 4 Turbo','path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED_RECENT_RUNS + '/Run_2/SDG_aggregated').replace("\\","/"), 'temperature': 'default'}
        # current_run = {'model':'GPT 4 Turbo', 'path':str(cfg.PATH.SDG_OUTPUT_AGGREGATED).replace("\\","/"), 'temperature': 0.01}

        # # basic checks current run 
        # df_temp = results.get_ranks()
        # # print(df_temp)
        # # count number of identical index values
        # print('Number of identical index values:\n', df_temp.index.value_counts())
        # # construct dictionary with unique indexes as key and na values in each row as value
        # na_values = {index: df_temp.loc[index].isna().sum() for index in df_temp.index.unique()}
        # # create barplot per key in na_values
        # for key in na_values.keys():
        #     # create barplot
        #     fig = plt.figure(figsize=(10, 5))
        #     plt.bar(na_values[key].index, na_values[key].values, color='skyblue')
        #     plt.grid(axis='y',alpha=0.4)
        #     plt.xlabel('SDGs')
        #     plt.ylabel('N/A values')    
        #     plt.title('N/A values per SDG for ' + key)
        #     plt.xticks(ticks=range(17), labels=na_values[key].index, rotation=90)
        #     plt.savefig(os.path.join(cfg.PATH.OUTPUT_PLOT + '\differences\zero_values\missing_values_' + key +'.png'), dpi=300,bbox_inches='tight')
        #     # clear the plot
        #     plt.close()

        # Boxplots per company
        # results.boxplot_all_companies(comparison_run=run_2)

        # development of standard deviation current run
        # results.analyse_standard_deviation_mean_median()

        # differences between models 
        # results.differences_models(comparison_run=run_2)

        # anonymised graphic current run
        # results.anonymised_graphic()


if __name__ == "__main__":
    # set up expert
    expert = SDGexpert()
    expert.run_all()
