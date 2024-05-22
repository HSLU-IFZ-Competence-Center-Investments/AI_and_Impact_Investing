import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from configs.__config import cfg # only if run alone
from tqdm import tqdm


def website_availability(websites):
    available_websites = []
    for url in tqdm(websites['Website']):
        #print(url)
        try:
            response = requests.get(url)
            # add to list
            available_websites.append(response)
        except requests.exceptions.RequestException as e:
            # add exception status as string to list
            available_websites.append(e)
        except AttributeError as e:
            # add exception status as string to list
            available_websites.append(e)
    # add to dataframe "Status Code"
    websites['Status Code'] = [response.status_code if isinstance(response, requests.models.Response) else response for response in available_websites]
    return websites


# Function to get text from HTML elements while preserving structure
def get_text_with_structure(element):
    text = ''
    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # Include h4 and h10 tags
        text += '\n'  # Add newline before headings
    elif element.name == 'p':
        text += '\n\n'  # Add double newline before paragraphs
    for sub_element in element.children:
        if sub_element.name is None:  # If it's a string, just append it
            text += str(sub_element)
        else:
            text += get_text_with_structure(sub_element)  # Recursively get text
    return text


def crawler(websites, headers, base_path):
    # iterate through websites
    for website in tqdm(websites['Website'], desc='Websites'):
        url = website
        print(1, url)
        # get trunk of url
        trunk = url.split('//')[1].split('/')[0]
        # keep only letters after www.
        trunk = trunk.strip('www.')
        print(2, trunk)

        try:
            # get all links from website
            response = requests.get(url, headers=headers)
            print('Response status code', response.status_code)
            # create list for needed websites
            needed_websites = []
            # add url to needed websites
            needed_websites.append(url)
            if response.status_code != 403:
                soup = bs(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    if 'mailto' in link['href']:
                        continue
                    # if trunk in link['href'] and 'https' in link['href']:
                    if trunk in link['href']:
                        # assign to needed website list
                        needed_websites.append(link['href'])
                        # get links for all pages with trunk in url
                        response_2 = requests.get(link['href'])
                        if response_2.status_code != 403:
                            soup_2 = bs(response_2.content, 'html.parser')
                            links_2 = soup_2.find_all('a', href=True)
                            for link_2 in links_2:
                                if url in link_2['href'] and 'https' in link_2['href']:
                                    needed_websites.append(link_2['href'])
                    if link['href'].startswith('/'):
                        if '/it/' in link['href']:
                            # cut it from link
                            link['href'] = link['href'].replace('/it/', '/')
                        potential_url = url + link['href']
                        # check if link is a subpage
                        response_3 = requests.get(potential_url, headers=headers)
                        if response_3.status_code != 403:
                            needed_websites.append(potential_url)
                            # search for links in subpage
                            soup_3 = bs(response_3.content, 'html.parser')
                            links_3 = soup_3.find_all('a', href=True)
                            for link_3 in links_3:
                                if url in link_3['href'] and 'https' in link_3['href']:
                                    needed_websites.append(link_3['href'])
                                if link['href'].startswith('/'):
                                    potential_url = url + link['href']
                                    # check if link is a subpage
                                    response_4 = requests.get(potential_url, headers=headers)
                                    if response_4.status_code != 403:
                                        needed_websites.append(potential_url)

        except Exception as e:
            print(f'Error: {e} for {url}')
            continue

        # drop duplicates
        needed_websites = list(set(needed_websites))
        print('Number of links: ', len(needed_websites))
        print('Websites: ', needed_websites)

        # save needed_websites to csv
        df = pd.DataFrame(needed_websites, columns=['Website'])
        # create folder needed_websites if not exists
        os.makedirs(os.path.join(base_path, '3_Websites/needed_websites/'), exist_ok=True)
        # save csv with website trunk
        df.to_csv(os.path.join(base_path, '3_Websites/needed_websites/needed_websites_' + trunk + '.csv'), sep=';', encoding='utf-8', index=False)
            
        if len(needed_websites) > 0:
            try:
                # create folder for company
                os.makedirs(os.path.join(base_path, '3_Websites/Texts/' + trunk), exist_ok=True)
                # counter
                counter = 0
                # iterate through needed websites
                for website_url in tqdm(needed_websites, desc='Needed websites'):
                    # get first website from the list
                    url_2 = website_url
                    # check for language by splitting url between / and creating a list
                    language = url_2.split('/')
                    # if any element is 'de', 'fr', 'it' then skip
                    if any(x in language for x in ['de', 'fr', 'it', 'es']):
                        continue
                    else:
                        # increase counter for unique names; 
                        counter += 1
                        # if two times "/en" strip one
                        if url_2.count('/en') > 1:
                            url_2 = url_2.replace('/en', '', 1)
                        print('URL_2: ', url_2)
                        # get website content and parse it
                        response = requests.get(url_2, headers=headers)
                        # keep only text from the website
                        soup = bs(response.content, 'html.parser')

                        # Remove unwanted content
                        unwanted_content = soup.find_all(['style', 'footer', 'script'])  # Find style, script, and footer elements
                        for item in unwanted_content:
                            item.decompose()  # Remove unwanted elements

                        # Get text with structure from the parsed HTML
                        text_with_structure = get_text_with_structure(soup)

                        # filename
                        filename = url_2.strip ('https://').strip ('www.')
                        # replace / with -
                        filename = filename.replace('/', '-').replace('.', '-').replace(':', '-').replace('?', '-').replace('&', '-').replace('=', '-')\
                            .replace('%', '-').replace(';', '-').replace('!', '-').replace('(', '-').replace(')', '-').replace(',', '-')
                        filename = str(counter) + '_' + filename + '.txt'

                        # save text to new file in current directory
                        with open(os.path.join(base_path, '3_Websites/Texts/', trunk + '/' + filename), 'w', encoding='utf-8') as file: 
                                file.write(text_with_structure)

            except Exception as e:
                print(f'Error: {e} for {url_2} of {website}')
                continue


if __name__ == '__main__':
    # path 
    base_path = cfg.PATH.CRAWLER 
    data_path = cfg.PATH.DATA 

    # read websites.csv from data
    websites = pd.read_csv(os.path.join(data_path, 'Fund_1_websites.csv'), sep=';', encoding='utf-8') 
    websites_2 = pd.read_csv(os.path.join(data_path, 'Fund_2_websites.csv'), sep=';', encoding='utf-8') 
    # rename column 0 to Company for both dataframes, then merge
    websites.rename(columns={websites.columns[0]: 'Company'}, inplace=True)
    websites['Fund'] = 'Fund 1'
    websites_2.rename(columns={websites_2.columns[0]: 'Company'}, inplace=True)
    websites_2['Fund'] = 'Fund 2'
    # merge dataframes
    websites = pd.concat([websites, websites_2], ignore_index=True)

    # # check website availability
    websites = website_availability(websites)
    # # save websites to csv
    websites.to_csv(os.path.join(data_path, 'Websites_status.csv'), sep=';', encoding='utf-8', index=False) # PATH

    # # run crawler # use vpn to change IP if many 403 errors
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'} # change to your user agent / other if needed
    crawler(websites, headers, base_path)