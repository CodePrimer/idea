# coding=utf-8
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

if __name__ == "__main__":

    plt.figure(figsize=(16, 8))
    map = Basemap()
    map.drawcoaslines()

    print("Finish.")
