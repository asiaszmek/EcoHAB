import os
import numpy as np
from numba import jit
from write_to_file import save_single_histograms, write_csv_rasters
from plotfunctions import single_in_cohort_soc_plot, make_RasterPlot, single_heat_map

def check_directory(directory,subdirectory):
    new_path = os.path.join(directory, subdirectory)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path


def results_path(path):
    head, tail = os.path.split(path)
    if tail == '':
        head, tail = os.path.split(head)
    head, tail2 = os.path.split(head)
    head = os.path.join(head, 'Results_'+tail2)
    return os.path.join(head, tail, 'Results')


def make_figure(title):
    fig = plt.figure(figsize=(12,12))
    ax = fig.add_subplot(111, aspect='equal')
    fig.suptitle('%s'%(title), fontsize=14, fontweight='bold')
    return fig, ax


def make_prefix(path):
    """
    Read-in info.txt and make a prefix for all files for results.
    Parameters
    ----------
    path: str
    """
    key_list = [
        'genotype',
        'sex',
        'type of experiment',
        'date of experiment',
        'social odor',
        'no social odor',
    ]

    fname = os.path.join(path, 'info.txt')

    try:
        f = open(fname)
    except IOError:
        return ''

    info_dict = {}
    for line in f:
        try:
            key, info = line.split(':')
        except ValueError:
            continue
        info = info.strip()
        info = info.replace(' ', '_')
        info_dict[key] = info
    prefix = ''
    for key in key_list:
        if key not in info_dict:
            continue
        if key == 'social odor' or key == 'non-social odor':
            if info_dict[key] == 'none' or info_dict[key] == 'None':
                key = key.replace(' ', '_')
                prefix += '_no_' + key.replace(' ', '_') + '_'
            else:
                prefix += key.replace(' ', '_') + '_' + info_dict[key] + '_'
        else:
            prefix += info_dict[key] + '_'
    return prefix


def list_of_pairs(mice):
    pair_labels = []
    for j, mouse in enumerate(mice):
        for k in range(j+1, len(mice)):
            pair_labels.append(mice[j]+'|'+mice[k])
    return pair_labels


def filter_dark(phases):
    out = []
    for phase in phases:
        if phase.endswith('dark'):
            out.append(phase)
        elif phase.endswith('DARK'):
            out.append(phase)
        elif phase.endswith('Dark'):
            out.append(phase)
    return out


def filter_light(phases):
    out = []
    for phase in phases:
        if phase.endswith('light'):
            out.append(phase)
        elif phase.endswith('LIGHT'):
            out.append(phase)
        elif phase.endswith('Light'):
            out.append(phase)
    return out


def filter_dark_light(phases):
    out = []
    for phase in phases:
        if phase.endswith('dark'):
            out.append(phase)
        elif phase.endswith('DARK'):
            out.append(phase)
        elif phase.endswith('Dark'):
            out.append(phase)
        elif phase.endswith('light'):
            out.append(phase)
        elif phase.endswith('LIGHT'):
            out.append(phase)
        elif phase.endswith('Light'):
            out.append(phase)

    return out


def add_info_mice_filename(remove_mouse):
    add_info_mice = ''
    if isinstance(remove_mouse, list):
        add_info_mice = 'remove'
        for mouse in remove_mouse:
            add_info_mice += '_' + mouse 
    elif isinstance(remove_mouse, str):
        add_info_mice = 'remove_%s' % remove_mouse
    return add_info_mice

def get_idx_pre(t0, times):
    idxs = np.where(np.array(times) < t0)[0]
    if len(idxs):
        return idxs[-1]
    return None

def get_idx_between(t0, t1, times):
    return  np.where((np.array(times) >= t0) & (np.array(times) <= t1))[0]

def get_idx_post(t1, times):
    idxs = np.where(np.array(times) > t1)[0]
    if len(idxs):
        return idxs[0]
    return None


def in_tube(antenna, next_antenna):
    if antenna % 2:
        if next_antenna  == antenna  + 1:
            return True
    else:
        if next_antenna == antenna - 1:
            return True
    return False


def in_chamber(antenna, next_antenna):
    antenna = antenna % 8
    next_antenna = next_antenna % 8
    if antenna % 2:
        if next_antenna  == antenna - 1:
            return True
    else:
        if next_antenna == antenna + 1:
            return True
    return False


def change_state(antennas):
    return np.where(abs(np.array(antennas[:-1]) - np.array(antennas[1:])) !=0)[0]

