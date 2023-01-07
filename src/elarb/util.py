import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def pivot_to_hm(df):
    dates = sorted(df.dt.unique())
    df_hm = pd.DataFrame(index=sorted(df.h.unique()))
    for date in dates:
        dt_col = pd.to_datetime(date).date().isoformat().replace('-', '_')
        df_sub = df[df.dt == date].set_index('h').SpotPriceDKK.to_frame(dt_col)
        df_sub[dt_col] = df_sub[dt_col] / 1000.0
        df_hm = df_hm.join(df_sub)
    return df_hm


def spot_heatmap(df, annot=True):
    df_plot = pivot_to_hm(df)
    sns.heatmap(df_plot, annot=annot, cmap='RdYlGn_r', fmt='.3g')
    plt.show()
