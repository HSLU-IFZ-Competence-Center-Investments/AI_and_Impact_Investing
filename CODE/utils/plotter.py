# Author: Ahmet Ege Yilmaz
# Year: 2020
# Title: Matplotlib based framework to create plots
# Documentation: https://github.com/Quantumyilmaz/Plotter

from matplotlib import pyplot as plt
from matplotlib import rcParams
import matplotlib.table as tbl
import numpy as np
from matplotlib.lines import Line2D
from tqdm import tqdm
import matplotlib.dates as mdates

# rcParams["font.family"] = 'Baskerville'
DPI = 200
#plot_indexten buraya axis gelsin sirayla for loopta yap

def plotter(arg_list, attribute_list,**kwargs):

    plot_count = len(arg_list)
    ncols= kwargs.get('ncols',2)
    nrows = int(np.ceil(plot_count/ncols))
    nlastrow = plot_count%ncols
    dpi= kwargs.get('dpi') if kwargs.get('dpi') else DPI

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols,figsize=kwargs.get("figsize",(20+kwargs.get('xpad',0), 6*nrows+kwargs.get('ypad',0)))
                                                    ,gridspec_kw={'height_ratios':[1]*nrows,'width_ratios': [1]*ncols})
    fig.dpi = dpi
    if nlastrow and nrows>1:
        width = 1/(nlastrow+1)
        space = 0.5*(1/nlastrow - width)
        for i in ax[-1]:
            fig.delaxes(i)
        fig.add_axes([space,0,width,0.9/nrows])
        
            
    def get_axes(figure_axes=fig.axes,attribute_list=attribute_list,arg_list=arg_list,pipeline=1):
    
        for i, axis in tqdm(enumerate(figure_axes),total=len(figure_axes)):
            row_no = i//ncols+1
            col_no = i%ncols+1
            axis.plots_ = []
            if pipeline:
                if kwargs.get('second_plot',0):
                    ax2=fig.add_subplot(nrows,ncols,i+1, label=f"second_{row_no}{col_no}", frame_on=False)
                    ax2.xaxis.tick_top()
                    ax2.yaxis.tick_right()
                    ax2.xaxis.set_label_position('top') 
                    ax2.yaxis.set_label_position('right')
                    ax2.mother = axis
                else:
                    if not kwargs.get('keep_spines'):
                        axis.spines["top"].set_visible(False)
                        axis.spines["right"].set_visible(False)
                    axis.set_label(f"{row_no}{col_no}")
                    
                axes_linewidth = kwargs.get('axes_linewidth')
                if isinstance(axes_linewidth,(int,float)):
                    for spine in ['top','bottom','left','right']:
                        axis.spines[spine].set_linewidth(axes_linewidth)
                        if hasattr(axis,'twin'):
                            axis.twin.spines[spine].set_linewidth(width)
                elif isinstance(axes_linewidth,dict):
                    for spine,width in axes_linewidth.items():
                        axis.spines[spine].set_linewidth(width)
                        if hasattr(axis,'twin'):
                            axis.twin.spines[spine].set_linewidth(width)

                if kwargs.get('centered_y_axis'):
                    axis.spines['left'].set_position('center')
                if kwargs.get('centered_x_axis'):
                    axis.spines['bottom'].set_position('center')
            
            lines = []

            for attribute,arg in zip(attribute_list, arg_list[i]):

                if attribute[:4]=='2nd_':
                    assert kwargs.get('second_plot',0), "Please pass in keyword argument 'second_plot=1' to enable a second graph on the same subplot."
                    axis.second_plot_ = ax2
                    ax_helper(ax2,attribute[4:],arg,lines)
                elif attribute=='inset_axes':
                    inset_bounds,inset_methods,inset_args = arg.pop('bounds'),arg.pop('methods'),arg.pop('args')
                    inset_pipeline = 1 if not 'pipeline' in arg else arg.pop('pipeline')
                    axis.inset_ = axis.inset_axes(inset_bounds)
                    axis.inset_.outset_ = axis
                    axis.inset_.set_label(f"{row_no}{col_no}")
                    get_axes([axis.inset_],inset_methods,inset_args,pipeline=inset_pipeline)#,**arg)
                else:
                    ax_helper(axis,attribute,arg,lines)

    get_axes()
    fig_title = kwargs.get('fig_title','')
    fig.suptitle(fig_title, x=kwargs.get('suptitle_x',0.5),y=kwargs.get('suptitle_y',0.95),fontsize=kwargs.get('titlesize',25))
    
    if kwargs.get('hspace',0):
        plt.subplots_adjust(hspace=kwargs.get('hspace'))
    if kwargs.get('wspace',0):
        plt.subplots_adjust(hspace=kwargs.get('wspace'))
    
    save_path = kwargs.get('save_path')
    if save_path and len(save_path)>3:
        if save_path[-4]!='.':
            assert len(fig_title), "You are trying to save your plot but you have neither provided a save path nor a title for you plot."
            save_filename = '_'.join([i[i.index(' ')+1:] for i in fig_title.split('\n')])+'.jpg'
            if save_path[-1]!='/':
                save_path += '/' + save_filename
            else:
                save_path += save_filename
        elif save_path[-4]=='.':
            pass
        else:
            print('Could not save file.')

        fig.savefig(save_path, dpi=dpi,bbox_inches='tight')
        # print('File saved to ' + save_path)
    
    if kwargs.get('show',0):
        plt.show()

    plt.close(fig)
    
    return fig

