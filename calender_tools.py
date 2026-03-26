import pandas as pd
from datetime import datetime
from event_registry import EVENTS

class PanchangCalendar:

    def next_tithi(self, tithi_name):
        future = self.df[self.df["GregorianDate"] >= self.today]

        rows = future[
            future["Tithi"].str.contains(tithi_name, case=False, na=False)
        ]

        return rows.iloc[0] if not rows.empty else None

    def next_nakshatra(self, nakshatra):
        future = self.df[self.df["GregorianDate"] >= self.today]

        rows = future[
            future["Nakshatra"].str.contains(nakshatra, case=False, na=False)
        ]

        return rows.iloc[0] if not rows.empty else None

    def next_monthly_weekday(self, occurrence):
        # e.g. "3rd Saturday"
        import calendar
        from datetime import date

        nth, weekday = occurrence.split()
        weekday_idx = list(calendar.day_name).index(weekday)

        year = self.today.year
        month = self.today.month

        while True:
            monthcal = calendar.monthcalendar(year, month)
            week = int(nth[0]) - 1
            day = monthcal[week][weekday_idx]

            if day != 0:
                candidate = date(year, month, day)
                if candidate >= self.today:
                    return candidate

            month += 1
            if month > 12:
                month = 1
                year += 1

    def next_event(calendar, event_name):
        event = EVENTS.get(event_name.lower())

        if not event:
            return None

        if event["type"] == "tithi":
            return calendar.next_tithi(event["value"])

        if event["type"] == "nakshatra":
            return calendar.next_nakshatra(event["value"])

        if event["type"] == "monthly_weekday":
            return calendar.next_monthly_weekday(event["occurrence"])