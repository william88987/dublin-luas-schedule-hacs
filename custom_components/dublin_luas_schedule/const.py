"""Constants for Dublin Luas Schedule integration."""
from datetime import timedelta

DOMAIN = "dublin_luas_schedule"
API_URL = "http://luasforecasts.rpa.ie/xml/get.ashx"
UPDATE_INTERVAL = timedelta(minutes=1)

# Luas stops organized by line
LUAS_STOPS = {
    "Luas Red Line": {
        "TPT": "The Point",
        "SDK": "Spencer Dock",
        "MYS": "Mayor Square - NCI",
        "GDK": "George's Dock",
        "CON": "Connolly",
        "BUS": "Busáras",
        "ABB": "Abbey Street",
        "JER": "Jervis",
        "FOU": "Four Courts",
        "SMI": "Smithfield",
        "MUS": "Museum",
        "HEU": "Heuston",
        "JAM": "James's",
        "FAT": "Fatima",
        "RIA": "Rialto",
        "SUI": "Suir Road",
        "GOL": "Goldenbridge",
        "DRI": "Drimnagh",
        "BLA": "Blackhorse",
        "BLU": "Bluebell",
        "KYL": "Kylemore",
        "RED": "Red Cow",
        "KIN": "Kingswood",
        "BEL": "Belgard",
        "COO": "Cookstown",
        "HOS": "Hospital",
        "TAL": "Tallaght",
        "FET": "Fettercairn",
        "CVN": "Cheeverstown",
        "CIT": "Citywest Campus",
        "FOR": "Fortunestown",
        "SAG": "Saggart",
    },
    "Luas Green Line": {
        "BRO": "Broombridge",
        "CAB": "Cabra",
        "PHI": "Phibsborough",
        "GRA": "Grangegorman",
        "BRD": "Broadstone - University",
        "DOM": "Dominick",
        "PAR": "Parnell",
        "OUP": "O'Connell - Upper",
        "OGP": "O'Connell - GPO",
        "MAR": "Marlborough",
        "WES": "Westmoreland",
        "TRY": "Trinity",
        "DAW": "Dawson",
        "STS": "St. Stephen's Green",
        "HAR": "Harcourt",
        "CHA": "Charlemont",
        "RAN": "Ranelagh",
        "BEE": "Beechwood",
        "COW": "Cowper",
        "MIL": "Milltown",
        "WIN": "Windy Arbour",
        "DUN": "Dundrum",
        "BAL": "Balally",
        "KIL": "Kilmacud",
        "STI": "Stillorgan",
        "SAN": "Sandyford",
        "CPK": "Central Park",
        "GLE": "Glencairn",
        "GAL": "The Gallops",
        "LEO": "Leopardstown Valley",
        "BAW": "Ballyogan Wood",
        "CCK": "Carrickmines",
        "LAU": "Laughanstown",
        "CHE": "Cherrywood",
        "BRI": "Brides Glen",
    },
}

# Flatten stops for easy lookup
ALL_STOPS = {}
for line_stops in LUAS_STOPS.values():
    ALL_STOPS.update(line_stops)
