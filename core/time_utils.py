import datetime
import pytz

UZ_TZ = pytz.timezone("Asia/Tashkent")

def today_uz():
    return datetime.datetime.now(UZ_TZ).date()

def uz_time_to_utc(hour: int, minute: int = 0):
    uz_now = datetime.datetime.now(UZ_TZ)
    uz_dt = uz_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    utc_dt = uz_dt.astimezone(pytz.UTC)
    return utc_dt.time()
