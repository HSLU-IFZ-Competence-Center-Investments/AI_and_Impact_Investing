import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from configs.misc_config import cfg # only if run alone
from CODE.configs.__config import cfg
# from utils.datamanager import * # only if run alone
# from utils.plotter import plotter # only if run alone
from CODE.utils.datamanager import fund_1, fund_2, company_website_to_name
from scipy.stats import ttest_rel
from matplotlib.colors import LinearSegmentedColormap
import os

def get_ranks(company_name=None, run=None):
    if run is None:
        path = cfg.PATH.SDG_OUTPUT_AGGREGATED
    else:
        path = run['path']
    # import company_dict_q3.txt as a file from cfg.PATH.SDG_OUTPUT_AGGREGATED
    with open(path + '/company_dict_q3.txt', 'r') as f:
        company_dict_q3 = eval(f.read())
    df_q3_rank = pd.DataFrame()
    for key in company_dict_q3.keys():
        temp_dict = company_dict_q3[key]
        temp_dict = {k: {k2: v2['rank'] for k2, v2 in v.items()} for k, v in temp_dict.items()}
        # make a dataframe from the dictionary
        temp_df = pd.DataFrame(temp_dict)
        # include the key in each column name
        temp_df.columns = [key + '_' + str(col) for col in temp_df.columns]
        # transpose the dataframe
        temp_df = temp_df.T
        # concatenate the dataframes
        df_q3_rank = pd.concat([df_q3_rank, temp_df], axis=0)
    
    df_q3_rank.index = df_q3_rank.index.str.split('_').map(lambda x: x[0])
    df_q3_rank.index = df_q3_rank.index.map(lambda x: company_website_to_name[x])
    if company_name is None: return df_q3_rank
    else: return df_q3_rank.loc[company_name]
    

