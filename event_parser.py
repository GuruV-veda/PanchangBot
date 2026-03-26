from event_registry import EVENTS

def extract_event_name(question: str):
    q = question.lower()

    for name in EVENTS.keys():
        if name in q:
            return name

    return None