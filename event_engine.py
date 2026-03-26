from event_registry import EVENTS

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