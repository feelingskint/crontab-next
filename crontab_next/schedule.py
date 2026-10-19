"""Work out when a parsed cron expression fires."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .fields import Cron

SEARCH_YEARS = 5


def _day_matches(cron: Cron, day: date) -> bool:
    """Whether the day field matches; per crontab(5), if both the day-of-month and
    day-of-week fields are restricted, either one matching is enough."""
    weekday = day.isoweekday() % 7  # cron counts from Sunday = 0
    dom = day.day in cron.days
    dow = weekday in cron.weekdays
    if cron.any_day:
        return dow
    if cron.any_weekday:
        return dom
    return dom or dow


def next_runs(cron: Cron, start: datetime, count: int = 5) -> list[datetime]:
    """The next `count` times after `start` (exclusive) at which `cron` fires."""
    t = start.replace(second=0, microsecond=0) + timedelta(minutes=1)
    give_up = start + timedelta(days=366 * SEARCH_YEARS)
    runs: list[datetime] = []
    while len(runs) < count:
        if t > give_up:
            raise ValueError(f"{cron.source!r} does not fire in the next {SEARCH_YEARS} years")
        if t.month not in cron.months:
            t = (t.replace(day=1, hour=0, minute=0) + timedelta(days=32)).replace(day=1)
        elif not _day_matches(cron, t.date()):
            t = t.replace(hour=0, minute=0) + timedelta(days=1)
        elif t.hour not in cron.hours:
            t = t.replace(minute=0) + timedelta(hours=1)
        elif t.minute not in cron.minutes:
            t += timedelta(minutes=1)
        else:
            runs.append(t)
            t += timedelta(minutes=1)
    return runs