def mouse_going_forward(antennas):
    assert len(antennas) > 2
    first_antenna, last_antenna = antennas[0], antennas[-1]
    if first_antenna % 2 and last_antenna % 2:
        return True
    if not first_antenna % 2 and not last_antenna % 2:
        return True
    return False
    
def mouse_backing_off(antennas):
    first_antenna, last_antenna = antennas[0], antennas[-1]
    how_many = len(set(antennas))
    if how_many == 3:
        if first_antenna % 2 and not last_antenna % 2:
            return True
        if not first_antenna % 2 and last_antenna % 2:
            return True
        return False

    if first_antenna == last_antenna and len(antennas) > 2:
        return True
    return False

def skipped_antennas(antennas):
    change = abs(np.array(antennas[:-1]) - np.array(antennas[1:]))
    if len(np.intersect1d(np.where(change>=2)[0], np.where(change<=6)[0])):
        return True
    return False

    
def change_seven_to_one(change):
    if isinstance(change, list):
        change = np.array(change)
    seven = np.where(change == 7)[0]
    if len(seven):
        change[seven] = -1
    minus_seven = np.where(change == -7)[0]
    if len(minus_seven):
        change[minus_seven] = 1
    return change


def mouse_going_clockwise(antennas):
    change = np.array(antennas[:-1]) - np.array(antennas[1:])
    change = change_seven_to_one(change)
    if sum(change) < 0:
        return True
    return False


def mouse_going_counterclockwise(antennas):
    change = np.array(antennas[:-1]) - np.array(antennas[1:])
    change = change_seven_to_one(change)
    if sum(change) > 0:
        return True
    return False


def get_times_antennas(ehd, mouse, t_1, t_2):
    ehd.mask_data(t_1, t_2)
    antennas, times = ehd.getantennas(mouse), ehd.gettimes(mouse)
    ehd.unmask_data()
    return times, antennas

@jit
def get_states_and_readouts(antennas, times, t1, t2):
    before = get_idx_pre(t1, times)
    between = get_idx_between(t1, t2, times)
    after = get_idx_post(t2, times)
    states = []
    readouts = []
    if before is not None:
        states.append(antennas[before])
        readouts.append(times[before])
    for idx in between:
        states.append(antennas[idx])
        readouts.append(times[idx])
    assert(len(states) == len(readouts))
    return states, readouts

@jit
def get_more_states(antennas, times, midx,
                    mouse_attention_span,
                    how_many_antennas):
    #save first antenna
    states = [antennas[midx]]
    readouts = [times[midx]]
    midx += 1
    idx = 1
    while True:
        if midx >= len(antennas):
            break
        #read in next antenna
        new_antenna = antennas[midx]
        new_readout = times[midx]
        #if pause too long break
        if new_readout > readouts[idx - 1] + mouse_attention_span:
            break

        states.append(new_antenna)
        readouts.append(new_readout)

        idx += 1
        #if more than 2 antennas, break
        if len(set(states)) == how_many_antennas:
            # go back to the last readout of the opposite antenna not to loose it
            break
        midx += 1
        
    return states, readouts, midx



def evaluate_whole_experiment(ehd, cf, main_directory, prefix, func, fname, xlabel, ylabel, title, remove_mouse=None, print_out=True):
    phases = cf.sections()
    phases = filter_dark(phases)
    mice = ehd.mice
    add_info_mice = add_info_mice_filename(remove_mouse)
    result = np.zeros((len(phases), len(mice), len(mice)))
    fname_ = '%s_%s%s.csv' % (fname, prefix, add_info_mice)
    hist_dir = fname + '/histograms'
    rast_dir = fname + '/raster_plots'
    for i, phase in enumerate(phases):
        result[i] = func(ehd, cf, phase, print_out=print_out)
        save_single_histograms(result[i],
                               fname,
                               mice,
                               phase,
                               main_directory,
                               hist_dir,
                               prefix,
                               additional_info=add_info_mice)
        single_heat_map(result[i],
                        fname,
                        main_directory,
                        mice,
                        prefix,
                        phase,
                        xlabel=xlabel,
                        ylabel=ylabel,
                        subdirectory=hist_dir,
                        vmax=None,
                        vmin=None,
                        xticks=mice,
                        yticks=mice)
    write_csv_rasters(mice,
                      phases,
                      result,
                      main_directory,
                      rast_dir,
                      fname_)
    make_RasterPlot(main_directory,
                    rast_dir,
                    result,
                    phases,
                    fname_,
                    mice,
                    title=title)
