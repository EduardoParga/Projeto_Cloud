from datetime import datetime


def yymmdd(dt:datetime):
    return dt.strftime("%y"), dt.strftime("%m"), dt.strftime("%d")



