""" The cluster_plot series of functions that plots all of the clustered stars and
    information. """
import scipy.stats as spy
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as pltc

def iqr_calc_angle(clustered_data, step, distcen, column):
    """ Calculated interquartile range of a cluster group and is scaled to distance
     from angle. """
    return spy.iqr(clustered_data.loc[clustered_data["clusternum"] == step,\
     [column]])*3.14159/180*distcen

def color_setup(clustered_data, membership_plot, unique_group, palette):
    """ If plotting a membership probability color map is wanted, the input dataframe must be
    separated into a different dataframe for each cluster.  Doing this with a dictionary
    is fast and efficient.  A second dictionary is made to set the color map for each cluster
    number.  If plotting membership probability is not needed, we instead set a unique color
    to each cluster and set non-clustered field stars to black. """
    import pandas as pd

    if membership_plot == 1:
        clustered_dict = {elem: pd.DataFrame for elem in unique_group}
        for key in clustered_dict.keys():
            clustered_dict[key] = clustered_data[:][clustered_data.clusternum == key]
        cmapdict = {-1:"Greys", 0:"Blues", 1:"Oranges", 2:"Greens", 3:"Reds",\
         4:"Purples", 5:"PuBu", 6:"YlGn", 7:"Greys", 8:"Purples", 9:"Blues",\
          10:"Greens", 11:"Reds", 12:"Oranges", 13:"PuBu", 14:"YlGn", 15:"Greys"}
        return clustered_dict, cmapdict
    return [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in clustered_data["clusternum"]]

def distance_hist(clustered_data, distcen, step, palette):
    """ A subplot illustrating the cluster distance histogram.  Additionally, the median
    cluster distance and distance IQR are plotted. IQR is preferred for potentially
    non-normally distributed data."""
    plt.subplot(223)
    plt.xlabel("Distance (pc)", fontsize=15)
    plt.ylabel("Number", fontsize=15)
    plt.xlim(distcen-250, distcen+250)
    bins = np.linspace(distcen-300, distcen+300, 30)
    memberdist = clustered_data[clustered_data["clusternum"] == step]["distance"]
    pmdistiqr = spy.iqr(clustered_data.loc[clustered_data["clusternum"] == step, ["distance"]])
    plt.hist(memberdist, bins, alpha=0.5, color=palette[step])
    plt.gcf().text(0.09, 0.43, "Distance = "+str(int(distcen))+" pc", fontsize=12)
    plt.gcf().text(0.32, 0.43, "Distance IQR = "+str(int(pmdistiqr))+" pc", fontsize=12)


def ra_dec_plot_setup(clustered_data, distcen, step):
    """ A subplot illustrating the cluster scaled RA and DEC is setup.  The median cluster
    RA and DEC and their IQR in pc space are plotted.  """
    plt.subplot(222)
    plt.ylabel("DEC", fontsize=15)
    plt.xlabel("RA Scaled", fontsize=15)
    ramin = min(clustered_data["ratransform"])
    ramax = max(clustered_data["ratransform"])
    decmin = min(clustered_data["dec"])
    decmax = max(clustered_data["dec"])
    raiqr = iqr_calc_angle(clustered_data, step, distcen, "ratransform")
    ramedian = np.median(clustered_data.loc[clustered_data["clusternum"] == step, ["ra"]])

    # The texts are placed in data space, which pushes them outside the plot and automatically
    # rescales the plot positions to make space for the text.
    plt.text(ramin, decmax+(decmax-decmin)*0.16, "RA = "+str(round(ramedian, 3)), fontsize=12)
    plt.text(ramin+(ramax-ramin)*0.6, decmax+(decmax-decmin)*0.16, "RA IQR =\
     "+str(round(raiqr, 2))+" pc", fontsize=12)
    decmedian = np.median(clustered_data.loc[clustered_data["clusternum"] == step, ["dec"]])
    deciqr = iqr_calc_angle(clustered_data, step, distcen, "dec")
    plt.text(ramin, decmax+(decmax-decmin)*0.08, "DEC = "+str(round(decmedian, 3)), fontsize=12)
    plt.text(ramin+(ramax-ramin)*0.6, decmax+(decmax-decmin)*0.08, "DEC IQR =\
     "+str(round(deciqr, 2))+" pc", fontsize=12)

def pm_plot_setup(clustered_data, pmraiqr, pmdeciqr, step):
    """ A subplot illustrating the cluster proper motions is setup.  Additionally, the
    median cluster RA PM and DEC PM (in mas/yr) and their IQR (in km/s) space are plotted. """
    plt.subplot(221)
    plt.ylabel("DEC PM (mas/yr)", fontsize=15)
    plt.xlabel("RA PM (mas/yr)", fontsize=15)
    pmramedian = np.median(clustered_data.loc[clustered_data["clusternum"] == step, ["pmra"]])
    pmdecmedian = np.median(clustered_data.loc[clustered_data["clusternum"] == step, ["pmdec"]])
    plt.gcf().text(0.08, 0.978, "RA PM = "+str(round(pmramedian, 2))+" mas/yr", fontsize=12)
    plt.gcf().text(0.08, 0.948, "DEC PM = "+str(round(pmdecmedian, 2))+" mas/yr", fontsize=12)
    plt.gcf().text(0.28, 0.978, "RA PM IQR = "+str(round(pmraiqr, 2))+" km/s", fontsize=12)
    plt.gcf().text(0.28, 0.948, "DEC PM IQR = "+str(round(pmdeciqr, 2))+" km/s", fontsize=12)
    # We do not want to plot the entire PM space, and zoom to around +/- 10 mas/yr on both
    # axis centered on the cluster median.
    plt.ylim(pmdecmedian-10, pmdecmedian+10)
    plt.xlim(pmramedian-10, pmramedian+10)

