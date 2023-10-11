import pandas as pd
import holidays
import datetime as dt

def GetBrazilianHolidays(start_date, end_date):
    if isinstance(start_date, str):
        pass
    elif isinstance(start_date, dt.date):
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
    else:
        raise ValueError('The date must follow the type str yyyy-mm-dd or the type dt.date')
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    br_holidays = holidays.Brazil(years=range(start_date.year, end_date.year + 1))

    holidays_list = []
    for date in pd.date_range(start_date, end_date):
        if date in br_holidays:
            holidays_list.append(date)

    return holidays_list