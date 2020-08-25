import numpy as np
import pylab
import matplotlib

if __name__ == '__main__':
    fig = pylab.figure(figsize=(3, 8))
    cmap = matplotlib.cm.Spectral_r
    ax3 = fig.add_axes([0.3, 0.2, 0.2, 0.5])  # 四个参数分别是左、下、宽、长
    norm = matplotlib.colors.Normalize(vmin=1.3, vmax=2.5)
    bounds = [round(elem, 2) for elem in np.linspace(1.3, 2.5, 14)]  #
    cb3 = matplotlib.colorbar.ColorbarBase(ax3, cmap=cmap, norm=norm, boundaries=[1.2] + bounds + [2.6], extend='both',
                                           ticks=bounds, spacing='proportional', orientation='vertical')
    # Colors = (
    # '#DDDDFF', '#7D7DFF', '#0000C6', '#000079', '#CEFFCE', '#28FF28', '#007500', '#FFFF93', '#8C8C00', '#FFB5B5',
    # '#FF0000', '#CE0000', '#750000')
    # cs = m.contourf(xi, yi, z, colors=Colors, levels=levels, extend='both')  # 这里m是一个basemap实例

    pylab.show()