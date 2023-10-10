from urllib.parse import urlparse

DIRS = {"ASSETS": "assets", "OUTPUT": "output"}


# From https://stackoverflow.com/a/38020041
def is_valid_url(candidate_url):
    try:
        result = urlparse(candidate_url)
        return all([result.scheme, result.netloc])
    except:
        return False


def drop_all_columns_except(df, *columns):
    total_cols = set(df.columns)
    diff = total_cols - set(columns)
    df.drop(diff, axis=1, inplace=True)