def cmd_plot_setup(clustered_data, step):
    """ A subplot illustrating the cluster CMD is setup."""
    plt.subplot(224)
    plt.xlabel("BP-RP", fontsize=15)
    plt.ylabel("M$_{\mathrm{G}}$", fontsize=15)
    ymin = min(clustered_data["M_G"])
    ymax = max(clustered_data["M_G"])
    plt.ylim(ymax, ymin-1)
    plt.xlim(-0.6, 3.5)
    return len(clustered_data.loc[clustered_data["clusternum"] == step]), ymin

def plot_map(unique_group, clustered_dict, cmapdict, normalize, step, xvar_col, yvar_col):
    """ For when a membership probability color map is desired (i.e., membership_plot == 1).
    This function plots each cluster separately with its own separate color map, while
    it plots non-clustered data as simply black."""
    for group in unique_group:
        if group == -1:
            plt.scatter(clustered_dict[group][xvar_col], clustered_dict[group][yvar_col], s=0.005,\
             alpha=1, color="black")
        elif group == step:
            plt.scatter(clustered_dict[group][xvar_col], clustered_dict[group][yvar_col], s=6,\
             alpha=1, c=clustered_dict[group]["clusterprob"], cmap=cmapdict[group], norm=normalize)
            cbar = plt.colorbar()
            cbar.set_label('Membership Probability')
        else:
            plt.scatter(clustered_dict[group][xvar_col], clustered_dict[group][yvar_col], s=0.02,\
             alpha=1, c=clustered_dict[group]["clusterprob"], cmap=cmapdict[group], norm=normalize)

def cluster_plot(clustered_data, membership_plot):
    """ This main function sets up the colors, figures, and plots the data based on the
    requested membership or not color scheme. """

# We count the number of found clusters, set up the color palette, and set tick label
# font size to 12 for clarity.
    unique_group = clustered_data.clusternum.unique()
    palette = sns.color_palette('bright', max(unique_group)+1)
    if membership_plot == 1:
        clustered_dict, cmapdict = color_setup(clustered_data, membership_plot,\
         unique_group, palette)
    else:
        colors = color_setup(clustered_data, membership_plot, unique_group, palette)
    normalize = pltc.Normalize(vmin=0, vmax=1)
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

# This loop iterates through all clustered groups found with hdbscan and plots the
# requested clusters that pass the checks.
    for step in range(max(unique_group)+1):

# The median stellar distance is found (in parsecs), which is used to transform proper
# motions and RA and DEC into spatial scales.  Because these distributions are not
# always Gaussian, the interquartile ranges are used to analyze parameter variations
# throughout a cluster.
        distcen = np.median(clustered_data.loc[clustered_data["clusternum"] == step, ["distance"]])
        pmraiqr = iqr_calc_angle(clustered_data, step, distcen, "pmra")*0.271795
        pmdeciqr = iqr_calc_angle(clustered_data, step, distcen, "pmdec")*0.271795

# Hdbscan will typically create a cluster from the overdensity in the field disk stars,
# producing apparent clusters but with large PM variation.  Therefore, we require that
# the transformed PM variation be less than 3 km/s in each axis to be displayed as a
# valid cluster.  If a legitimate cluster is identified but retains a lot of
# noise/non-members, a 3 km/s cut may remove it from display.  In these cases, you may
# increase the cut to 4 or 5 km/s, etc., to first analyze its output, but in the end I
# recommend adjusting the hdbscan min_samples or the parameter scalings.
        if (pmraiqr < 3 and pmdeciqr < 3):

# To set up the plots, we set a separate Figure for each cluster.  For when membership
# probability is not shown, we set all clustered data to a large size and nonclustered
# data to small data size.
            plt.figure(step, figsize=(14, 10))
            if membership_plot != 1:
                sizes = [4 if x == step else 0.003 for x in clustered_data["clusternum"]]

            distance_hist(clustered_data, distcen, step, palette)
            ra_dec_plot_setup(clustered_data, distcen, step)
            if membership_plot == 1:
                plot_map(unique_group, clustered_dict, cmapdict, normalize, step,\
                 "ratransform", "dec")
            else:
                plt.scatter(clustered_data["ratransform"], clustered_data["dec"],\
                 s=sizes, alpha=1, color=colors)
            pm_plot_setup(clustered_data, pmraiqr, pmdeciqr, step)
            if membership_plot == 1:
                plot_map(unique_group, clustered_dict, cmapdict, normalize, step, "pmra", "pmdec")
            else:
                plt.scatter(clustered_data["pmra"], clustered_data["pmdec"], s=sizes,\
                 alpha=1, color=colors)
            number, ymin = cmd_plot_setup(clustered_data, step)
            if membership_plot == 1:
                xlabelpos = 1.57
                plot_map(unique_group, clustered_dict, cmapdict, normalize, step, "bp_rp", "M_G")
            else:
                xlabelpos = 1.95
                plt.scatter(clustered_data["bp_rp"], clustered_data["M_G"], s=sizes,\
                 alpha=1, color=colors)
            plt.text(xlabelpos, ymin+0.5, "Cluster Number "+str(step), fontsize=12)
            plt.text(xlabelpos, ymin+1.68, "Cluster Count = "+str(number), fontsize=12)
            plt.tight_layout()

    plt.show()
    