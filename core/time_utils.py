import datetime
import pytz

UZ_TZ = pytz.timezone("Asia/Tashkent")


def today_uz() -> datetime.date:
    """Текущая дата по Узбекистану"""
    return datetime.datetime.now(UZ_TZ).date()


def now_uz() -> datetime.datetime:
    """Текущее время по Узбекистану"""
    return datetime.datetime.now(UZ_TZ)


def uz_time_to_utc(hour: int, minute: int = 0) -> datetime.time:
    """
    Конвертирует время Узбекистана (сегодня) в UTC time
    для job_queue.run_daily
    """
    today = today_uz()

    uz_dt = UZ_TZ.localize(
        datetime.datetime.combine(
            today,
            datetime.time(hour, minute)
        )
    )

    return uz_dt.astimezone(pytz.UTC).time()

