import pandas as pd


def download_nordpool(from_date, to_date, price_area='DK2'):
    url = (
            f"https://api.energidataservice.dk/dataset/Elspotprices/download?"
            f"format=XL&offset=0&start={from_date}T00:00&end={to_date}T00:00"
            f"&filter=%7B%22PriceArea%22:%22{price_area}%22%7D&sort=HourDK%20ASC&timezone=dk"
    )
    df = pd.read_excel(url)
    df['dt'] = df.HourDK.dt.date
    df['h'] = df.HourDK.dt.hour
    return df
