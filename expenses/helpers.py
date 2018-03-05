# HELPER FUNCTIONS
import pandas as pd
import numpy as np


def sqlalchemy_obj_to_dict(obj):
    d = {k: obj.__dict__[k] for k in ['id', 'item', 'cost', 'date_purchased', 'category', 'subcategory']}
    return d


def sqlalchemy_objects_to_dicts(objects_list):
    list_of_dicts = [sqlalchemy_obj_to_dict(obj) for obj in objects_list]
    return list_of_dicts


def create_df(user_expenses):
    df = pd.DataFrame(user_expenses)
    df.rename(columns={'date_purchased': 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_monthly_limit(current_user):
    monthly_limit = (
            current_user.food_limit +
            current_user.car_limit +
            current_user.entertainment_limit
    )
    return monthly_limit


def get_user_months(user_expenses):
    df = create_df(user_expenses)
    user_months = df['date'].sort_values().dt.strftime('%Y-%m').unique().tolist()
    return user_months


def get_show_last_x_months_default(session, number_user_months, default=3):
    if 'show_last_x_months' in session:
        if number_user_months < session['show_last_x_months']:
            return number_user_months
        else:
            return session['show_last_x_months']
    else:
        if number_user_months < default:
            return number_user_months
        else:
            return default


def build_results(user_expenses, session):

    # create df
    df = create_df(user_expenses)

    # determine selected option for show last x months
    user_months = get_user_months(user_expenses)
    show_last_x_months = get_show_last_x_months_default(session, len(user_months))

    # filter df to include only selected months
    show_months = user_months[-1 * show_last_x_months:]  # get list of months to show in chart
    df['yr_month'] = df['date'].dt.strftime('%Y-%m')  # create reference column
    df = df[df['yr_month'].isin(show_months)]  # get rows in date list (last 3 months)
    df.drop('yr_month', axis=1, inplace=True)  # drop reference column
    df = df.reset_index()  # reset index

    # construct pivot table
    pt = pd.pivot_table(
        data=df[['date', 'category', 'cost']],
        index=pd.Grouper(key='date', freq='M'),
        columns='category', values='cost', aggfunc=np.sum).round(2)
    pt.fillna('', inplace=True)
    index_data = pt.index.tolist()
    labels = [i.strftime('%b %Y') for i in index_data]

    # create data structure for chart
    data = [
        [category] + pt[category].tolist()
        for category in ['Food', 'Car', 'Entertainment']
        if category in pt.columns
    ]

    # determine if limit is exceeded for any selected month
    monthly_limit = 1500
    limit_exceeded = False
    df_monthly_totals = df[['date', 'cost']].groupby(by=pd.Grouper(key='date', freq='M'))['cost'].agg('sum').dropna()
    for monthly_sum in df_monthly_totals.tolist():
        if monthly_sum > monthly_limit:
            limit_exceeded = True

    results = {
        'labels': labels,
        'data': data,
        'limit_exceeded': limit_exceeded,
        'monthly_limit': monthly_limit,
        'user_months': user_months,
        'show_last_x_months': show_last_x_months
    }

    return results
