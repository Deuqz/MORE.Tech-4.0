from app.source import track_repository
from dateutil.parser import parse
import datetime
import numpy as np
from sklearn.cluster import KMeans


def analyze(role: str):
    df_core = track_repository.get_datasets(role)

    target_date = datetime.datetime.now()

    for i, row in df_core.iterrows():
        ds = (target_date - parse(row['date'])).days
        if ds > 365 or ds < 0:
            df_core = df_core.drop(i)

    berk_vecs = df_core['vectorized_text']

    kmeans = KMeans(n_clusters=10, random_state=0).fit(berk_vecs)
    clusters_nums = kmeans.predict(berk_vecs)

    uniq_clusters_nums = np.unique(clusters_nums)
    clusters = [[] for i in range(len(uniq_clusters_nums))]
    for i, num in enumerate(clusters_nums):
        if num != -1:
            clusters[num].append(df_core.index[i])

    start_date_temp = datetime.date.today() - datetime.timedelta(days=365)
    start_date = datetime.datetime(start_date_temp.year, start_date_temp.month, start_date_temp.day)
    term = 366

    functions = []
    for cltr in clusters:
        dates = df_core.loc[cltr]['date']
        views = df_core.loc[cltr]['views']
        y = [[] for _ in range(term)]
        for d, v in zip(dates, views):
            dd = parse(d)
            y[(dd - start_date).days].append(v)
        to_delete = []
        x = []
        for i, lst in enumerate(y):
            if lst:
                x.append(i)
                y[i] = np.array(lst).mean()
            else:
                to_delete.append(i)
        to_delete.reverse()
        for i in to_delete:
            del y[i]
        fit = np.polyfit(x, y, deg=2)
        fit_function = np.poly1d(fit)
        other_y = fit_function(x)
        functions.append(other_y)

    trends_cltr_ids = []
    mean_val = np.array([f[-1] for f in functions]).mean()
    for i, f in enumerate(functions):
        if np.gradient(f)[-1] > 0 and f[-1] > mean_val:
            trends_cltr_ids.append(i)

    trends_ids = [clusters[i] for i in trends_cltr_ids]
    all_trends = [df_core.loc[ids] for ids in trends_ids]

    result_trends = []
    for trend in all_trends:
        if len(trend) < 5:
            continue
        last_date = parse(trend['date'].values[0])
        last_ind = trend.index[0]
        max_views = trend['views'].values[0]
        max_ind = trend.index[0]
        max2_views = trend['views'].values[0]
        max2_ind = trend.index[0]
        for i, n in trend.iterrows():
            d = parse(n['date'])
            if d > last_date:
                last_date = d
                last_ind = i
            v = n['views']
            if v > max_views:
                max2_views = max_views
                max2_ind = max_ind
                max_views = v
                max_ind = i
            elif v > max2_views:
                max2_views = v
                max2_ind = i
        ids = list({max_ind, max2_ind, last_ind})
        result_trends.append([(n[0], n[1]) for n in trend[['header', 'link']].loc[ids].values])

    return result_trends
