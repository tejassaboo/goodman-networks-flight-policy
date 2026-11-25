"""Writes the Goodman Networks scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (a colleague's flight) are read from the shared world, so they
match what search_flights lists. Expected answers are hand-written here; tests/test_scenarios.py checks them
against rules.solve.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses -----
BUSINESS_ONLY = keep(11, 11, "Goodman Networks employee business travel is authorized only in circumstances that are "
                     "clearly consistent with the Company's business interest.", "travel is for the business only")
DOMESTIC_DEF = keep(193, 195, None, "domestic travel includes Alaska and Hawaii")
REIMBURSE = keep(325, 325, "The Company reimburses employees for all reasonable and necessary expenses while traveling "
                 "on authorized company business", "the company pays for authorized business travel")
AUTHORIZE = keep(355, 355, "Employees must obtain authorization for all travel prior to booking any travel arrangements.",
                 "every trip needs its sign-off before booking")
TABLE = keep(383, 407, None, "Table 2: the approval each dollar range of travel expenses needs")
LOWEST = keep(635, 635, "Within travel policy, the lowest logical airfare is always required.",
              "the default: the lowest logical airfare")
COACH = keep(643, 643, "Coach class or lower special fares are required for all domestic travel and international "
             "flight segments of six (6) hours or less.", "coach for domestic travel and segments of six hours or less")
BUSINESS = keep(647, 647, "Travelers are permitted business class only on international flight segments when the "
                "non-stop/direct airtime exceeds six (6) hours from the point of origin to the first destination point.",
                "business only on an international segment over six hours")
FIRST = keep(651, 651, "First Class is not authorized to or from any destination unless approved by the EVP, with "
             "notification to the CEO.", "first class needs the EVP's approval")
ADVANCE = keep(683, 683, None, "requests at least seven days ahead, or the approving manager's exception")
UPGRADES = keep(689, 691, None, "upgrades at the traveller's expense or free; executive travel is in 11.1")
CRITERIA = keep(697, 705, None, "the lowest logical airfare: at most one interim stop, within two hours of the requested time")
NONSTOP = keep(707, 707, "Travelers may elect to fly a non-stop flight (over a lower-priced, connecting flight) provided "
               "that the additional cost is less than $100 per direction of travel. (i.e., the connecting flight would "
               "have added more than a 2-hour extension of travel time each way which would impact customer "
               "requirements).", "a nonstop over a cheaper connection within $100 per direction")
LOYALTY = keep(717, 717, None, "a frequent flyer programme may not add cost beyond the lowest airfare")
PREFERRED = keep(733, 733, None, "no higher fare to use frequent flyer privileges")
EXECUTIVE = keep(1151, 1151, None, "an executive's request to upgrade a travelling employee needs the CEO")
NON_EMPLOYEE = keep(1203, 1203, None, "a non-employee travels at their own risk and expense")
SCOPE_LINE = keep(89, 89, "This Goodman Networks Corporate Travel Policy covers all business travel activity",
                  "the policy covers business travel")
EXCEPTIONS = keep(329, 329, None, "exceptions are approved through the EVP organization and the CFO and/or CEO")
TRAVEL_DEPT = keep(101, 101, "The Corporate Travel Department is responsible for establishment, maintenance, revision, "
                   "and publication of this policy", "nobody else is named to settle the policy's words")

BAGGAGE = aside(813, 817, "When traveling for more than 14 days.", "a day count for excess baggage, not for booking")
CANCEL = aside(789, 789, "The employee should call a minimum of one (1) hour prior to departure time to cancel.",
               "a time rule for cancelling, not for booking")
HOTEL = aside(881, 881, "all hotel reservations for non-managers be capped at $85 per night",
              "a dollar cap on hotels, not on airfare")
GROUP = aside(1209, 1209, "Group Meetings are defined as 10 or more people traveling to a common destination for a "
              "common purpose.", "six travellers are not a group meeting")
MEALS = aside(1157, 1157, "however a cap is also applicable at $35.", "a meal cap, not a fare rule")
NOTIFY = aside(405, 407, "$1,200 + or first class tickets", "a CEO notification, not an approval")
FREE_UPGRADE = aside(689, 689, "If upgrades are available at no cost to Goodman Networks (i.e. frequent flyer incentives "
                     "offered by the airlines, etc.), they are allowed.",
                     "a free upgrade with miles is allowed but does not choose the ticket")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "EMPLOYEE", "accompanies": "", "origin": "",
        "destination": "", "travel_date": "", "booking_date": "", "purpose": "", "purpose_kind": "CUSTOMER_SITE_WORK",
        "requested_cabin": "ECONOMY", "requested_departure": "", "wants_nonstop": False, "loyalty_airline": "",
        "trip_estimate_cents": 0, "sign_offs": [], "travelling_with": [], "group_size": 1, "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def sign(role, name, subject="TRIP"):
    return {"role": role, "name": name, "subject": subject}


def offer(slot, flight, cabin, cents, seats=True):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": reasons,
            "approvers": approvers, "clauses": clauses, "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=3):
    # handbook.json background_offers is 0, so a search the scenario does not pin lists nothing; each pinned
    # search sets its own number.
    return {"name": "main", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request, trip_, search_spec, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": [search_spec]}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


LOW = ["AIR_REQUIREMENTS", "AIR_TRAVEL", "LOWEST_LOGICAL_AIRFARE"]
CLASS = ["AIR_REQUIREMENTS", "AIR_TRAVEL"]
NOT_LONG = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
DOMESTIC_COACH = ["DOMESTIC_COACH_REQUIRED", *NOT_LONG]
UNCLEAR = ["NOT_NAMED", "TRAVEL_DEPARTMENT", "EXECUTIVE_VP", "CHIEF_FINANCIAL_OFFICER", "CHIEF_EXECUTIVE"]


def on_file(*roles):
    """SYNC_NOTES 4': a booking whose sign-offs are on file accepts those roles and NONE."""
    return ["NONE", *roles]


# ===== easy (5) =====