def grid_graphic():
    # data for current run
    df_4 = get_ranks()
    df_4 = df_4.fillna(17).apply(lambda x: (18-x.astype(int))).groupby(level=0)
    q1 = df_4.quantile(0.25)
    q3 = df_4.quantile(0.75)
    iqr = q3 - q1
    # filter out values which are equal/greater 4 times the iqr
    result = df_4.apply(lambda x: x.where(iqr <= 4, 0))

    # PLOT
    # Define hex colors
    colors = ['#F8F8F8', '#DAEEF3', '#BAE0EA', '#77C5D8', '#449DC2', '#206A8A', '#0D4F6E', '#0A3C57', '#072A40']

    # Code for fund_1
    growth_result_dicts = result.loc[fund_1].groupby(level=0).median().apply(lambda x: {i: k for i, k in zip(x.index, x.values) if k > 1}, axis=1)
    growth_temp_min = []
    growth_temp_max = []

    for i in growth_result_dicts:
        if len(i) == 0:
            continue
        growth_temp_min.append(min(i.values()))
        growth_temp_max.append(max(i.values()))

    growth_temp_min = int(min(growth_temp_min)) 
    growth_temp_max = int(max(growth_temp_max)) 
    growth_N_colors = growth_temp_max - growth_temp_min + 1 + 1

    growth_data = result.loc[fund_1].groupby(level=0).median() 
    # set zero values to nan
    growth_data = growth_data.replace(1, np.nan)
    growth_data = growth_data.rank(axis=1, method='max', ascending=True) # False if scaled after
    growth_data = growth_data.fillna(0)
    # replace 1 with 4, 2 with 3, 3 with 2, 4 with 1
    # growth_data = growth_data.replace({1: 4, 2: 3, 3: 2, 4: 1})
    # sort by sum of columns
    growth_data = growth_data.loc[sorted(fund_1), growth_data.sum(axis=0).sort_values(ascending=False).index]

    # Code for fund_2
    carbon_result_dicts = result.loc[fund_2].groupby(level=0).median().apply(lambda x: {i: k for i, k in zip(x.index, x.values) if k > 1}, axis=1)
    carbon_temp_min = []
    carbon_temp_max = []

    for i in carbon_result_dicts:
        if len(i) == 0:
            continue
        carbon_temp_min.append(min(i.values()))
        carbon_temp_max.append(max(i.values()))

    carbon_temp_min = int(min(carbon_temp_min)) + 1
    carbon_temp_max = int(max(carbon_temp_max)) + 1
    carbon_N_colors = carbon_temp_max - carbon_temp_min + 1  # + 1

    carbon_data = result.loc[fund_2].groupby(level=0).median() #.apply(lambda x: x.where(x == 1, x - carbon_temp_min + 2)) - 1
    # set zero values to nan
    carbon_data = carbon_data.replace(1, np.nan)
    carbon_data = carbon_data.rank(axis=1, method='max', ascending=True) # False if scaled after
    carbon_data = carbon_data.fillna(0)
    # replace 1 with 4, 2 with 3, 3 with 2, 4 with 1
    # carbon_data = carbon_data.replace({1: 4, 2: 3, 3: 2, 4: 1})
    # sort by sum of columns
    carbon_data = carbon_data.loc[sorted(fund_2), carbon_data.sum(axis=0).sort_values(ascending=False).index]

    # Set up subplots
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))

    # Generate growth fund heatmap
    growth_cmap_name = 'custom_colormap'
    growth_cm = LinearSegmentedColormap.from_list(growth_cmap_name, colors, N=(growth_N_colors+1))
    # growth_cm = LinearSegmentedColormap.from_list(growth_cmap_name, colors, N=len(colors))  # Use len(colors) for number of colors

    growth_ticks = np.arange(np.min(growth_data), np.max(growth_data) + 1)  # Generate ticks
    heatmap_growth = axs[0].imshow(growth_data, cmap=growth_cm, vmin=np.min(growth_data) - 0.5, vmax=np.max(growth_data) + 0.5)
    cbar_growth = fig.colorbar(heatmap_growth, ax=axs[0], ticks=growth_ticks, label='Score')  # Use specified ticks
    cbar_growth.set_ticklabels(growth_ticks)  # Set tick labels

    axs[0].set_xticks(np.arange(len(growth_data.columns)))
    axs[0].set_xticklabels(growth_data.columns, rotation=90)
    axs[0].set_yticks(range(len(growth_data.index)))
    axs[0].set_yticklabels(growth_data.index)
    axs[0].set_xlabel('SDGs')
    axs[0].set_ylabel('Companies')

    # Generate carbon fund heatmap
    carbon_cmap_name = 'custom_colormap'
    # carbon_cm = LinearSegmentedColormap.from_list(carbon_cmap_name, colors, N=carbon_N_colors)
    carbon_cm = LinearSegmentedColormap.from_list(carbon_cmap_name, colors, N=len(colors))  # Use len(colors) for number of colors

    carbon_ticks = np.arange(np.min(carbon_data), np.max(carbon_data) + 1)  # Generate ticks
    heatmap_carbon = axs[1].imshow(carbon_data, cmap=carbon_cm, vmin=np.min(carbon_data) - 0.5, vmax=np.max(carbon_data) + 0.5)
    cbar_carbon = fig.colorbar(heatmap_carbon, ax=axs[1], ticks=carbon_ticks, label='Score')  # Use specified ticks
    cbar_carbon.set_ticklabels(carbon_ticks)  # Set tick labels

    axs[1].set_xticks(range(len(carbon_data.columns)))
    axs[1].set_xticklabels(carbon_data.columns, rotation=90)
    axs[1].set_yticks(range(len(carbon_data.index)))
    axs[1].set_yticklabels(carbon_data.index)
    axs[1].set_xlabel('SDGs')
    axs[1].set_ylabel('Companies')

    # add title Carbon Fund on top of first heatmap
    axs[0].set_title('Growth Fund')
    axs[1].set_title('Carbon Fund')

    for position in np.arange(.5, len(growth_data.columns), 1):
        axs[0].axvline(x=position, color='gray', linestyle='--', linewidth=0.2)
        axs[1].axvline(x=position, color='gray', linestyle='--', linewidth=0.2)

    for position in np.arange(.5, len(growth_data.index), 1):
        axs[0].axhline(y=position, color='gray', linestyle='--', linewidth=0.2)
        if position < 10: axs[1].axhline(y=position, color='gray', linestyle='--', linewidth=0.2)

    plt.tight_layout()

    # Save the figure
    fig.savefig(os.path.join(cfg.PATH.OUTPUT_PLOT, 'grid_graphic.png'), dpi=300, bbox_inches='tight')
