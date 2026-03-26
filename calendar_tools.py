import pandas as pd
from datetime import datetime
from event_registry import EVENTS

class PanchangCalendar:

    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path, encoding="utf-8-sig")
        self.df.columns = self.df.columns.str.strip()

        if "Date" not in self.df.columns:
            raise ValueError(
                f"Expected 'Date' column. Found: {self.df.columns.tolist()}"
            )

        self.df["GregorianDate"] = pd.to_datetime(
            self.df["Date"],
            dayfirst=True
        )

        self.today = pd.Timestamp.today().normalize()


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