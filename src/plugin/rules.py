"""The answer key's rules for the Goodman Networks Corporate Travel Policy (Schedule Q of the Alcatel-Lucent
Master Services Agreement, SEC exhibit 10.4, 2013), as exact integer code. Byte-identical in
src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. Lines 643 and 647: "Coach class or lower special fares are required for all domestic travel
and international flight segments of six (6) hours or less." and "Travelers are permitted business class only
on international flight segments when the non-stop/direct airtime exceeds six (6) hours from the point of
origin to the first destination point." The handbook measures one flight segment's own airtime, never adds
segments, and is strictly over the limit above 360 minutes ("exceeds"; "or less" puts 360 itself in coach). A
nonstop is over when its scheduled minutes exceed 360. A connection whose every flight is 360 minutes or less
is within on every reading. A connection with a flight over 360 minutes is unclear (None): the words "from the
point of origin to the first destination point" can mean the first flight out of the traveller's origin (a
short first hop then rules business out) or each long segment on its own, and every offer sells one cabin on
all of its flights, so a short flight of the same ticket would be in business too.

Domestic travel (lines 193-195) is "within the contiguous 48 states, Alaska and Hawaii"; everything else is
international (lines 211-213). In the simulated world those are exactly the airports with country US.
"""

from contract import Approver, Cabin, Clause, Decision, Passenger, Purpose, ReasonCode, SignOffSubject

from .world import clock_minutes, days_between

HANDBOOK = "Goodman Networks Corporate Travel Policy (Schedule Q, Alcatel-Lucent MSA, 2013)"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.INTRODUCTION: "Introduction",
    Clause.GENERAL_PHILOSOPHY: "General Philosophy",
    Clause.SCOPE: "Scope",
    Clause.DEFINITIONS: "Definitions",
    Clause.POLICY_GUIDELINES: "Travel Policy Guidelines",
    Clause.EMPLOYEE_RESPONSIBILITY: "Employee Responsibility",
    Clause.POLICY_ENFORCEMENT: "Travel Policy Enforcement",
    Clause.TRAVEL_AUTHORIZATIONS: "Travel Authorizations & Approval Thresholds",
    Clause.PER_DIEM: "Per Diem",
    Clause.TRAVEL_ARRANGEMENTS: "Travel Arrangements",
    Clause.TRAVEL_RESERVATIONS: "Travel Reservations",
    Clause.AIR_TRAVEL: "Air Travel",
    Clause.AIR_REQUIREMENTS: "Air Travel Requirements/Reservations",
    Clause.ADVANCE_PLANNING: "Advance Planning",
    Clause.AIR_UPGRADES: "Upgrades for Air Travel",
    Clause.LOWEST_LOGICAL_AIRFARE: "Lowest Logical Airfare",
    Clause.FREQUENT_FLYER: "Airline Frequent Flyer Programs",
    Clause.PRIVATE_AIRCRAFT: "Travel on Private and Charter Aircraft",
    Clause.DENIED_BOARDING: "Denied Boarding Compensation",
    Clause.CANCELLATIONS: "Cancellations",
    Clause.EXCESS_BAGGAGE: "Lost or Excess Baggage",
    Clause.LODGING: "Lodging",
    Clause.EXECUTIVE_TRAVEL: "Executive Management Travel with Other Employees",
    Clause.MEALS: "Meal Reimbursement When Traveling",
    Clause.NON_EMPLOYEE_TRAVEL: "Non-Employee Travel",
    Clause.GROUP_MEETINGS: "Group Meetings Requirement",
}