scenario(
    "aspen-tarn", "easy", [],
    "Dallas to Atlanta on January 14th for the tower upgrade survey with the carrier. Economy, cheapest seat please.",
    trip(traveller_name="Marcus Bell", traveller_title="RF Engineer", origin="DFW", destination="ATL",
         travel_date="2027-01-14", booking_date="2026-12-15", purpose="Tower upgrade site survey for a wireless carrier",
         trip_estimate_cents=38_000, sign_offs=[sign("MANAGER", "Karen Ostrowski")]),
    search("DFW", "ATL", "2027-01-14", {
        "early": {"carrier": "AA", "depart": "06:50"},
        "morning": {"carrier": "DL", "depart": "09:30"},
        "afternoon": {"carrier": "DL", "depart": "14:15"},
        "evening": {"carrier": "AA", "depart": "18:05"},
    }, [
        offer("early-economy", "early", "ECONOMY", 17_900, seats=False),
        offer("morning-economy", "morning", "ECONOMY", 19_800),
        offer("afternoon-economy", "afternoon", "ECONOMY", 21_700),
        offer("evening-economy", "evening", "ECONOMY", 24_500),
    ]),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], ["LOWEST_FARE"], on_file("MANAGER"), LOW),
    [LOWEST, AUTHORIZE, TABLE],
    "The lowest logical airfare (line 635): the 06:50 fare is sold out, so Delta at 09:30. The trip's 380 dollars of "
    "travel expenses need Manager approval (Table 2), which is on file.")

