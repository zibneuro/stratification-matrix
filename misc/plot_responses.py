import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

Q1_demoVideo = [
    4,
    5,
    4,
    5,
    5,
    4,
    5,
    5,
    5,
    4,
    5,
    4,
    5,
    5]

Q2_easeOfUse = [
    5,
    5,
    5,
    5,
    4,
    5,
    5,
    5]

Q3_toolbox = [
    4,
    4,
    4,
    5,
    5,
    5,
    4,
    4]

Q5_easierExploreDownload = [
    4,
    5,
    4,
    5,
    3,
    3,
    4,
    4,
    5,
    5,
    5,
    4,
    4,
    5]


Q6_easierCommunicate = [
    3,
    3,
    4,
    5,
    4,
    3,
    5,
    5,
    4,
    4,
    5,
    4,
    4,
    4]

Q7_ownResearch = [
    5,
    5,
    4,
    4,
    1,
    3,
    2,
    4,
    1,
    1,
    4,
    1,
    1,
    5]

if __name__ == "__main__":

    mpl.rcParams["axes.spines.top"] = False
    mpl.rcParams["axes.spines.right"] = False
    #mpl.rcParams["axes.labelsize"] = "medium"
    #mpl.rcParams["xtick.labelsize"] = "small"
    #mpl.rcParams["ytick.labelsize"] = "small"
    #mpl.rcParams["legend.frameon"] = False

    #mpl.rcParams["legend.fontsize"] = 10
    #mpl.rcParams["font.size"] = 10
    #mpl.rcParams["figure.max_open_warning"] = 0
    #mpl.rcParams.update({'font.family': 'sans-serif'})    

    questions = [Q1_demoVideo, Q2_easeOfUse, Q3_toolbox, Q5_easierExploreDownload, Q6_easierCommunicate, Q7_ownResearch]
    for responses in questions:
        print(len(responses))

    x = np.arange(1,len(questions)+1)
    print(x)

    jitter_x = 0.2
    jitter_y = 0.2
    annotationOffset_x = 0.7 * jitter_x
    annotationOffset_y = 0
    
    plt.figure(figsize=(5,2.5))
    for responseVals in [1,2,3,4,5]:
        plt.axhline(y=responseVals, color='lightgrey', linestyle='-', linewidth=0.8, zorder=-1)
    for k in range(0, len(questions)):
        plt.axvline(x=k+1, color='lightgrey', linestyle='-', linewidth=0.8, zorder=-1)
        responses = np.array(questions[k])                
        x_i = x[k] + (-0.5 * jitter_x) + jitter_x * np.random.random(responses.size)
        y_i = responses + (-0.5 * jitter_y) + jitter_y * np.random.random(responses.size)
        plt.scatter(x_i, y_i, c="blue", marker=".", s=17)    
        y_unique, counts_unqiue = np.unique(responses, return_counts=True)
        for j in range(0,y_unique.size):
            plt.text(x[k]+annotationOffset_x, y_unique[j]+annotationOffset_y, str(counts_unqiue[j]), fontsize=8, c="blue")
    plt.xticks(x, ["Q1", "Q2", "Q3", "Q5", "Q6", "Q7"])
    plt.yticks([1,2,3,4,5], [r"$--1$", r"$-2$", r"$3$", r"$+4$", r"$++5$"])
    plt.xlim(0.5,len(questions)+0.5)
    plt.savefig("responses.png", dpi=300)
    