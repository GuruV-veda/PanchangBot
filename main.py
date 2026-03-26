import os
from anyio import Path
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI






# -----------------------------
# Load environment variables
# -----------------------------
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path,  override=True)
print("ENV path:", env_path)
print("Loaded API key:", os.getenv("OPENAI_API_KEY"))
#load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CSV_FILE = Path(__file__).parent / "seattle_panchang_2026_mypanchang_fixed.csv"
JSONL_FILE = Path(__file__).parent / "panchang_documents.json"
RULES_FILE = Path(__file__).parent / "festivalRules.json"

# -----------------------------
# Step 1: Load Data and Rules
# -----------------------------
print("Loading CSV...")
df = pd.read_csv(CSV_FILE)
print(f"Loaded {len(df)} rows")

print("Loading festival rules...")
with open(RULES_FILE, "r", encoding="utf-8") as f:
    festival_rules = json.load(f)

# -----------------------------
# Step 2: Festival Matcher
# -----------------------------
def festival_matcher(row, festival_rules):
    tithi = str(row['Tithi'])
    nakshatra = str(row['Nakshatra'])
    try:
        masa = str(row['Masa'])
    except KeyError:
        masa = ""   # protect if not present
    try:
        paksha = str(row['Paksha'])
    except KeyError:
        # You may need to derive paksha from tithi number in your CSV
        paksha = ""
    possible = []

    for fest, rule in festival_rules.items():
        # Example: Full Moon (Purnima)
        if 'tithi' in rule and rule['tithi'] in tithi:
            tithi_match = True
        else:
            tithi_match = False

        # Paksha (if present)
        paksha_match = ('paksha' not in rule) or (rule.get('paksha','') in paksha)

        # Masa (if present)
        masa_match = ('masa' not in rule) or (rule.get('masa','') in masa or (isinstance(rule.get('masa', None), list) and masa in rule['masa']))

        # Nakshatra (if present)
        nakshatra_match = ('nakshatra' not in rule) or (rule.get('nakshatra','') in nakshatra)

        if tithi_match and paksha_match and masa_match and nakshatra_match:
            possible.append(fest)

        # Special recurring festivals (e.g., Pradosham, Ekadashi):
        if fest == "Pradosham" and "Trayodashi" in tithi:
            possible.append("Pradosham")
        if fest == "Ekadashi" and "Ekadashi" in tithi:
            possible.append("Ekadashi")
        if fest == "Purnima" and "Purnima" in tithi:
            possible.append("Purnima")
        if fest == "Amavasya" and "Amavasya" in tithi:
            possible.append("Amavasya")
    return list(set(possible))  # no duplicates

# -----------------------------
# Step 3: Transform Rows Into Documents w/Festival Tags
# -----------------------------
print("Annotating rows with festival matches...")

def row_to_document(row):
    return (
        f"On {row['GregorianMonth']} {int(row['Date'])}, {row['GregorianYear']} "
        f"({row['Vaar']}) in Seattle: "
        f"Masa is {row['Masa']}, "
        f"Paksha is {row['Paksha']}, "
        f"Tithi is {row['Tithi']}, "
        f"Nakshatra is {row['Nakshatra']}, "
        f"Yoga is {row['Yoga']}. "
        f"Sunrise is at {row['Sun rise']} and sunset at {row['Sun Set']}. "
        f"Rahukala is {row['Rahukala']}, "
        f"Yamaganda is {row['Yamaganda']}, "
        f"Gulikai is {row['Gulikai']}."
    )

festival_list = []
docs = []

for idx, row in df.iterrows():
    entry = row_to_document(row)
    possible_fests = festival_matcher(row, festival_rules)
    docs.append({"text": entry, "possibleFestivals": possible_fests})

print("Sample document w/possibleFestivals:")
print(json.dumps(docs[0], indent=2))

#------------------
#Adding Veda Events
#------------------

def build_panchang_documents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def build_veda_event_documents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    temple = data["Temple_Information"]
    docs.append({
        "text": f"{temple['Name']} is located at {temple['Address']}. "
                f"Phone: {temple['Phone']}. Website: {temple['Website']}. "
                f"Weekend hours: {temple['Temple_Hours']['Weekends']}. "
                f"Weekday hours: {temple['Temple_Hours']['Weekdays']}.",
        "source": "veda_events",
        "type": "temple_info"
    })

    for item in data["Weekly_Abhisheka_Puja_Schedule"]:
        docs.append({
            "text": f"Every {item['Day']} at {item['Time']}, "
                    f"{item['Service']} is performed at Veda Sri Venkateswara Temple in Redmond.",
            "source": "veda_events",
            "type": "weekly_puja"
        })

    for item in data["Monthly_Puja_Schedule"]:
        docs.append({
            "text": f"On the {item['Occurrence']} of every month at {item['Time']}, "
                    f"{item['Service']} is performed at  Veda Sri Venkateswara Temple.",
            "source": "veda_events",
            "type": "monthly_puja"
        })

    for item in data["Tithi_Based_Puja_Schedule"]:
        docs.append({
            "text": f"On {item['Tithi']}, at {item['Time']}, "
                    f"{item['Service']} is conducted at Veda Sri Venkateswara Temple.",
            "source": "veda_events",
            "type": "tithi_puja"
        })

    for priest in data["VEDA_Priests"]:
        docs.append({
            "text": f"{priest['Name']} serves at Veda Sri Venkateswara Temple as "
                    f"{priest.get('Title') or priest.get('Role') or priest.get('Specialty')}.",
            "source": "veda_events",
            "type": "priest_info"
        })

    return docs

# -----------------------------
# Step 4: Export as Panchangam JSON
# -----------------------------
print("Exporting to enriched JSON...")

with open(JSONL_FILE, "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=2)

print(f"Panchangam JSON file created: {JSONL_FILE}")

# -----------------------------
# Step 4a: Export Unified JSON
# -----------------------------

panchang_docs = build_panchang_documents(JSONL_FILE)
veda_docs = build_veda_event_documents(Path(__file__).parent /"data/veda_events.json")

all_docs = panchang_docs + veda_docs

with open("rag_documents.json", "w", encoding="utf-8") as f:
    json.dump(all_docs, f, indent=2)

print(f"rag_document JSON file created: {'rag_documents'}")

print("Creating vector store and uploading documents...")

# vector_store = client.vector_stores.create(
#    name="seattle-panchang-2026"
# )

file = client.files.create(
    file=open("rag_documents.json", "rb"),
    purpose="assistants"
)

client.vector_stores.files.create_and_poll(
    vector_store_id="vs_69c4481dc2b48191aff0b997e515845b",
    file_id=file.id
)


""" client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=[open(JSONL_FILE, "rb")]
) """

print("Vector store ready!")


