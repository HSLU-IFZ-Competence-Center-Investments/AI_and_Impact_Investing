import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
# from configs.misc_config import cfg # only if run alone
from CODE.configs.__config import cfg
# from utils.datamanager import * # only if run alone
# from utils.plotter import plotter # only if run alone
from CODE.utils.datamanager import fund_1, fund_2
# from utils.datamanager import fund_1, fund_2, company_website_to_name
from matplotlib.colors import LinearSegmentedColormap
import os


colors = ['#F8F8F8', '#DAEEF3', '#BAE0EA', '#77C5D8', '#449DC2', '#206A8A', '#0D4F6E', '#0A3C57', '#072A40']


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
    
    # print(df_q3_rank.index)
    df_q3_rank.index = df_q3_rank.index.str.split('_').map(lambda x: x[0])
    # print(df_q3_rank.index)
    # df_q3_rank.index = df_q3_rank.index.map(lambda x: company_website_to_name[x]) # not needed if Company names are already in index
    # print(df_q3_rank.index)
    if company_name is None: return df_q3_rank
    else: return df_q3_rank.loc[company_name]
    
def _grid_graphic(result,fund_names:list[str],fig,ax):

    _data = result.loc[fund_names].groupby(level=0).median()
    # set zero values to nan
    _data = _data.replace(0, np.nan)
    _data = _data.rank(axis=1, method='max', ascending=True) # False if scaled after
    _data = _data.fillna(0)
    _data = _data.loc[sorted(fund_names), _data.sum(axis=0).sort_values(ascending=False).index]

    # Code for fund_names
    _result_dicts = _data.groupby(level=0).median().apply(lambda x: {i: k for i, k in zip(x.index, x.values) if k > 0}, axis=1)
    _temp_min = []
    _temp_max = []

    for i in _result_dicts:
        if len(i) == 0:
            continue
        _temp_min.append(min(i.values()))
        _temp_max.append(max(i.values()))

    _temp_min = int(min(_temp_min)) 
    _temp_max = int(max(_temp_max)) 
    _N_colors = _temp_max - _temp_min + 1 + 1

    _cmap_name = 'custom_colormap'
    _cm = LinearSegmentedColormap.from_list(_cmap_name, colors, N=_N_colors)

    _ticks = np.array(list(set(_data.apply(pd.unique).apply(list).sum()))) # Generate ticks

    # dummy_range = np.arange(0, len(_ticks), 1)
    dummy_data = _data.replace(0,_temp_min-1)
    dummy_ticks = np.array(list(set(dummy_data.apply(pd.unique).apply(list).sum()))) 
    heatmap = ax.imshow(_data, cmap=_cm, vmin=np.min(dummy_data) - 0.5, vmax=np.max(dummy_data) + 0.5)
    cbar= fig.colorbar(heatmap, ax=ax, ticks=dummy_ticks, label='Score')  # Use specified ticks
    _tick_labels = _ticks + 17 - _ticks.max()
    _tick_labels = [0] + _tick_labels.astype(int).tolist()[1:]
    cbar.set_ticklabels(_tick_labels)  # Set tick labels0

    ax.set_xticks(np.arange(len(_data.columns)))
    ax.set_xticklabels(_data.columns, rotation=90)
    ax.set_yticks(range(len(_data.index)))
    ax.set_yticklabels(_data.index)
    ax.set_xlabel('SDGs')
    ax.set_ylabel('Companies')

    for position in np.arange(.5, len(_data.columns), 1):
        ax.axvline(x=position, color='gray', linestyle='--', linewidth=0.2)

    for position in np.arange(.5, len(_data.index), 1):
        ax.axhline(y=position, color='gray', linestyle='--', linewidth=0.2)

def grid_graphic():

    # PLOT
    # Define hex colors
    # data for current run
    df_4 = get_ranks()
    df_4 = df_4.fillna(18).apply(lambda x: (18-x.astype(int))).groupby(level=0)
    q1 = df_4.quantile(0.25)
    q3 = df_4.quantile(0.75)
    iqr = q3 - q1
    # filter out values which are equal/greater 4 times the iqr
    result = df_4.apply(lambda x: x.where(iqr <= 4, 0))

    # make 2 axes
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))

    for i, fund in enumerate([fund_1, fund_2]):
        _grid_graphic(result, fund, fig, axs[i])


    plt.tight_layout()

    # Save the figure
    # if folder does not exist, create it
    if not os.path.exists(cfg.PATH.OUTPUT_PLOT):
        os.makedirs(cfg.PATH.OUTPUT_PLOT)
    # fig.savefig(os.path.join(cfg.PATH.OUTPUT_PLOT, 'grid_graphic_{}.png'), dpi=300, bbox_inches='tight')

    plt.show()


if __name__ == "__main__":
    grid_graphic()