scenario(
    "birch-quarry", "easy", ["dearer_option"],
    "I fly Dallas to London Heathrow on February 2nd for the operator's network rollout kickoff. It's a nine-hour "
    "overnight flight, so business class please.",
    trip(traveller_name="Priya Raman", traveller_title="Program Director, EMEA Deployments", origin="DFW",
         destination="LHR", travel_date="2027-02-02", booking_date="2027-01-04",
         purpose="Network rollout kickoff with a UK mobile operator", purpose_kind="CUSTOMER_MEETING",
         requested_cabin="BUSINESS", trip_estimate_cents=620_000,
         sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes")]),
    search("DFW", "LHR", "2027-02-02", {
        "american": {"carrier": "AA", "depart": "17:05", "minutes": [560]},
        "british": {"carrier": "BA", "depart": "19:40", "minutes": [570]},
    }, [
        offer("american-economy", "american", "ECONOMY", 98_000),
        offer("american-business", "american", "BUSINESS", 520_000),
        offer("british-economy", "british", "ECONOMY", 101_500),
        offer("british-business", "british", "BUSINESS", 489_000),
    ], background=0),
    expected("BOOK", ["british-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT"], on_file("EXECUTIVE_VP"), CLASS),
    [BUSINESS, AUTHORIZE, TABLE],
    "Both nonstops are international with airtime over six hours (line 647): business is permitted; the cheapest "
    "business fare. The 6,200 dollars of travel expenses need EVP / President-COO approval (Table 2), on file; the "
    "CEO notification above 1,200 dollars is not an approval.",
    distractors=[NOTIFY])

scenario(
    "cinder-moss", "easy", ["multi_leg"],
    "Dallas to Boston on January 26th for the small-cell design review. Connections are fine, just keep it cheap.",
    trip(traveller_name="Owen Fairley", traveller_title="Senior Design Engineer", origin="DFW", destination="BOS",
         travel_date="2027-01-26", booking_date="2026-12-28", purpose="Small-cell design review with the customer",
         purpose_kind="CUSTOMER_MEETING", trip_estimate_cents=91_000,
         sign_offs=[sign("VICE_PRESIDENT", "Angela Ruiz")]),
    search("DFW", "BOS", "2027-01-26", {
        "twostop": {"carrier": "UA", "via": ["IAH", "ORD"], "depart": "06:30", "layovers": [60, 75]},
        "atlanta": {"carrier": "DL", "via": ["ATL"], "depart": "07:05", "layovers": [70]},
        "nonstop": {"carrier": "AA", "depart": "08:15"},
        "jetblue": {"carrier": "B6", "depart": "12:40"},
    }, [
        offer("twostop-economy", "twostop", "ECONOMY", 24_900),
        offer("atlanta-economy", "atlanta", "ECONOMY", 29_600),
        offer("nonstop-economy", "nonstop", "ECONOMY", 41_800),
        offer("jetblue-economy", "jetblue", "ECONOMY", 39_500),
    ]),
    expected("BOOK", ["atlanta-economy"], ["ECONOMY"], ["LOWEST_FARE", "TOO_MANY_STOPS"], on_file("VICE_PRESIDENT"), LOW),
    [LOWEST, CRITERIA, AUTHORIZE, TABLE],
    "The lowest logical airfare is searched with no more than one interim stop each way (line 701): the cheapest "
    "itinerary has two stops and is out; the one-stop via Atlanta is the lowest logical airfare. The 910 dollars of "
    "expenses need Vice President approval, on file.")

scenario(
    "dove-heath", "easy", ["upgrade_not_taken"],
    "Dallas to Sao Paulo on February 9th for the fiber backhaul workshop. Economy is fine for me, whatever is cheapest.",
    trip(traveller_name="Lucas Pereira", traveller_title="Transport Network Manager", origin="DFW", destination="GRU",
         travel_date="2027-02-09", booking_date="2027-01-08", purpose="Fiber backhaul workshop with a Brazilian operator",
         purpose_kind="CUSTOMER_MEETING", trip_estimate_cents=290_000,
         sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes")]),
    search("DFW", "GRU", "2027-02-09", {
        "american": {"carrier": "AA", "depart": "20:40", "minutes": [590]},
        "latam": {"carrier": "LA", "depart": "21:55", "minutes": [595]},
    }, [
        offer("american-economy", "american", "ECONOMY", 121_000),
        offer("american-business", "american", "BUSINESS", 610_000),
        offer("latam-economy", "latam", "ECONOMY", 116_500),
        offer("latam-business", "latam", "BUSINESS", 585_000),
    ]),
    expected("BOOK", ["latam-economy"], ["ECONOMY"], ["LOWEST_FARE"], on_file("EXECUTIVE_VP"), LOW),
    [LOWEST, BUSINESS, AUTHORIZE, TABLE],
    "Business would be permitted on these nonstops over six hours (line 647), but permitted is not required: the "
    "traveller asks for economy, so the lowest logical airfare (line 635).")

scenario(
    "elder-pike", "easy", [],
    "Miami to Seattle on January 20th for the DAS install kickoff. It's almost seven hours coast to coast, so can you "
    "put me in business? If not, economy is fine; I have to be there.",
    trip(traveller_name="Renata Cole", traveller_title="Construction Manager", origin="MIA", destination="SEA",
         travel_date="2027-01-20", booking_date="2026-12-21", purpose="Distributed antenna system install kickoff",
         requested_cabin="BUSINESS", trip_estimate_cents=88_000,
         sign_offs=[sign("VICE_PRESIDENT", "Angela Ruiz")]),
    search("MIA", "SEA", "2027-01-20", {
        "american": {"carrier": "AA", "depart": "08:10", "minutes": [400]},
        "alaska": {"carrier": "AS", "depart": "10:35", "minutes": [405]},
    }, [
        offer("american-economy", "american", "ECONOMY", 38_900),
        offer("american-business", "american", "BUSINESS", 112_000),
        offer("alaska-economy", "alaska", "ECONOMY", 36_400),
    ], background=0),
    expected("BOOK", ["alaska-economy"], ["ECONOMY"], DOMESTIC_COACH, on_file("VICE_PRESIDENT"), LOW),
    [COACH, BUSINESS, LOWEST, AUTHORIZE, TABLE],
    "Coach class is required for all domestic travel (line 643), whatever the flight time; business is only for "
    "international segments (line 647). The lowest logical airfare.")

# ===== boundary twins (6) =====


def dub_flights(minutes):
    return {
        "aerlingus": {"carrier": "EI", "depart": "18:40", "minutes": [minutes]},
        "delta": {"carrier": "DL", "depart": "20:15", "minutes": [minutes]},
    }


DUB_OFFERS = [
    offer("aerlingus-economy", "aerlingus", "ECONOMY", 68_500),
    offer("aerlingus-business", "aerlingus", "BUSINESS", 312_000),
    offer("delta-economy", "delta", "ECONOMY", 71_200),
    offer("delta-business", "delta", "BUSINESS", 298_000),
]
DUB_TRIP = {"origin": "BOS", "destination": "DUB", "travel_date": "2027-02-16", "booking_date": "2027-01-15",
            "purpose": "Radio access network audit for an Irish operator", "purpose_kind": "CUSTOMER_MEETING",
            "requested_cabin": "BUSINESS", "trip_estimate_cents": 390_000,
            "sign_offs": [sign("EXECUTIVE_VP", "Leonard Haynes")]}
DUB_REQUEST = ("Boston to Dublin overnight on February 16th for the RAN audit. It's a long overnight flight and I "
               "present the afternoon I land. Business please; if that isn't allowed, economy is fine, I have to be "
               "there.")

scenario(
    "fable-wharf", "boundary_twin", ["dearer_option"],
    DUB_REQUEST,
    trip(traveller_name="Siobhan Keane", traveller_title="Principal RF Consultant", **DUB_TRIP),
    search("BOS", "DUB", "2027-02-16", dub_flights(361), DUB_OFFERS, background=0),
    expected("BOOK", ["delta-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT"], on_file("EXECUTIVE_VP"), CLASS),
    [BUSINESS, COACH, AUTHORIZE, TABLE],
    "Both nonstops are scheduled at 361 minutes: international airtime that exceeds six hours (line 647), so business "
    "is permitted; the cheapest business fare. Background is off: a filler connection could fall on the other side.",
    twin_of="gorse-lantern", twin_fact="both nonstops scheduled at 361 minutes or 360 minutes")

scenario(
    "gorse-lantern", "boundary_twin", [],
    DUB_REQUEST,
    trip(traveller_name="Siobhan Keane", traveller_title="Principal RF Consultant", **DUB_TRIP),
    search("BOS", "DUB", "2027-02-16", dub_flights(360), DUB_OFFERS, background=0),
    expected("BOOK", ["aerlingus-economy"], ["ECONOMY"], NOT_LONG, on_file("EXECUTIVE_VP"), LOW),
    [BUSINESS, COACH, LOWEST, AUTHORIZE, TABLE],
    "Both nonstops are scheduled at exactly 360 minutes: an international segment of six hours or less, so coach is "
    "required (line 643) and the 'exceeds six (6) hours' of line 647 is not met; the lowest logical airfare.",
    twin_of="fable-wharf", twin_fact="both nonstops scheduled at 360 minutes or 361 minutes")


def sea_offers(nonstop_cents):
    return [
        offer("denver-economy", "denver", "ECONOMY", 31_200),
        offer("american-economy", "american", "ECONOMY", nonstop_cents),
        offer("alaska-economy", "alaska", "ECONOMY", 45_600),
    ]


SEA_FLIGHTS = {
    "denver": {"carrier": "UA", "via": ["DEN"], "depart": "06:45", "minutes": [125, 165], "layovers": [140]},
    "american": {"carrier": "AA", "depart": "08:30", "minutes": [260]},
    "alaska": {"carrier": "AS", "depart": "13:10", "minutes": [265]},
}
SEA_TRIP = {"origin": "DFW", "destination": "SEA", "travel_date": "2027-03-03", "booking_date": "2027-02-01",
            "purpose": "5G densification planning with the carrier's Seattle market team",
            "purpose_kind": "CUSTOMER_MEETING", "wants_nonstop": True, "trip_estimate_cents": 96_000,
            "sign_offs": [sign("VICE_PRESIDENT", "Angela Ruiz")]}
SEA_REQUEST = ("Dallas to Seattle on March 3rd for the densification planning sessions. I'd much rather take the "
               "nonstop than connect through Denver, please.")

scenario(
    "hazel-rook", "boundary_twin", ["multi_leg", "dearer_option"],
    SEA_REQUEST,
    trip(traveller_name="Devon Marsh", traveller_title="Market Engineering Manager", **SEA_TRIP),
    search("DFW", "SEA", "2027-03-03", SEA_FLIGHTS, sea_offers(41_100), background=0),
    expected("BOOK", ["american-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_WITHIN_MARGIN"], on_file("VICE_PRESIDENT"),
             LOW),
    [NONSTOP, LOWEST, AUTHORIZE, TABLE],
    "The nonstop costs 99 dollars more than the Denver connection: less than $100 (line 707), and the connection adds "
    "170 minutes, over two hours, so the elected nonstop is allowed on either reading of the parenthesis.",
    twin_of="iris-spindle", twin_fact="the nonstop costs 99 or 100 dollars more than the connection")

scenario(
    "iris-spindle", "boundary_twin", ["multi_leg"],
    SEA_REQUEST,
    trip(traveller_name="Devon Marsh", traveller_title="Market Engineering Manager", **SEA_TRIP),
    search("DFW", "SEA", "2027-03-03", SEA_FLIGHTS, sea_offers(41_200), background=0),
    expected("BOOK", ["denver-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_TOO_EXPENSIVE"],
             on_file("VICE_PRESIDENT"), LOW),
    [NONSTOP, LOWEST, CRITERIA, AUTHORIZE, TABLE],
    "The nonstop costs exactly 100 dollars more: not 'less than $100' (line 707), so the lowest logical airfare, the "
    "one-stop connection (lines 701-705 treat it the same as a nonstop).",
    twin_of="hazel-rook", twin_fact="the nonstop costs 100 or 99 dollars more than the connection")


def ord_flights(united_depart):
    return {
        "early": {"carrier": "AA", "depart": "06:45"},
        "mid": {"carrier": "AA", "depart": "08:15"},
        "united": {"carrier": "UA", "depart": united_depart},
        "afternoon": {"carrier": "AA", "depart": "14:30"},
    }


ORD_OFFERS = [
    offer("early-economy", "early", "ECONOMY", 26_900),
    offer("mid-economy", "mid", "ECONOMY", 25_900),
    offer("united-economy", "united", "ECONOMY", 21_600),
    offer("afternoon-economy", "afternoon", "ECONOMY", 19_800),
]
ORD_TRIP = {"origin": "DFW", "destination": "ORD", "travel_date": "2027-02-23", "booking_date": "2027-01-25",
            "purpose": "Quarterly deployment review at the carrier's Chicago office", "purpose_kind": "CUSTOMER_MEETING",
            "requested_departure": "09:00", "trip_estimate_cents": 46_000,
            "sign_offs": [sign("MANAGER", "Karen Ostrowski")]}
ORD_REQUEST = ("Dallas to Chicago O'Hare on February 23rd for the quarterly deployment review. I'd like to leave "
               "around 9 in the morning. Economy.")

scenario(
    "jade-copse", "boundary_twin", [],
    ORD_REQUEST,
    trip(traveller_name="Hector Villanueva", traveller_title="Deployment Manager", **ORD_TRIP),
    search("DFW", "ORD", "2027-02-23", ord_flights("11:00"), ORD_OFFERS, background=0),
    expected("BOOK", ["united-economy"], ["ECONOMY"], ["LOWEST_FARE", "OUTSIDE_REQUESTED_TIME_WINDOW"],
             on_file("MANAGER"), LOW),
    [CRITERIA, LOWEST, AUTHORIZE, TABLE],
    "Requested 09:00. The 14:30 fare is cheaper but leaves 330 minutes later, outside 'no more than 2 hours before and "
    "2 hours after' (line 705). United at 11:00 leaves exactly 120 minutes after, inside the window: the lowest "
    "logical airfare. The 06:45 fare (135 minutes early, but landing 08:45) is dearer than the 08:15 one, so a reader "
    "who lets 'Departure/arrival' match either end gets the same answer.",
    twin_of="kiln-sorrel", twin_fact="the United flight leaves at 11:00 or 11:05")

scenario(
    "kiln-sorrel", "boundary_twin", [],
    ORD_REQUEST,
    trip(traveller_name="Hector Villanueva", traveller_title="Deployment Manager", **ORD_TRIP),
    search("DFW", "ORD", "2027-02-23", ord_flights("11:05"), ORD_OFFERS, background=0),
    expected("BOOK", ["mid-economy"], ["ECONOMY"], ["LOWEST_FARE", "OUTSIDE_REQUESTED_TIME_WINDOW"],
             on_file("MANAGER"), LOW),
    [CRITERIA, LOWEST, AUTHORIZE, TABLE],
    "Requested 09:00. United now leaves at 11:05, 125 minutes after (and lands 13:05), outside the window (line 705), "
    "as is 14:30. The 08:15 is the cheapest fare inside it; the 06:45 (landing 08:45) is dearer, so either reading of "
    "'Departure/arrival' gives 08:15: the lowest logical airfare.",
    twin_of="jade-copse", twin_fact="the United flight leaves at 11:05 or 11:00")

# ===== multi-rule (4) =====

scenario(
    "lark-basin", "multi_rule", ["multi_leg"],
    "Dallas to Bogota on February 24th for the operator's site acceptance tests. With the connection it's a long day "
    "of flying, so please book business. If the policy doesn't allow it, economy is fine; I have to be there.",
    trip(traveller_name="Camila Ortega", traveller_title="Director, Latin America Programs", origin="DFW",
         destination="BOG", travel_date="2027-02-24", booking_date="2027-01-26",
         purpose="Site acceptance tests with a Colombian operator", requested_cabin="BUSINESS",
         trip_estimate_cents=240_000, sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes")]),
    search("DFW", "BOG", "2027-02-24", {
        "miami": {"carrier": "AA", "via": ["MIA"], "depart": "07:10", "minutes": [170, 225], "layovers": [85]},
        "houston": {"carrier": "UA", "via": ["IAH"], "depart": "08:25", "minutes": [65, 300], "layovers": [75]},
    }, [
        offer("miami-economy", "miami", "ECONOMY", 48_600),
        offer("miami-business", "miami", "BUSINESS", 162_000),
        offer("houston-economy", "houston", "ECONOMY", 45_900),
        offer("houston-business", "houston", "BUSINESS", 171_000),
    ], background=0),
    expected("BOOK", ["houston-economy"], ["ECONOMY"], NOT_LONG, on_file("EXECUTIVE_VP"), LOW),
    [COACH, BUSINESS, LOWEST, AUTHORIZE, TABLE],
    "Only connections: 170 + 225 and 65 + 300 flying minutes. Every flight segment is six hours or less, so coach is "
    "required (line 643); business needs one segment's own nonstop airtime over six hours (line 647), and segments "
    "are never added. The lowest logical airfare.")

maple_spec = search("DFW", "LAX", "2027-01-28", {
    "morning": {"carrier": "AA", "depart": "08:00"},
    "noon": {"carrier": "AA", "depart": "12:30"},
    "united": {"carrier": "UA", "depart": "10:10"},
}, [
    offer("morning-economy", "morning", "ECONOMY", 28_900),
    offer("morning-business", "morning", "BUSINESS", 79_000),
    offer("noon-economy", "noon", "ECONOMY", 26_400),
    offer("united-economy", "united", "ECONOMY", 25_800),
])
scenario(
    "maple-cove", "multi_rule", ["multi_traveller", "outside_air_section", "dearer_option"],
    "I'm flying Dallas to Los Angeles on January 28th with Dana Whitfield, our EVP, for the carrier's executive "
    "briefing. Dana wants me next to her in business on her 8 a.m. flight so we can rehearse, and the CEO signed off "
    "on the company paying for it. Can you book that?",
    trip(traveller_name="Jordan Pike", traveller_title="Solutions Architect", origin="DFW", destination="LAX",
         travel_date="2027-01-28", booking_date="2026-12-29", purpose="Executive briefing for a wireless carrier",
         purpose_kind="CUSTOMER_MEETING", requested_cabin="BUSINESS", trip_estimate_cents=105_000,
         sign_offs=[sign("VICE_PRESIDENT", "Angela Ruiz"), sign("CHIEF_EXECUTIVE", "Ronald Garza", "CABIN_UPGRADE")],
         travelling_with=[{"name": "Dana Whitfield", "title": "Executive Vice President, Engineering Services",
                           "flight_number": first_flight("maple-cove", maple_spec, "morning-business"),
                           "date": "2027-01-28"}],
         group_size=2,
         notes=[("Dana Whitfield asked that the company pay for the traveller's business seat beside her on her flight, "
                "so they can prepare the briefing together.")]),
    maple_spec,
    expected("BOOK", ["morning-business"], ["BUSINESS"], ["EXECUTIVE_UPGRADE_APPROVED"],
             on_file("CHIEF_EXECUTIVE", "VICE_PRESIDENT"), ["AIR_UPGRADES", "EXECUTIVE_TRAVEL"]),
    [EXECUTIVE, UPGRADES, COACH, AUTHORIZE, TABLE],
    "Domestic travel is coach (line 643), but line 1151, to which the upgrade rule points (line 691), lets Executive "
    "Management travelling with an employee ask for the employee's upgrade at company expense with the CEO's "
    "approval, which is on file: business on the EVP's 08:00 flight. The trip itself is a Vice President's sign-off "
    "(1,050 dollars).")

scenario(
    "nettle-brook", "multi_rule", ["date_arithmetic"],
    "Sorry for the short notice: the customer moved the drive test to Monday afternoon, the 15th, so I'd like to leave "
    "Dallas for Denver around 8 that morning. Karen already okayed the late request. Cheapest economy.",
    trip(traveller_name="Tyler Brandt", traveller_title="Drive Test Engineer", origin="DFW", destination="DEN",
         travel_date="2027-02-15", booking_date="2027-02-10", purpose="Drive test for a carrier's network launch",
         requested_departure="08:00", trip_estimate_cents=44_000,
         sign_offs=[sign("MANAGER", "Karen Ostrowski"), sign("MANAGER", "Karen Ostrowski", "LATE_REQUEST")]),
    search("DFW", "DEN", "2027-02-15", {
        "united": {"carrier": "UA", "depart": "07:20"},
        "southwest": {"carrier": "WN", "depart": "09:05"},
        "american": {"carrier": "AA", "depart": "12:10"},
    }, [
        offer("united-economy", "united", "ECONOMY", 19_400),
        offer("southwest-economy", "southwest", "ECONOMY", 17_900),
        offer("american-economy", "american", "ECONOMY", 16_900),
    ]),
    expected("BOOK", ["southwest-economy"], ["ECONOMY"],
             ["LATE_REQUEST_APPROVED", "LOWEST_FARE", "OUTSIDE_REQUESTED_TIME_WINDOW"], on_file("MANAGER"),
             LOW + ["ADVANCE_PLANNING"]),
    [ADVANCE, LOWEST, CRITERIA, AUTHORIZE, TABLE],
    "Requested on February 10 for February 15: 5 days, under the seven of line 683. The approving manager made the "
    "exception and approved the request, which is on file, so the ticket is bought at the lowest logical airfare. The "
    "traveller asks to leave around 08:00: the 12:10 fare is cheaper but leaves 250 minutes later, outside the "
    "two-hour window (line 705); the 09:05 is the cheapest inside it. The drive test starts in the afternoon, so no "
    "arrival deadline separates the morning flights.")

scenario(
    "oriole-fen", "multi_rule", ["dearer_option"],
    "Dallas to Tokyo Narita on March 8th for the vendor summit. Leonard, my EVP, approved first class for this one and "
    "the CEO's office has been told. First class please.",
    trip(traveller_name="Gregory Lam", traveller_title="Vice President, Network Engineering", origin="DFW",
         destination="NRT", travel_date="2027-03-08", booking_date="2027-02-05",
         purpose="Equipment vendor summit in Tokyo", purpose_kind="CONFERENCE", requested_cabin="FIRST",
         trip_estimate_cents=1_240_000,
         sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes"), sign("EXECUTIVE_VP", "Leonard Haynes", "FIRST_CLASS")],
         notes=["The Chief Executive Officer's office was notified of the first-class ticket on 2027-02-03."]),
    search("DFW", "NRT", "2027-03-08", {
        "american": {"carrier": "AA", "depart": "11:00", "minutes": [790]},
        "japan": {"carrier": "JL", "depart": "12:15", "minutes": [800]},
    }, [
        offer("american-economy", "american", "ECONOMY", 132_000),
        offer("american-business", "american", "BUSINESS", 610_000),
        offer("american-first", "american", "FIRST", 1_120_000),
        offer("japan-economy", "japan", "ECONOMY", 128_500),
        offer("japan-business", "japan", "BUSINESS", 585_000),
        offer("japan-first", "japan", "FIRST", 1_060_000),
    ], background=0),
    expected("BOOK", ["japan-first"], ["FIRST"], ["FIRST_CLASS_APPROVED"], on_file("EXECUTIVE_VP"),
             CLASS + ["TRAVEL_AUTHORIZATIONS"]),
    [FIRST, AUTHORIZE, TABLE],
    "First class is not authorized unless approved by the EVP, with notification to the CEO (line 651; Table 2 lists "
    "first-class tickets for CEO notification): both are on file, so the cheapest first-class fare.")

# ===== hidden clause (2) =====

scenario(
    "plover-dune", "hidden_clause", ["multi_leg", "outside_air_section"],
    "Dallas to Honolulu on February 17th for the island network survey. It's an overseas flight over eight hours, and "
    "Angela, my VP, approved business class. Business please; if that isn't allowed, economy is fine, I have to be "
    "there.",
    trip(traveller_name="Kai Nakamura", traveller_title="Senior Network Planner", origin="DFW", destination="HNL",
         travel_date="2027-02-17", booking_date="2027-01-19", purpose="Island network survey for a wireless carrier",
         requested_cabin="BUSINESS", trip_estimate_cents=104_000,
         sign_offs=[sign("VICE_PRESIDENT", "Angela Ruiz"), sign("VICE_PRESIDENT", "Angela Ruiz", "BUSINESS_CLASS")]),
    search("DFW", "HNL", "2027-02-17", {
        "nonstop": {"carrier": "AA", "depart": "09:40", "minutes": [500]},
        "losangeles": {"carrier": "UA", "via": ["LAX"], "depart": "07:15", "minutes": [205, 345], "layovers": [90]},
    }, [
        offer("nonstop-economy", "nonstop", "ECONOMY", 61_800),
        offer("nonstop-business", "nonstop", "BUSINESS", 182_000),
        offer("losangeles-economy", "losangeles", "ECONOMY", 58_400),
        offer("losangeles-business", "losangeles", "BUSINESS", 171_000),
    ], background=0),
    expected("BOOK", ["losangeles-economy"], ["ECONOMY"], DOMESTIC_COACH, on_file("VICE_PRESIDENT"),
             LOW + ["DEFINITIONS"]),
    [DOMESTIC_DEF, COACH, LOWEST, AUTHORIZE, TABLE],
    "Table 1 (lines 193-195) defines domestic travel as within the contiguous 48 states, Alaska and Hawaii, so "
    "Honolulu is domestic: coach class is required (line 643) and the Vice President's business sign-off does not "
    "matter. The cheapest fare is the Los Angeles connection, one stop.")

H2_TRIP = {"origin": "DFW", "destination": "MSP", "travel_date": "2027-02-11", "booking_date": "2027-01-12",
           "purpose": "Two-day fiber splicing certification course", "purpose_kind": "TRAINING",
           "sign_offs": [sign("DIRECTOR", "Paul Whitaker")]}
H2_FLIGHTS = {
    "morning": {"carrier": "DL", "depart": "07:50"},
    "american": {"carrier": "AA", "depart": "10:15"},
    "evening": {"carrier": "DL", "depart": "16:20"},
}
H2_OFFERS = [
    offer("morning-economy", "morning", "ECONOMY", 26_300),
    offer("american-economy", "american", "ECONOMY", 24_100),
    offer("evening-economy", "evening", "ECONOMY", 27_800),
]
H2_REQUEST = ("Dallas to Minneapolis on February 11th for the splicing certification course. Paul, my director, "
              "signed off on the trip. Economy, cheapest flight.")

scenario(
    "quince-ridge", "hidden_clause", ["outside_air_section"],
    H2_REQUEST,
    trip(traveller_name="Nadia Brooks", traveller_title="Fiber Technician", trip_estimate_cents=75_000, **H2_TRIP),
    search("DFW", "MSP", "2027-02-11", H2_FLIGHTS, H2_OFFERS, background=0),
    expected("BOOK", ["american-economy"], ["ECONOMY"], ["LOWEST_FARE"], on_file("DIRECTOR"),
             LOW + ["TRAVEL_AUTHORIZATIONS"]),
    [AUTHORIZE, TABLE, LOWEST],
    "Table 2 (lines 383-407, in the authorizations section, not under Air Travel): travel expenses of $501-$750 need "
    "Director approval. The trip is estimated at exactly 750 dollars and the Director signed: book the lowest logical "
    "airfare.",
    twin_of="yarrow-fern", twin_fact="travel expenses of 750 or 751 dollars", distractors=[HOTEL])

# ===== distractor (2) =====

scenario(
    "rowan-glade", "distractor", ["date_arithmetic", "month_end"],
    "I know it's only a week out: Dallas to Phoenix on January 3rd for the small-cell build. Six of us from the crew "
    "are heading out, and I'll be on site about 16 days with my test gear. Cheapest economy please.",
    trip(traveller_name="Andre Wilkins", traveller_title="Field Technician", origin="DFW", destination="PHX",
         travel_date="2027-01-03", booking_date="2026-12-27", purpose="Small-cell construction build in Phoenix",
         trip_estimate_cents=47_000, sign_offs=[sign("MANAGER", "Karen Ostrowski")], group_size=6),
    search("DFW", "PHX", "2027-01-03", {
        "early": {"carrier": "AA", "depart": "07:00"},
        "southwest": {"carrier": "WN", "depart": "10:20"},
        "afternoon": {"carrier": "AA", "depart": "15:45"},
    }, [
        offer("early-economy", "early", "ECONOMY", 24_800),
        offer("southwest-economy", "southwest", "ECONOMY", 22_300),
        offer("afternoon-economy", "afternoon", "ECONOMY", 26_100),
    ]),
    expected("BOOK", ["southwest-economy"], ["ECONOMY"], ["LOWEST_FARE"], on_file("MANAGER"), LOW + ["ADVANCE_PLANNING"]),
    [ADVANCE, LOWEST, AUTHORIZE, TABLE],
    "Requested on December 27 for January 3: 7 days across the month and year end, which is 'at least seven (7) days' "
    "(line 683), so no exception is needed. Six travellers are not a group meeting (10 or more, line 1209); the 14-day "
    "baggage rule and the cancellation hour do not touch the ticket. The lowest logical airfare.",
    distractors=[GROUP, BAGGAGE, CANCEL])

scenario(
    "sedge-harbor", "distractor", ["upgrade_not_taken"],
    "Dallas to Paris on February 25th for the equipment vendor review. Economy is fine; I'll upgrade myself with my "
    "AAdvantage miles. Please book American though, I need the flights for my status. If American isn't possible, "
    "book what the policy allows; I have to be at the review.",
    trip(traveller_name="Elena Varga", traveller_title="Supply Chain Manager", origin="DFW", destination="CDG",
         travel_date="2027-02-25", booking_date="2027-01-27", purpose="Equipment vendor quality review in Paris",
         purpose_kind="INTERNAL_MEETING", loyalty_airline="American Airlines", trip_estimate_cents=270_000,
         sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes")]),
    search("DFW", "CDG", "2027-02-25", {
        "american": {"carrier": "AA", "depart": "16:45", "minutes": [550]},
        "airfrance": {"carrier": "AF", "depart": "18:20", "minutes": [555]},
    }, [
        offer("american-economy", "american", "ECONOMY", 92_400),
        offer("american-business", "american", "BUSINESS", 455_000),
        offer("airfrance-economy", "airfrance", "ECONOMY", 86_900),
        offer("airfrance-business", "airfrance", "BUSINESS", 431_000),
    ]),
    expected("BOOK", ["airfrance-economy"], ["ECONOMY"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE"],
             on_file("EXECUTIVE_VP"), LOW + ["AIR_UPGRADES", "FREQUENT_FLYER"]),
    [LOYALTY, PREFERRED, LOWEST, AUTHORIZE, TABLE],
    "Frequent flyer participation must not influence flight selection that adds cost beyond the lowest airfare "
    "(lines 717, 733): Air France, 55 dollars cheaper, not American. An upgrade with miles costs the company nothing "
    "and is allowed (line 689), but it does not choose the ticket; business is permitted on this route but not asked.",
    distractors=[FREE_UPGRADE, MEALS])

# ===== refusal (2) =====

scenario(
    "thistle-bay", "refusal", ["personal_travel", "outside_air_section"],
    "Can you book me Dallas to Orlando on December 21st? It's our family holiday trip to the parks. Just put it through "
    "the company travel account and I'll sort it out with expenses.",
    trip(traveller_name="Brianna Scott", traveller_title="Project Coordinator", origin="DFW", destination="MCO",
         travel_date="2026-12-21", booking_date="2026-11-30", purpose="Family holiday", purpose_kind="PERSONAL"),
    search("DFW", "MCO", "2026-12-21", {
        "american": {"carrier": "AA", "depart": "09:05"},
        "southwest": {"carrier": "WN", "depart": "13:40"},
    }, [
        offer("american-economy", "american", "ECONOMY", 27_400),
        offer("southwest-economy", "southwest", "ECONOMY", 24_900),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["INTRODUCTION", "POLICY_ENFORCEMENT", "SCOPE", "TRAVEL_AUTHORIZATIONS"]),
    [BUSINESS_ONLY, REIMBURSE, SCOPE_LINE],
    "Business travel is authorized only when clearly consistent with the company's business interest (line 11; line "
    "359), and the company reimburses expenses of authorized company business (line 325). A family holiday is not: no "
    "ticket is bought.")

scenario(
    "umber-wren", "refusal", ["multi_traveller", "outside_air_section"],
    "Hi, I'm Tessa Morgan. My husband Ryan is presenting at the wireless infrastructure conference in Las Vegas on "
    "March 9th and I'm going with him. Could you book my flight from Dallas too? Economy is fine.",
    trip(traveller_name="Tessa Morgan", traveller_title="Spouse of Ryan Morgan, Director of Engineering",
         passenger="SPOUSE_OR_GUEST", accompanies="Ryan Morgan", origin="DFW", destination="LAS",
         travel_date="2027-03-09", booking_date="2027-02-08",
         purpose="Accompanying her husband to a wireless infrastructure conference", purpose_kind="CONFERENCE",
         group_size=2),
    search("DFW", "LAS", "2027-03-09", {
        "southwest": {"carrier": "WN", "depart": "08:35"},
        "american": {"carrier": "AA", "depart": "11:50"},
    }, [
        offer("southwest-economy", "southwest", "ECONOMY", 18_600),
        offer("american-economy", "american", "ECONOMY", 21_200),
    ]),
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             ["NONE"],
             ["NON_EMPLOYEE_TRAVEL"]),
    [NON_EMPLOYEE],
    "Any non-employee accompanying an employee on an approved business trip does so at their own risk and expense "
    "(line 1203, under Additional Travel Policy Items): the company buys no ticket for her.")

# ===== flag (3) =====

scenario(
    "vale-crocus", "flag", ["multi_leg", "unclear_phrase"],
    "Austin to Frankfurt on March 2nd for the equipment certification at the vendor's lab. The long leg is ten hours, "
    "so business class please.",
    trip(traveller_name="Stefan Albrecht", traveller_title="Director, Equipment Certification", origin="AUS",
         destination="FRA", travel_date="2027-03-02", booking_date="2027-02-01",
         purpose="Equipment certification at the vendor's lab", purpose_kind="CUSTOMER_SITE_WORK",
         requested_cabin="BUSINESS", trip_estimate_cents=620_000, sign_offs=[sign("EXECUTIVE_VP", "Leonard Haynes")]),
    search("AUS", "FRA", "2027-03-02", {
        "dallas": {"carrier": "AA", "via": ["DFW"], "depart": "14:10", "minutes": [55, 590], "layovers": [95]},
        "chicago": {"carrier": "UA", "via": ["ORD"], "depart": "13:05", "minutes": [160, 505], "layovers": [80]},
    }, [
        offer("dallas-economy", "dallas", "ECONOMY", 112_000),
        offer("dallas-business", "dallas", "BUSINESS", 498_000),
        offer("chicago-economy", "chicago", "ECONOMY", 108_500),
        offer("chicago-business", "chicago", "BUSINESS", 476_000),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["chicago-business", "chicago-economy"], ["BUSINESS", "ECONOMY"],
             ["UNCLEAR_POLICY_TEXT"], UNCLEAR, CLASS,
             phrase="from the point of origin to the first destination point"),
    [BUSINESS, COACH, TRAVEL_DEPT, EXCEPTIONS, AUTHORIZE, TABLE],
    "Only connections: a short domestic hop (55 or 160 minutes) to Dallas or Chicago, then a transatlantic segment "
    "of 590 or 505 minutes. Line 647 allows business 'when the non-stop/direct airtime exceeds six (6) hours from the "
    "point of origin to the first destination point': from Austin to the first destination point is a short hop "
    "(coach), but the transatlantic segment's own nonstop airtime exceeds six hours (business), and one offer sells "
    "one cabin on both flights. Hold the cheapest business or economy fare; nobody is named to settle the words "
    "(line 101: the Corporate Travel Department owns the policy).",
    flag_twins=["birch-quarry", "lark-basin"],
    ambiguity={"phrase": "from the point of origin to the first destination point",
               "readings": [("the airtime is counted from the traveller's origin, Austin, to the first place the "
                             "itinerary lands: a short hop, so coach"),
                            ("each international segment counts from its own point of origin to its first destination: "
                             "the transatlantic segment exceeds six hours, so business")]})

sfo_spec = search("DFW", "SFO", "2027-02-18", {
    "denver": {"carrier": "UA", "via": ["DEN"], "depart": "07:00", "minutes": [125, 150], "layovers": [60]},
    "american": {"carrier": "AA", "depart": "08:00", "minutes": [245]},
    "united": {"carrier": "UA", "depart": "11:30", "minutes": [250]},
}, [
    offer("denver-economy", "denver", "ECONOMY", 28_700),
    offer("american-economy", "american", "ECONOMY", 33_200),
    offer("united-economy", "united", "ECONOMY", 36_900),
], background=0)
scenario(
    "willow-shoal", "flag", ["multi_leg", "unclear_phrase"],
    "Dallas to San Francisco on February 18th for the in-building wireless design review. Please put me on the "
    "American nonstop rather than the Denver connection.",
    trip(traveller_name="Grace Holloway", traveller_title="In-Building Systems Manager", origin="DFW",
         destination="SFO", travel_date="2027-02-18", booking_date="2027-01-19",
         purpose="In-building wireless design review", purpose_kind="CUSTOMER_MEETING", wants_nonstop=True,
         trip_estimate_cents=82_000, sign_offs=[sign("VICE_PRESIDENT", "Angela Ruiz")]),
    sfo_spec,
    expected("FLAG_FOR_APPROVAL", ["american-economy", "denver-economy"], ["ECONOMY"], ["UNCLEAR_POLICY_TEXT"],
             UNCLEAR + ["VICE_PRESIDENT"], ["LOWEST_LOGICAL_AIRFARE"],
             phrase="i.e., the connecting flight would have added more than a 2-hour extension of travel time each way"),
    [NONSTOP, CRITERIA, TRAVEL_DEPT, EXCEPTIONS, AUTHORIZE, TABLE],
    "The nonstop costs 45 dollars more than the Denver connection, less than $100 (line 707), but the connection takes "
    "335 minutes against 245, only 90 minutes longer. Line 707's parenthesis, '(i.e., the connecting flight would have "
    "added more than a 2-hour extension of travel time each way ...)', is either an example or a condition of the "
    "election. Hold either offer; nobody is named to settle the words (line 101).",
    flag_twins=["hazel-rook", "iris-spindle"],
    ambiguity={"phrase": "i.e., the connecting flight would have added more than a 2-hour extension of travel time each way",
               "readings": [("the parenthesis only illustrates why a traveller might elect a nonstop: the 45-dollar "
                             "difference is under $100, so book the nonstop"),
                            ("the parenthesis states when the election applies: the connection adds only 90 minutes, so "
                             "the lowest logical airfare, the connection")]})

scenario(
    "yarrow-fern", "flag", ["approval_required", "outside_air_section"],
    H2_REQUEST,
    trip(traveller_name="Nadia Brooks", traveller_title="Fiber Technician", trip_estimate_cents=75_100, **H2_TRIP),
    search("DFW", "MSP", "2027-02-11", H2_FLIGHTS, H2_OFFERS, background=0),
    expected("FLAG_FOR_APPROVAL", ["american-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED"],
             ["DIVISION_GENERAL_MANAGER", "VICE_PRESIDENT"], ["TRAVEL_AUTHORIZATIONS"]),
    [AUTHORIZE, TABLE],
    "Authorization is required before booking (line 355). The trip is estimated at 751 dollars: Table 2 puts $751 - "
    "$1,100 at Vice President and/or Division General Manager approval, and only the Director signed. Hold the lowest "
    "logical fare for that approval: approval required, not 'no compliant offer'.",
    twin_of="quince-ridge", twin_fact="travel expenses of 751 or 750 dollars",
    flag_twins=["quince-ridge", "cinder-moss"],
    ambiguity="none: an approval is required and missing; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