# The handbook's duration threshold (the per-handbook duration hook; tests/test_duration.py tests both sides).
DURATION_RULES = (
    {"name": "international-business", "minutes": 360, "operator": ">", "lines": [647, 647],
     "quote": "Travelers are permitted business class only on international flight segments when the non-stop/direct "
              "airtime exceeds six (6) hours from the point of origin to the first destination point."},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 699-705: the lowest logical airfare is searched with "no more than one additional interim stop each way"
# and a departure "no more than 2 hours before and 2 hours after the requested time" (inclusive).
MOST_STOPS = 1
WINDOW_MINUTES = 120
# Line 707: a nonstop over a lower-priced connection "provided that the additional cost is less than $100 per
# direction of travel" (strict); its parenthesis speaks of a connection that "would have added more than a
# 2-hour extension of travel time each way".
NONSTOP_MARGIN_CENTS = 10_000
EXTENSION_MINUTES = 120
# Line 683: requests "at least seven (7) days prior to the planned departure date" (inclusive).
ADVANCE_DAYS = 7
# Lines 383-407, Table 2: the approval each dollar range of travel expenses needs (whole dollars, inclusive).
TIERS = (
    (100, 50_000, (Approver.MANAGER,)),
    (50_100, 75_000, (Approver.DIRECTOR,)),
    (75_100, 110_000, (Approver.VICE_PRESIDENT, Approver.DIVISION_GENERAL_MANAGER)),
    (110_100, None, (Approver.EXECUTIVE_VP, Approver.PRESIDENT_COO)),
)
RANK = {Approver.MANAGER: 1, Approver.DIRECTOR: 2, Approver.VICE_PRESIDENT: 3, Approver.DIVISION_GENERAL_MANAGER: 3,
        Approver.EXECUTIVE_VP: 4, Approver.PRESIDENT_COO: 4}
# Airports outside the contiguous 48 states that the definition of domestic travel names (Alaska, Hawaii).
NAMED_STATES = ("ANC", "HNL")

SEGMENT_PHRASE = "from the point of origin to the first destination point"
EXTENSION_PHRASE = "i.e., the connecting flight would have added more than a 2-hour extension of travel time each way"

LOW = [Clause.AIR_TRAVEL, Clause.AIR_REQUIREMENTS, Clause.LOWEST_LOGICAL_AIRFARE]
CLASS = [Clause.AIR_TRAVEL, Clause.AIR_REQUIREMENTS]
# A hold over unclear words: no role is named to settle the words (line 101 gives the policy to the Corporate Travel
# Department), and line 329 sends exceptions through the EVP organization "in addition to the CFO and/or CEO".
UNCLEAR_ROLES = [Approver.NOT_NAMED, Approver.TRAVEL_DEPARTMENT, Approver.EXECUTIVE_VP,
                 Approver.CHIEF_FINANCIAL_OFFICER, Approver.CHIEF_EXECUTIVE]


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s outbound flights are over the handbook's ``rule``."""
    if rule != "international-business":
        raise ValueError(f"unknown duration rule {rule!r}")
    limit = LIMITS[rule]
    minutes = [segment.scheduled_minutes for segment in offer.segments]
    if len(minutes) == 1:
        return minutes[0] > limit
    if all(value <= limit for value in minutes):
        return False
    return None


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def signed(trip, subject, roles=None):
    return [record for record in trip.sign_offs if record.subject == subject and (roles is None or record.role in roles)]


def domestic_airport(airport):
    return airport.country == "US"


def tier(cents):
    """Table 2 (lines 383-407): the roles whose approval a trip of ``cents`` travel expenses needs."""
    for low, high, roles in TIERS:
        if cents >= low and (high is None or cents <= high):
            return roles
    raise ValueError(f"{cents} cents falls between the whole-dollar ranges of Table 2: not modelled")


def stops_ok(offer):
    return len(offer.layover_minutes) <= MOST_STOPS and len(offer.return_layover_minutes) <= MOST_STOPS


def window_ok(trip, offer):
    if not trip.requested_departure:
        return True
    leaves = clock_minutes(offer.segments[0].depart_local[11:])
    return abs(leaves - clock_minutes(trip.requested_departure)) <= WINDOW_MINUTES


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused by this handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.purpose_kind == Purpose.PERSONAL:
        if trip.sign_offs:
            raise ValueError("a personal trip with sign-offs on file is not modelled")
        return answer(Decision.REFUSE, [], [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Approver.NONE],
                      [Clause.INTRODUCTION, Clause.POLICY_ENFORCEMENT, Clause.SCOPE, Clause.TRAVEL_AUTHORIZATIONS],
                      "Line 11: business travel is authorized only in circumstances clearly consistent with the "
                      "company's business interest; line 325: the company reimburses expenses while traveling on "
                      "authorized company business (and line 359). A holiday is neither: no ticket is bought.")
    if trip.passenger != Passenger.EMPLOYEE:
        if trip.sign_offs or not trip.accompanies:
            raise ValueError("a non-employee with sign-offs, or with nobody accompanied, is not modelled")
        # PERSONAL_TRAVEL_NOT_COVERED too: the companion's trip is not company business for her.
        return answer(Decision.REFUSE, [], [ReasonCode.COMPANION_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE,
                                            ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Approver.NONE], [Clause.NON_EMPLOYEE_TRAVEL],
                      "Line 1203: any non-employee accompanying an employee on an approved business trip does so at "
                      "their own risk and expense. The company buys no ticket.")
    if not domestic_airport(trip.origin):
        raise ValueError("a trip that starts outside the United States is not modelled")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys the one-way fare out")
    trips = signed(trip, SignOffSubject.TRIP)
    if len(trips) != 1:
        raise ValueError("every business trip carries exactly one trip sign-off (line 355)")
    authorizer = trips[0].role
    needed = tier(trip.trip_estimate_cents)
    domestic = domestic_airport(trip.origin) and domestic_airport(trip.destination)
    seated = [offer for offer in offers if offer.seats_available]
    fit = [offer for offer in seated if stops_ok(offer) and window_ok(trip, offer)]
    lowest = cheapest([offer for offer in fit if offer.cabin == Cabin.ECONOMY])
    if not lowest:
        raise ValueError("no economy offer within the search criteria can be bought")
    decision, chosen, reasons, relied, clauses, notes, phrase = choose(trip, seated, fit, lowest, domestic)
    days = days_between(trip.booking_date, trip.travel_date)
    if days < ADVANCE_DAYS:
        late = signed(trip, SignOffSubject.LATE_REQUEST, [Approver.MANAGER])
        if not late or decision != Decision.BOOK:
            raise ValueError("a late request without the approving manager's exception, or not booked, is not modelled")
        reasons.append(ReasonCode.LATE_REQUEST_APPROVED)
        relied.append(Approver.MANAGER)
        clauses.append(Clause.ADVANCE_PLANNING)
        notes.append(f"line 683: the request is {days} days before departure, under seven, and the approving manager "
                     "made the exception")
    elif days == ADVANCE_DAYS:
        clauses.append(Clause.ADVANCE_PLANNING)
        notes.append("line 683: the request is exactly seven days before departure, which is at least seven")
    elif signed(trip, SignOffSubject.LATE_REQUEST):
        raise ValueError("a late-request exception on a trip that is not late is not modelled")
    if authorizer not in needed:
        if RANK[authorizer] > RANK[needed[0]] or decision != Decision.BOOK:
            raise ValueError("a trip sign-off above its Table 2 level, or a short one on a hold, is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, chosen, [ReasonCode.APPROVAL_REQUIRED], list(needed),
                      [Clause.TRAVEL_AUTHORIZATIONS],
                      f"Line 355: authorization is needed before booking; Table 2 (lines 383-407) puts travel "
                      f"expenses of {trip.trip_estimate_cents // 100} dollars at "
                      f"{' or '.join(role.value for role in needed)} approval, and only a {authorizer.value} signed: "
                      "hold the ticket the request would otherwise get.")
    if decision == Decision.FLAG_FOR_APPROVAL:
        # A hold over unclear words: UNCLEAR_ROLES (lines 101 and 329); the trip sign-off on file, which the held
        # ticket relies on, is accepted too.
        approvers = [*UNCLEAR_ROLES, authorizer]
    else:
        # SYNC_NOTES 4': a BOOK whose needed sign-offs are already on file accepts those roles and NONE (readers
        # split on whether a routine sign-off already given is "relied on"); 4(b): an unused one is accepted too.
        unused = [record.role for record in trip.sign_offs if record.role not in relied]
        approvers = [Approver.NONE, authorizer, *relied, *unused]
        if trip.trip_estimate_cents <= 75_000 and authorizer == Approver.DIRECTOR:
            clauses.append(Clause.TRAVEL_AUTHORIZATIONS)
            notes.append("lines 383-407: travel expenses up to 750 dollars need Director approval, which is on file")
    notes.append(f"line 355 and Table 2: the trip sign-off relied on is the {authorizer.value}'s")
    return answer(decision, chosen, reasons, approvers, clauses, "; ".join(notes) + ".", phrase)


def choose(trip, seated, fit, lowest, domestic):
    """(decision, offers, reasons, roles relied on beyond the trip sign-off, clauses, notes, unclear phrase)."""
    if trip.requested_cabin == Cabin.ECONOMY:
        return economy(trip, seated, fit, lowest)
    if trip.wants_nonstop or trip.loyalty_airline or trip.requested_departure:
        raise ValueError("a premium-cabin request with a routing, airline or time wish is not modelled")
    if trip.requested_cabin == Cabin.BUSINESS:
        if domestic:
            return domestic_business(trip, fit, lowest)
        return international_business(fit, lowest)
    if trip.requested_cabin == Cabin.FIRST:
        return first_class(trip, fit, domestic)
    raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")


def economy(trip, seated, fit, lowest):
    """An economy request: the lowest logical airfare (lines 635 and 697-705), or the nonstop the traveller
    elects within line 707's margin."""
    if trip.wants_nonstop:
        if trip.loyalty_airline:
            raise ValueError("a nonstop wish with a loyalty wish is not modelled")
        return nonstop(fit, lowest)
    reasons, clauses = [ReasonCode.LOWEST_FARE], list(LOW)
    notes = ["lines 635 and 697: the lowest logical airfare"]
    cheaper = [offer for offer in seated if offer.cabin == Cabin.ECONOMY and offer.fare_cents < lowest[0].fare_cents]
    if any(not stops_ok(offer) for offer in cheaper):
        reasons.append(ReasonCode.TOO_MANY_STOPS)
        notes.append("line 701: a cheaper itinerary with two interim stops is outside the search criteria")
    if any(stops_ok(offer) and not window_ok(trip, offer) for offer in cheaper):
        reasons.append(ReasonCode.OUTSIDE_REQUESTED_TIME_WINDOW)
        notes.append("line 705: a cheaper flight leaves more than two hours from the requested time")
    if trip.loyalty_airline:
        if all(offer.carrier == trip.loyalty_airline for offer in lowest):
            raise ValueError("a loyalty wish that the lowest fare already meets is not modelled")
        # Lines 717 and 733 decline the airline on the lowest-fare test itself ("beyond the lowest available
        # airfare"), so LOWEST_FARE names why the request is declined, beside the loyalty code.
        reasons.append(ReasonCode.LOYALTY_PROGRAM_PREFERENCE)
        clauses += [Clause.FREQUENT_FLYER, Clause.AIR_UPGRADES]
        notes.append("lines 717 and 733: a frequent flyer programme may not add cost beyond the lowest airfare; "
                     "line 689: an upgrade with miles costs the company nothing and does not choose the flight")
    return Decision.BOOK, lowest, reasons, [], clauses, notes, ""


def nonstop(fit, lowest):
    """Line 707: a nonstop over a lower-priced connection when the additional cost is less than $100 per direction.
    Its parenthesis ("i.e., the connecting flight would have added more than a 2-hour extension of travel time
    each way") may be an example or a condition; it decides only when the connection adds two hours or less."""
    if any(not offer.layover_minutes for offer in lowest):
        raise ValueError("a nonstop wish when a nonstop is already the lowest fare is not modelled")
    best = cheapest([offer for offer in fit if offer.cabin == Cabin.ECONOMY and not offer.layover_minutes])
    if not best:
        raise ValueError("a nonstop wish with no nonstop offer is not modelled")
    extra = best[0].fare_cents - lowest[0].fare_cents
    added = {offer.elapsed_minutes - best[0].elapsed_minutes for offer in lowest}
    if len(added) != 1:
        raise ValueError("lowest connections of different lengths are not modelled")
    added = added.pop()
    if extra < NONSTOP_MARGIN_CENTS:
        if added > EXTENSION_MINUTES:
            return (Decision.BOOK, best, [ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN], [], list(LOW),
                    [(f"line 707: the nonstop costs {extra // 100} dollars more, less than 100, and the connection adds "
                     f"{added} minutes, so the elected nonstop is allowed on every reading")], "")
        return (Decision.FLAG_FOR_APPROVAL, best + lowest, [ReasonCode.UNCLEAR_POLICY_TEXT], [], [Clause.LOWEST_LOGICAL_AIRFARE],
                [(f"line 707: the nonstop costs {extra // 100} dollars more, less than 100, but the connection adds only "
                 f"{added} minutes; the parenthesis may make a connection that adds more than two hours a condition of "
                 "the nonstop. Hold either offer; line 101 gives the policy to the Corporate Travel Department")],
                EXTENSION_PHRASE)
    if added > EXTENSION_MINUTES:
        # The nonstop is declined because line 707's margin is not met; that margin is part of the lowest-fare rule,
        # so LOWEST_FARE is accepted beside the specific code (lead's decision, the same in every plugin).
        return (Decision.BOOK, lowest, [ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE, ReasonCode.LOWEST_FARE], [], list(LOW),
                [(f"line 707: the nonstop costs {extra // 100} dollars more, not less than 100: the lowest logical "
                 "airfare, the connection")], "")
    raise ValueError("a dear nonstop beside a connection adding two hours or less is not modelled")


def domestic_business(trip, fit, lowest):
    """Line 643: coach for all domestic travel; line 1151 (Executive Management travelling with employees and
    asking that they be upgraded at company expense: the CEO's approval), which line 691 points to."""
    upgrade = signed(trip, SignOffSubject.CABIN_UPGRADE, [Approver.CHIEF_EXECUTIVE])
    if upgrade:
        if not trip.travelling_with:
            raise ValueError("a company-paid upgrade with nobody travelling along is not modelled")
        flights = {(colleague.flight_number, colleague.date) for colleague in trip.travelling_with}
        beside = cheapest([offer for offer in fit if offer.cabin == Cabin.BUSINESS and
                           all((segment.flight_number, segment.depart_local[:10]) in flights for segment in offer.segments)])
        if not beside:
            raise ValueError("no business offer on the executive's flight")
        return (Decision.BOOK, beside, [ReasonCode.EXECUTIVE_UPGRADE_APPROVED], [Approver.CHIEF_EXECUTIVE],
                [Clause.EXECUTIVE_TRAVEL, Clause.AIR_UPGRADES],
                [("line 1151: Executive Management travelling with the employee asked for the upgrade at company expense "
                 "and the CEO approved it (line 691 points there from the upgrade rule): business on the executive's "
                 "flight")], "")
    if trip.travelling_with or signed(trip, SignOffSubject.CABIN_UPGRADE):
        raise ValueError("colleagues or an upgrade sign-off without the CEO's approval are not modelled")
    clauses = list(LOW)
    notes = [("line 643: coach class is required for all domestic travel, whatever the flight time; the lowest "
             "logical airfare")]
    if trip.origin.code in NAMED_STATES or trip.destination.code in NAMED_STATES:
        clauses.append(Clause.DEFINITIONS)
        notes.append("lines 193-195: domestic travel includes Alaska and Hawaii")
    # The reason names why business is declined (line 643, and line 647's international condition), not LOWEST_FARE.
    return (Decision.BOOK, lowest, [ReasonCode.DOMESTIC_COACH_REQUIRED, ReasonCode.UPGRADE_NOT_ELIGIBLE,
                                    ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET], [], clauses, notes, "")


def verdict_of(fit):
    verdicts = {over("international-business", offer) for offer in fit}
    if len(verdicts) != 1:
        raise ValueError("offers on different sides of the six-hour limit are not modelled (set background 0)")
    return verdicts.pop()


def international_business(fit, lowest):
    """Lines 643-647: business only on an international segment whose nonstop airtime exceeds six hours."""
    verdict = verdict_of(fit)
    business = cheapest([offer for offer in fit if offer.cabin == Cabin.BUSINESS])
    if verdict is False:
        # The reason names why business is declined (the six-hour condition), so LOWEST_FARE is not accepted.
        return (Decision.BOOK, lowest, [ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET, ReasonCode.UPGRADE_NOT_ELIGIBLE],
                [], list(LOW),
                [("line 643: every flight is six hours or less, so coach is required (flights are not added together); "
                 "the lowest logical airfare")], "")
    if not business:
        raise ValueError("a business request with no business offer is not modelled")
    if verdict is None:
        return (Decision.FLAG_FOR_APPROVAL, business + lowest, [ReasonCode.UNCLEAR_POLICY_TEXT], [], list(CLASS),
                [("line 647: only connections, whose flight out of the origin is short and whose next flight is over six "
                 "hours; 'from the point of origin to the first destination point' may mean the first flight or each "
                 "long segment. Hold either fare; line 101 gives the policy to the Corporate Travel Department")],
                SEGMENT_PHRASE)
    return (Decision.BOOK, business, [ReasonCode.INTERNATIONAL_LONG_FLIGHT], [], list(CLASS),
            [("line 647: an international nonstop whose airtime exceeds six hours: business is permitted, the cheapest "
             "business fare")], "")


def first_class(trip, fit, domestic):
    """Line 651: first class is not authorized to or from any destination unless approved by the EVP, with
    notification to the CEO (Table 2, line 405, lists first-class tickets for CEO notification)."""
    approved = signed(trip, SignOffSubject.FIRST_CLASS, [Approver.EXECUTIVE_VP])
    if domestic or not approved or verdict_of(fit) is not True:
        raise ValueError("first class other than an EVP-approved long international nonstop is not modelled")
    first = cheapest([offer for offer in fit if offer.cabin == Cabin.FIRST])
    if not first:
        raise ValueError("a first-class request with no first-class offer is not modelled")
    return (Decision.BOOK, first, [ReasonCode.FIRST_CLASS_APPROVED], [Approver.EXECUTIVE_VP],
            [*CLASS, Clause.TRAVEL_AUTHORIZATIONS],
            ["line 651: first class approved by the EVP, with the CEO notified: the cheapest first-class fare"], "")
