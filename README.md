# Goodman Networks Flight Policy

**No affiliation with Goodman Networks or Alcatel-Lucent.** The handbook is Goodman Networks' *Corporate Travel
Policy*, filed publicly with the SEC as Schedule Q ("Service Provider's Travel and Living Expenses") of its 2013
Master Services Agreement with Alcatel-Lucent (exhibit 10.4), bundled verbatim for research. It is a corporate
handbook: do not publish this plugin before the course staff confirm that a verbatim corporate handbook may be
redistributed (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the company's real travel
policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files
(the JSON files are the truth).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 7,392 words, 1,237 lines, 50,768 characters, sha256
`15131adc...945534fe91`, equal to `pilot_work/originals/goodman-networks/frozen/SHA256SUMS`) is never paraphrased,
and the task text restates no rule. It keeps the SEC confidentiality banner and page header at every page break
(converter output, left in). Under stock NanoAgent the agent does not see it: the plugin then runs as the `off`
baseline. The `harness.policy` switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch
`policy-switch`) adds it to the system prompt: `harness.policy: full` adds all of it, and the selection methods
add parts of it. These plugins are meant to run with `query: instructions+input`, so a selector sees the
traveller's request.

**Size.** At 1.33 tokens a word the policy is about 9,800 tokens (about 12,700 at 4 characters a token). On the
DeepSeek calibration of the paid Thornton and NJC runs (about 0.2 tokens a character of handbook plus 1,800) the
first call under `full` is about 12,000 input tokens, the second about 12,500 (plus the trip record) and the
third 13,000 to 14,500 (plus 3 to 9 offers). A 3-call run (`get_trip`, `search_flights`, `submit`) is about
38,000 to 39,000 input tokens, and the final-message call after `submit` starts near 15,000: far under the hosted
cap of 65,536, with room for one or two repeated searches.

**Flight duration, as this handbook defines it** (`rules.DURATION_RULES`, `rules.over`). Line 643, coach for
"international flight segments of six (6) hours or less", and line 647, business "only on international flight
segments when the non-stop/direct airtime exceeds six (6) hours from the point of origin to the first destination
point": one segment's own scheduled minutes, strictly over 360; segments are never added. A nonstop of 361
minutes qualifies, 360 does not. A connection whose every flight is 360 minutes or less is within on every reading;
a connection with a longer flight is unclear (one flag, `vale-crocus`). Domestic travel includes Alaska and Hawaii
(Table 1, lines 193-195), so it is coach whatever the flight time.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (every case buys the one-way fare
  out), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing;
  otherwise the chosen offer's own), `reason_code`, `approver` and `clause`, each from a closed list. The reason
  list is the template's shared list plus six Goodman codes (`DOMESTIC_COACH_REQUIRED`,
  `OUTSIDE_REQUESTED_TIME_WINDOW`, `TOO_MANY_STOPS`, `LATE_REQUEST_APPROVED`, `EXECUTIVE_UPGRADE_APPROVED`,
  `FIRST_CLASS_APPROVED`) and decoy codes from other handbooks' rules. Fares are in cents of US dollars.