def make_labels(ax,x_or_y,prop):
    #labels = [round(i,10) for i in getattr(ax, f'get_{x_or_y}ticks')()]
    labels = getattr(ax, f'get_{x_or_y}ticks')().tolist()
    if isinstance(prop,dict):
        for key in prop:
            if key == "add":
                labels += prop[key]
                labels.sort()
                getattr(ax, f'set_{x_or_y}ticks')(labels)
            else:
                raise NotImplementedError
    else:
        if prop == 'absolute':
            # getattr(ax, f'set_{x_or_y}ticklabels')([*map(abs,labels)])
            getattr(ax, f'set_{x_or_y}ticks')(ticks=labels,labels=[*map(abs,np.round(labels,5))])
        else:
            raise NotImplementedError
        
def ax_helper(ax,attribute,arg,lines=[]):
    if arg is None:
        pass

    elif attribute.startswith('indicate_inset'):
        assert hasattr(ax,'inset_')
        if sum([isinstance(i,dict) for i in arg]):
            # print(ax.inset_,*arg[:-1],**arg[-1])
            connector_lines = None if not 'connector_lines' in arg[-1] else arg[-1].pop('connector_lines')
            ax.rectangle_patch_,ax.connector_lines_=getattr(ax, attribute)(*arg[:-1],**arg[-1],inset_ax=ax.inset_)
            if connector_lines:
                for select_,connector_line in zip(connector_lines,ax.connector_lines_):
                    connector_line.set_visible(select_)
        else:
            ax.rectangle_patch_,ax.connector_lines_=getattr(ax, attribute)(*arg,inset_ax=ax.inset_)
        

    elif attribute=='make_table':
        dictionary = arg[0]
        dictionary.update({'ax':ax})
        table = tbl.table(**dictionary)
        table.auto_set_font_size(False)
        if len(arg)>1:
            KEYS = list(arg[1].keys())
            if KEYS.count('text_props'):
                table_props = table.properties()
                table_cells = table_props['children']
                for cell in table_cells:
                    #cell.PAD = 0.01
                    for prop in arg[1]['text_props']:
                        getattr(cell.get_text(), prop)(*arg[1]['text_props'][prop])
            if KEYS.count('fontsize'):
                table.set_fontsize(arg[1]['fontsize'])
            if KEYS.count('row_scale') and KEYS.count('col_scale'):
                table.scale(arg[1]['col_scale'], arg[1]['row_scale'])
            if KEYS.count("alpha"):
                for cell in table._cells:
                    table._cells[cell].set_alpha(.5)
        ax.add_table(table)
        
    elif attribute=='make_twinx':
        assert isinstance(arg,dict), "Please make sure your list contains only a dictionary with attributes as keys and arguments as values, which must be lists or dictionaries."
        twin_ax = ax.twinx()
        ax.twin = twin_ax
        twin_ax.set_label("twinx_"+ax.get_label())
        for attr in arg.keys():
            ax_helper(twin_ax,attr,arg[attr])
        twin_ax.spines["top"].set_visible(False)
        twin_ax.spines["bottom"].set_visible(False)
        twin_ax.spines["left"].set_visible(False)
        
    elif attribute=='make_twiny':
        assert isinstance(arg,dict), "Please make sure your list contains only a dictionary with attributes as keys and arguments as values, which must be lists or dictionaries."
        twin_ax = ax.twiny()
        ax.twin = twin_ax
        twin_ax.set_label("twiny_"+ax.get_label())
        for attr in arg.keys():
            ax_helper(twin_ax,attr,arg[attr])
        twin_ax.spines["right"].set_visible(False)
        twin_ax.spines["bottom"].set_visible(False)
        twin_ax.spines["left"].set_visible(False)

        # twin_ax.set_xlabel(**arg['xlabel'])
        # twin_ax.set_xlim(ax.get_xlim())
        # twin_ax.set_xticks(arg['tick_locations'])
        # if list(arg.keys()).count('tick_function'):
        #     twin_ax.set_xticklabels(arg['tick_function'](arg['tick_locations']))
        # if list(arg.keys()).count('tick_params'):
        #     twin_ax.tick_params(**arg['tick_params'])

    elif attribute=='ticks':
        for i in arg.keys():
            make_labels(ax,i,arg[i])
    
    elif attribute=='color_ax':
        ax_label = ax.get_label()
        if ax_label.count('second_'):
            ax.mother.spines['top'].set_color(arg['color'])
            ax.mother.spines['right'].set_color(arg['color'])
        elif ax_label.count('twinx_'):
            ax.spines['right'].set_color(arg['color'])
        elif ax_label.count('twiny_'):
            ax.spines['top'].set_color(arg['color'])
        else:
            for spine in ax.spines.values():
                spine.set_color(arg['color'])
            # ax.spines['bottom'].set_color(arg['color'])
            # ax.spines['left'].set_color(arg['color'])
                                              
    elif attribute=='text':
        ax.text(*arg[0],**arg[1],transform=ax.transAxes)
    
    elif attribute=='set_alpha':
        ax.patch.set_alpha(arg[0])

    elif attribute.count("time_format"):
        assert len(arg) == 1
        formatter = arg[0]
        x_or_y = attribute.split('time_format')[-1]
        getattr(ax,f"{x_or_y}axis").set_major_formatter(mdates.DateFormatter(formatter))

    elif attribute == "legend":
        handles , labels = ax.get_legend_handles_labels()
        if hasattr(ax,'twin'):
            if ax.twin.get_legend() is None:
                twin_handles , twin_labels = ax.twin.get_legend_handles_labels()
                handles+=twin_handles
                labels+=twin_labels
        if hasattr(ax,'second_plot_'):
            if ax.second_plot_.get_legend() is None:
                second_plot_handles , second_plot_labels = ax.second_plot_.get_legend_handles_labels()
                handles+=second_plot_handles
                labels+=second_plot_labels
        if sum([isinstance(i,dict) for i in arg]):
            if list(arg[-1].keys()).count('line_order'):
                line_order = arg[-1].pop('line_order')
                line_order = [*map(lambda x: tuple([*map(lambda i: lines[i],x)]),line_order)]
                getattr(ax, attribute)(handles = line_order,**arg[-1])
            else:
                keyword_args_ = {i:k for i,k in arg[-1].items()}
                keyword_args_.update(dict(handles=handles,labels=labels))
                ax.legend(*arg[:-1],**keyword_args_)
        else:
            keyword_args_ = dict(handles=handles,labels=labels)
            ax.legend(*arg,**keyword_args_)


    elif sum([isinstance(i,dict) for i in arg]):
        if attribute =='plot' and list(arg[-1].keys()).count('fillstyle'):
            line_main, = getattr(ax, attribute)(*arg[:-1],**arg[-1])
            line = Line2D(*line_main.get_data(),linestyle=arg[-1]['ls'],color=arg[-1]['color'],fillstyle=arg[-1]['fillstyle'],marker=arg[-1]['marker'], markersize=20)
            lines.append(line)
        elif attribute =='legend' and list(arg[-1].keys()).count('line_order'):
            line_order = arg[-1].pop('line_order')
            line_order = [*map(lambda x: tuple([*map(lambda i: lines[i],x)]),line_order)]
            getattr(ax, attribute)(handles = line_order,**arg[-1])
        else:
            getattr(ax, attribute)(*arg[:-1],**arg[-1])
    else:
        getattr(ax, attribute)(*arg)

        
        
        