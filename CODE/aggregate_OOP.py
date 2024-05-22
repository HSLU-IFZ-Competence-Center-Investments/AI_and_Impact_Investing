import os
import pandas as pd
from tqdm import tqdm
import regex as re
# from configs.misc_config import cfg # only if run alone
import copy

class FileCounter:
    def __init__(self, path):
        self.path = path
        self.folder_files_dict = {}
        self.valid_files_dict = {}  # Dictionary to store valid files and their folders
        self.sdg_goals = ['No Poverty', 'Zero Hunger', 'Good Health and Well-being', 'Quality Education',
                          'Gender Equality', 'Clean Water and Sanitation', 'Affordable and Clean Energy',
                          'Decent Work and Economic Growth', 'Industry, Innovation, and Infrastructure',
                          'Reduced Inequality', 'Sustainable Cities and Communities',
                          'Responsible Consumption and Production', 'Climate Action', 'Life Below Water',
                          'Life on Land', 'Peace, Justice, and Strong Institutions', 'Partnerships for the Goals']
        self.sdg_goals_dict = {i + 1: self.sdg_goals[i] for i in range(len(self.sdg_goals))}

    def count_files(self):
        folders = os.listdir(self.path)
        for folder in folders:
            self.folder_files_dict[folder] = 0
            self.valid_files_dict[folder] = []  # Initialize an empty list for each folder

        for folder in tqdm(folders):
            files = os.listdir(os.path.join(self.path, folder))
            valid_files = 0

            for file in files:
                if self.is_valid_file(folder, file):
                    valid_files += 1
                    self.valid_files_dict[folder].append(file)  # Append the valid file to the list

            self.folder_files_dict[folder] = valid_files

        min_value = min(self.folder_files_dict.values())
        print('Files considered:', min_value)
        print(self.folder_files_dict)
        return min_value, self.valid_files_dict  # Return the minimum value and the valid files dictionary

    def is_valid_file(self, folder, file):
        file_path = os.path.join(self.path, folder, file)
        if not os.path.isfile(file_path):
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.readlines()

        user = len(re.findall(r'user:', str(data)))
        assistant = len(re.findall(r'assistant:', str(data)))
        file_not_found = len(re.findall(r"couldn't access the content of the files", str(data))) + \
                         len(re.findall(r"don't have access to the content of the files", str(data))) + \
                         len(re.findall(r"I encountered errors while trying to access the content of the files you uploaded", str(data))) + \
                         len(re.findall(r"It seems that there were no contents in the files you uploaded", str(data)))  # CHECK FILES !

        # check for SDG goals without calling the SDGTextAnalyzer
        sdg_dict = {}
        for goal in self.sdg_goals_dict:
            key = str(goal) + '. ' + self.sdg_goals_dict[goal]
            sdg_dict[key] = {'count': 0, 'position(s)': [], 'rank': 0}

            sdg_dict[key]['count'] += len(re.findall(self.sdg_goals_dict[goal], str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(self.sdg_goals_dict[goal], str(data))]

            goal_number = str(goal)
            sdg_dict[key]['count'] += len(re.findall(r'\bGoal ' + goal_number + r'\b', str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(r'\bGoal ' + goal_number + r'\b', str(data))]

            sdg_dict[key]['count'] += len(re.findall(r'\bSDG ' + goal_number + r'\b', str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(r'\bSDG ' + goal_number + r'\b', str(data))]

        # if sdg_dict is empty, print file
        if all(value['count'] == 0 for value in sdg_dict.values()):
            # print(file, 'is empty in ', folder)
            return False
        # if sdg_dict is not empty, return True only if all conditions are met
        else:
            return user == 3 and assistant == 3 and file_not_found == 0




class SDGTextAnalyzer:
    def __init__(self, sdg_goals_dict):
        self.sdg_goals_dict = sdg_goals_dict

    def analyze_text(self, data, folder, file):
        sdg_dict = {}

        for goal in self.sdg_goals_dict:
            key = str(goal) + '. ' + self.sdg_goals_dict[goal]
            sdg_dict[key] = {'count': 0, 'position(s)': [], 'rank': 0}

            sdg_dict[key]['count'] += len(re.findall(self.sdg_goals_dict[goal], str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(self.sdg_goals_dict[goal], str(data))]

            goal_number = str(goal)
            sdg_dict[key]['count'] += len(re.findall(r'\bGoal ' + goal_number + r'\b', str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(r'\bGoal ' + goal_number + r'\b', str(data))]

            sdg_dict[key]['count'] += len(re.findall(r'\bSDG ' + goal_number + r'\b', str(data)))
            sdg_dict[key]['position(s)'] += [m.start() for m in re.finditer(r'\bSDG ' + goal_number + r'\b', str(data))]

        position_list = [sdg_dict[goal]['position(s)'][0] for goal in sdg_dict if sdg_dict[goal]['position(s)']]
        position_list.sort()

        for goal in sdg_dict:
            if sdg_dict[goal]['position(s)']:
                sdg_dict[goal]['rank'] = position_list.index(sdg_dict[goal]['position(s)'][0]) + 1
            else:
                sdg_dict[goal]['rank'] = None
        
        # print file if sdg_dict is empty
        if all(value['count'] == 0 for value in sdg_dict.values()):
            # print(file, 'IS STILL EMPTY IN', folder)
            pass

        return sdg_dict


class SDGDataAnalyzer:
    def __init__(self, path, min_value, valid_files_dict):
        self.path = path
        self.min_value = min_value
        self.valid_files_dict = valid_files_dict
        self.sdg_goals = ['No Poverty', 'Zero Hunger', 'Good Health and Well-being', 'Quality Education',
                          'Gender Equality', 'Clean Water and Sanitation', 'Affordable and Clean Energy',
                          'Decent Work and Economic Growth', 'Industry, Innovation, and Infrastructure',
                          'Reduced Inequality', 'Sustainable Cities and Communities',
                          'Responsible Consumption and Production', 'Climate Action', 'Life Below Water',
                          'Life on Land', 'Peace, Justice, and Strong Institutions', 'Partnerships for the Goals']
        self.sdg_goals_dict = {i + 1: self.sdg_goals[i] for i in range(len(self.sdg_goals))}
        self.company_dict_q2 = {}
        self.company_dict_q3 = {}
        self.differences_q2_q3 = []

    def analyze_data(self):
        folders = os.listdir(self.path)
        for folder in folders:
            self.company_dict_q2[folder] = {}
            self.company_dict_q3[folder] = {}

        for folder in tqdm(folders):
            files = os.listdir(os.path.join(self.path, folder))
            files.sort(reverse=True)

            # drop files if they are not in valid_files_dict
            files = [file for file in files if file in self.valid_files_dict[folder]]

            # differences company level
            differences_q2_q3_company = []
            for file in files[:self.min_value]:
                if self.is_valid_file(folder, file):
                    data = self.read_file(folder, file)

                    data_q2 = data[data.index('user: Purely based on the information in the files, which SDGs arguably does the company have in the focus?\n'):]
                    user_position = [m.start() for m in re.finditer('user:', str(data_q2))]
                    data_q2 = data_q2[:user_position[1]]

                    data_q3 = data[data.index("user: If you had to, how would you rank these against each other in terms of how prominent they seem to be in the company's self-presentation based on the information provided to you.\n"):]

                    self.company_dict_q2 = self.sdg_text_analysis(data_q2, folder, file, self.company_dict_q2)
                    self.company_dict_q3 = self.sdg_text_analysis(data_q3, folder, file, self.company_dict_q3)

                    if self.company_dict_q2 != self.company_dict_q3:
                        differences_q2_q3_company.append(folder + '/' + file)
            
            self.differences_q2_q3.append(differences_q2_q3_company)

    def is_valid_file(self, folder, file):
        file_path = os.path.join(self.path, folder, file)
        if not os.path.isfile(file_path):
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.readlines()

        user = len(re.findall(r'user:', str(data)))
        assistant = len(re.findall(r'assistant:', str(data)))
        file_not_found = len(re.findall(r"couldn't access the content of the files", str(data))) + \
                         len(re.findall(r"don't have access to the content of the files", str(data))) + \
                         len(re.findall(r"I encountered errors while trying to access the content of the files you uploaded", str(data))) + \
                         len(re.findall(r"It seems that there were no contents in the files you uploaded", str(data))) # CHECK FILES !
        
        # check for SDG goals
        sdg_analyzer = SDGTextAnalyzer(self.sdg_goals_dict)
        sdg_dict = sdg_analyzer.analyze_text(data, folder, file)

        # if sdg_dict is empty, print file
        if all(value['count'] == 0 for value in sdg_dict.values()):
            # print(file, 'is empty in ', folder)
            return False
        # if sdg_dict is not empty, return True
        else:
            return user == 3 and assistant == 3 and file_not_found == 0

    def read_file(self, folder, file):
        file_path = os.path.join(self.path, folder, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.readlines()
        return data

    def sdg_text_analysis(self, data, folder, file, company_dict):
        sdg_analyzer = SDGTextAnalyzer(self.sdg_goals_dict)
        sdg_dict = sdg_analyzer.analyze_text(data, folder, file)
        company_dict[folder][file] = sdg_dict
        return company_dict


class CSVWriter:
    def __init__(self, output_path):
        self.output_path = output_path

    def save_to_csv(self, company_dict, question):
        for folder in company_dict:
            temp_dict = company_dict[folder]
            temp_dict = {k: {k2: v2['rank'] for k2, v2 in v.items()} for k, v in temp_dict.items()}
            df = pd.DataFrame(temp_dict)

            folder_path = os.path.join(self.output_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file_path = os.path.join(folder_path, folder + question + '.csv')
            df.to_csv(file_path)


if __name__ == "__main__":
    path = cfg.PATH.SDG_OUTPUT
    output_path = cfg.PATH.SDG_OUTPUT_AGGREGATED

    file_counter = FileCounter(path)
    min_value, valid_files_dict = file_counter.count_files()
    # min_value = 100
    sdg_data_analyzer = SDGDataAnalyzer(path, min_value, valid_files_dict)
    sdg_data_analyzer.analyze_data()

    csv_writer = CSVWriter(output_path)
    csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q2, '_Q2')
    csv_writer.save_to_csv(sdg_data_analyzer.company_dict_q3, '_Q3')

    differences_q2_q3 = pd.DataFrame(sdg_data_analyzer.differences_q2_q3)
    differences_q2_q3.to_csv(os.path.join(output_path, 'differences_q2_q3.csv'))

    with open(os.path.join(output_path, 'company_dict_q2.txt'), 'w') as f:
        f.write(str(sdg_data_analyzer.company_dict_q2))

    with open(os.path.join(output_path, 'company_dict_q3.txt'), 'w') as f:
        f.write(str(sdg_data_analyzer.company_dict_q3))