- **Success:** every field is one the answer key accepts. Score = fields right / 6.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller
  asked for, the reason code gives why the request is declined. Such a booking accepts only the codes that name the
  handbook's ground, not `LOWEST_FARE`: business declined (`elder-pike`, `plover-dune`, `gorse-lantern`,
  `lark-basin`). A nonstop declined because the cheaper connection passes the handbook's specific savings or margin test, part of its lowest-logical-fare rule, accepts `LOWEST_FARE` beside the specific codes (lead's decision, the same in every plugin): `iris-spindle` (line 707's margin). `sedge-harbor` keeps `LOWEST_FARE`
  beside `LOYALTY_PROGRAM_PREFERENCE`, because lines 717 and 733 decline the airline on the lowest-fare test itself
  ("beyond the lowest available airfare").
- **No hidden facts:** no `answer_key_inputs`. The trip record carries what a booking tool would not show by
  itself: the trip's estimated travel expenses (Table 2 sets the approval by dollar range), sign-offs on file,
  colleagues on the same flights, the group size, the requested departure time and notes.

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (must_keep lines) |
|---|---|---|---|---|---|
| `aspen-tarn` | easy | BOOK (morning-economy; ECONOMY) | LOWEST_FARE | NONE or MANAGER | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (635, 355, 383-407) |
| `birch-quarry` | easy | BOOK (british-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL (647, 355, 383-407) |
| `cinder-moss` | easy | BOOK (atlanta-economy; ECONOMY) | LOWEST_FARE or TOO_MANY_STOPS | NONE or VICE_PRESIDENT | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (635, 697-705, 355, 383-407) |
| `dove-heath` | easy | BOOK (latam-economy; ECONOMY) | LOWEST_FARE | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (635, 647, 355, 383-407) |
| `elder-pike` | easy | BOOK (alaska-economy; ECONOMY) | DOMESTIC_COACH_REQUIRED or LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or VICE_PRESIDENT | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (643, 647, 635, 355, 383-407) |
| `fable-wharf` | boundary_twin | BOOK (delta-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL (647, 643, 355, 383-407) |
| `gorse-lantern` | boundary_twin | BOOK (aerlingus-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (647, 643, 635, 355, 383-407) |
| `hazel-rook` | boundary_twin | BOOK (american-economy; ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN | NONE or VICE_PRESIDENT | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (707, 635, 355, 383-407) |
| `iris-spindle` | boundary_twin | BOOK (denver-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or LOWEST_FARE | NONE or VICE_PRESIDENT | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (707, 635, 697-705, 355, 383-407) |
| `jade-copse` | boundary_twin | BOOK (united-economy; ECONOMY) | LOWEST_FARE or OUTSIDE_REQUESTED_TIME_WINDOW | NONE or MANAGER | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (697-705, 635, 355, 383-407) |
| `kiln-sorrel` | boundary_twin | BOOK (mid-economy; ECONOMY) | LOWEST_FARE or OUTSIDE_REQUESTED_TIME_WINDOW | NONE or MANAGER | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (697-705, 635, 355, 383-407) |
| `lark-basin` | multi_rule | BOOK (houston-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE (643, 647, 635, 355, 383-407) |
| `maple-cove` | multi_rule | BOOK (morning-business; BUSINESS) | EXECUTIVE_UPGRADE_APPROVED | NONE or CHIEF_EXECUTIVE or VICE_PRESIDENT | AIR_UPGRADES or EXECUTIVE_TRAVEL (1151, 689-691, 643, 355, 383-407) |
| `nettle-brook` | multi_rule | BOOK (southwest-economy; ECONOMY) | LATE_REQUEST_APPROVED or LOWEST_FARE or OUTSIDE_REQUESTED_TIME_WINDOW | NONE or MANAGER | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or ADVANCE_PLANNING (683, 635, 697-705, 355, 383-407) |
| `oriole-fen` | multi_rule | BOOK (japan-first; FIRST) | FIRST_CLASS_APPROVED | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL or TRAVEL_AUTHORIZATIONS (651, 355, 383-407) |
| `plover-dune` | hidden_clause | BOOK (losangeles-economy; ECONOMY) | DOMESTIC_COACH_REQUIRED or LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or VICE_PRESIDENT | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or DEFINITIONS (193-195, 643, 635, 355, 383-407) |
| `quince-ridge` | hidden_clause | BOOK (american-economy; ECONOMY) | LOWEST_FARE | NONE or DIRECTOR | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or TRAVEL_AUTHORIZATIONS (355, 383-407, 635) |
| `rowan-glade` | distractor | BOOK (southwest-economy; ECONOMY) | LOWEST_FARE | NONE or MANAGER | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or ADVANCE_PLANNING (683, 635, 355, 383-407) |
| `sedge-harbor` | distractor | BOOK (airfrance-economy; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | NONE or EXECUTIVE_VP | AIR_REQUIREMENTS or AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or AIR_UPGRADES or FREQUENT_FLYER (717, 733, 635, 355, 383-407) |
| `thistle-bay` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE | INTRODUCTION or POLICY_ENFORCEMENT or SCOPE or TRAVEL_AUTHORIZATIONS (11, 325, 89) |
| `umber-wren` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE | NON_EMPLOYEE_TRAVEL (1203) |
| `vale-crocus` | flag | FLAG_FOR_APPROVAL (chicago-business, chicago-economy; BUSINESS or ECONOMY) | UNCLEAR_POLICY_TEXT | NOT_NAMED or TRAVEL_DEPARTMENT or EXECUTIVE_VP or CHIEF_FINANCIAL_OFFICER or CHIEF_EXECUTIVE | AIR_REQUIREMENTS or AIR_TRAVEL (647, 643, 101, 329, 355, 383-407) |
| `willow-shoal` | flag | FLAG_FOR_APPROVAL (american-economy, denver-economy; ECONOMY) | UNCLEAR_POLICY_TEXT | NOT_NAMED or TRAVEL_DEPARTMENT or VICE_PRESIDENT or EXECUTIVE_VP or CHIEF_FINANCIAL_OFFICER or CHIEF_EXECUTIVE | LOWEST_LOGICAL_AIRFARE (707, 697-705, 101, 329, 355, 383-407) |
| `yarrow-fern` | flag | FLAG_FOR_APPROVAL (american-economy; ECONOMY) | APPROVAL_REQUIRED | DIVISION_GENERAL_MANAGER or VICE_PRESIDENT | TRAVEL_AUTHORIZATIONS (355, 383-407) |

Mix (EDGE_CASES.md 5.2, 24 row): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal,
3 flags (12.5%; the cap is 3). Decisions: 19 BOOK (3 business, 1 first, 15 economy), 2 REFUSE, 3
FLAG_FOR_APPROVAL. Twin pairs: 361 against 360 nonstop minutes (`fable-wharf`, `gorse-lantern`); a nonstop 99 or
100 dollars dearer than the connection, which adds 170 minutes (`hazel-rook`, `iris-spindle`); the cheapest
flight leaving 120 or 125 minutes after the requested 09:00 (`jade-copse`, `kiln-sorrel`); and, against the
approval-required flag, travel expenses of 750 or 751 dollars with a Director's sign-off (`quince-ridge`,
`yarrow-fern`).

Flags, each with clear twins on both sides:

- `vale-crocus` (unclear): only connections from Austin with a short first hop and a transatlantic segment over
  six hours. "from the point of origin to the first destination point" (line 647) can mean Austin to the first
  landing (coach) or each segment on its own (business). Twins `birch-quarry` (a nonstop over six hours:
  business) and `lark-basin` (every segment six hours or less: coach). Either held offer is accepted.
- `willow-shoal` (unclear): the elected nonstop costs 45 dollars more, under $100 (line 707), but the connection
  adds only 90 minutes; the parenthesis "(i.e., the connecting flight would have added more than a 2-hour
  extension of travel time each way ...)" reads as an example or as a condition. Twins `hazel-rook` (nonstop
  booked) and `iris-spindle` (connection booked). Either held offer is accepted.
- `yarrow-fern` (approval required): 751 dollars of travel expenses need Vice President and/or Division General
  Manager approval (Table 2), only a Director signed. Twins `quince-ridge` (750 dollars, Director: BOOK) and
  `cinder-moss` (910 dollars, Vice President: BOOK).

Approvers (template SYNC_NOTES 4'): every business trip needs its sign-off before booking (line 355, Table 2). A
BOOK whose sign-offs are on file accepts those roles and `NONE`; an unused sign-off on file is accepted too
(4(b)); the approval-required hold accepts only the awaited roles; the unclear holds accept `NOT_NAMED`,
`TRAVEL_DEPARTMENT` (line 101: the Corporate Travel Department owns the policy), the exception approvers of line
329 (`EXECUTIVE_VP`, `CHIEF_FINANCIAL_OFFICER`, `CHIEF_EXECUTIVE`) and the trip's signer; refusals
accept `NONE`. Table 2's CEO notification (over $1,200, first class) is not an approval, and is never accepted as
the approver. Degenerate agents (`tests/test_verifier.py`): always holding the right offer as unclear passes 2
cases; always booking the cheapest seat with `LOWEST_FARE` and `NONE` passes 6 (the plain cheapest-economy cases,
`iris-spindle` and `sedge-harbor`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, date, purpose, requested cabin, time, routing and airline, the trip's estimated expenses, sign-offs, colleagues flying along, group size, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-goodman-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, six reason
  codes, decoys and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design decisions, the blind read and the acceptance outputs.
- `tests/AUDIT_NOTES.md`: the independent audit, its fixes and its acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/goodman-networks-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
