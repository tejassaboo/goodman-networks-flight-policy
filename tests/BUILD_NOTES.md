# Build notes: goodman-networks-flight-policy (wave 2)

Built 2026-11-24 from `pilot_work/tier_plan/build/WAVE2_BUILD_BRIEF.md`, unattended: every open choice below took
the recommended option and is recorded here.

## Handbook

`pilot_work/originals/goodman-networks/frozen/goodman-networks_policy.txt`: 7,392 words, 1,237 lines, sha256
`15131adc...945534fe91` (Schedule Q of the Goodman Networks / Alcatel-Lucent MSA, SEC exhibit 10.4). Under 10,000
words, so 24 scenarios (EDGE_CASES 5.1). Instantiated with `--slug goodman-networks --task-id book-goodman-flight
--background 0 --scenarios 24`. `handbook.json` `raw_pdf_sha256` holds the raw HTML's sha256 (there is no PDF).

## Checkable flight rules found (frozen lines)

| Rule | Lines | Operator | Used by |
|---|---|---|---|
| Authorization before booking; Table 2 approval by dollar range of travel expenses | 355, 383-407 | ranges inclusive, whole dollars | every booking; `quince-ridge`, `yarrow-fern` |
| Domestic = contiguous 48 + Alaska + Hawaii; international = outside | 193-195, 211-213 | definition | `plover-dune` |
| Coach for domestic and international segments of six hours or less | 643 | "or less", inclusive | `elder-pike`, `gorse-lantern`, `lark-basin` |
| Business only on international segments over six hours of nonstop airtime | 647 | "exceeds", strict | `birch-quarry`, `fable-wharf`, `vale-crocus` |
| First class only with EVP approval and CEO notification | 651 | | `oriole-fen` |
| Advance planning: at least seven days, else the approving manager's exception | 683 | "at least", inclusive | `nettle-brook`, `rowan-glade` |
| Upgrades at own expense or free; executive travel cross-reference | 689-691 | | `sedge-harbor`, `maple-cove` |
| Lowest logical airfare: at most one interim stop; departure within two hours of the requested time | 697-705 | "no more than", inclusive | `cinder-moss`, `jade-copse`, `kiln-sorrel` |
| Nonstop election when the extra cost is less than $100 per direction | 707 | "less than", strict | `hazel-rook`, `iris-spindle`, `willow-shoal` |
| Frequent flyer programmes must not add cost | 717, 733 | | `sedge-harbor` |
| Executive Management asking for an employee's upgrade at company expense: CEO approval | 1151 | | `maple-cove` |
| Non-employees travel at their own risk and expense | 1203 | | `umber-wren` |
| Travel only for the business interest | 11, 325, 359 | | `thistle-bay` |

Rules present but not tested (no booking decision rests on them, or a scenario would need facts the world does not
model): supplier-direct bookings (259, 509, 677), group meetings of 10 or more (1209, used only as a distractor in
`rowan-glade`), private and charter aircraft (753), denied boarding (759-769), same-plane one-stop flights (707,
last sentence). The handbook has no refundable-fare rule and no overnight-stop rule for booking (7.9 is about airline
delays), so neither appears and `OVERLAY_MINIMUMS` asks for no overnight case.

## Decisions taken without asking

1. **Trip authorization in every case.** Line 355 makes a sign-off mandatory before booking, and Table 2 sets its
   level by "Dollar Range" of travel expenses. The trip record carries `trip_estimate_cents` (the whole trip's
   estimated travel expenses, the amount the sign-off was asked for) and one TRIP sign-off; `rules.solve` checks
   the signer against Table 2. Amounts in the cents gaps between ranges (e.g. 500.50 dollars) raise ValueError: no
   scenario uses them. A signer above the needed level also raises (not modelled).
2. **Approvers under SYNC_NOTES 4'** (coordinator message during the build): a BOOK accepts `NONE` plus every
   sign-off on file it rests on (and unused ones, 4(b)); the approval hold `yarrow-fern` accepts only
   `VICE_PRESIDENT` / `DIVISION_GENERAL_MANAGER`; unclear holds accept `NOT_NAMED`, `TRAVEL_DEPARTMENT` (line 101)
   and the trip's signer; refusals `NONE`. `MAX_PASS_ALWAYS_LOWEST` = 11 (measured; the plain cheapest-economy
   cases: aspen-tarn, dove-heath, elder-pike, gorse-lantern, iris-spindle, lark-basin, nettle-brook, plover-dune,
   quince-ridge, rowan-glade, sedge-harbor). `MAX_PASS_ALWAYS_FLAG` = 2 (the two unclear holds).
3. **Table 2's "CEO Notification"** (1,200 dollars and over, first class) is read as notice, not approval: it never
   blocks a booking and `CHIEF_EXECUTIVE` is not accepted as the approver for it.
4. **Business is a permission.** A traveller who asks for business on an international nonstop over six hours gets
   the cheapest business fare; one who asks for economy gets economy (`dove-heath`, `sedge-harbor`). The answer key
   does not accept economy when business is asked and permitted (see "Unsure").
5. **Duration.** Per segment, strict over 360; a connection with every flight at or under 360 is coach; a connection
   with a longer flight is unclear (`vale-crocus` is the only scenario on it). International business and first
   cases use `background: 0`, as do all twins whose answer could move with a filler itinerary.
6. **The time window** is measured on the departure from the origin against `requested_departure`; it applies only
   when the record names a time. A cheaper flight outside the window is not accepted (line 697: travellers are
   required to book the lowest logical airfare the criteria determine).
7. **The nonstop election** applies only when the traveller asks for a nonstop (`wants_nonstop`). The extra cost is
   against the lowest logical fare; the added time is the connection's elapsed minutes minus the nonstop's.
8. **Advance planning:** under seven days needs the approving manager's LATE_REQUEST sign-off (late cases have
   Manager-level trips, so "approving manager" is unambiguous). A late case without it raises (no flag slot left).
9. **One ticket per case:** every case is the one-way fare out; the Trip has no `return_date` field.
10. **Decoys:** WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED, NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED,
    OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING, EXTENDED_TRAVEL_SAVINGS, CHANCELLOR_WRITTEN_AUTHORIZATION,
    DOUBLE_BOOKING_PROHIBITED, CANDIDATE_TRIP_NOT_COVERED, SAME_CLASS_AS_CUSTOMER (each subject grepped: absent).
    PRIVATE_AIRCRAFT_NOT_APPROVED and DENIED_BOARDING_NOT_ALLOWED were not used as decoys: this handbook has
    sections 7.7 and 7.8.

## Mix and overlays

5 easy, 6 boundary twins (361/360 minutes; 99/100 dollars; 11:00/11:05 against 09:00), 4 multi-rule, 2 hidden
clause, 2 distractor, 2 refusal, 3 flags (12.5%). Overlays: multi_leg 7, date_arithmetic 2, month_end 1,
personal_travel 1, multi_traveller 2, dearer_option 6, upgrade_not_taken 2, outside_air_section 6.

## Independent blind read (non-flag scenarios)

Re-derived from the handbook text and the `get_trip` / `search_flights` outputs only (a dump of every offer,
background ones included), not from `rules.py`. Agreement on decision and offer for all 21 non-flag scenarios:

| Scenario | My reading | Agrees |
|---|---|---|
| aspen-tarn | 06:50 fare sold out; Delta 09:30 $198 is the lowest; $380 trip, Manager signed (Table 2 $1-500) | yes |
| birch-quarry | DFW-LHR nonstops 560/570 min > 360, international: business permitted, BA business $4,890 cheapest; $6,200 trip, EVP | yes |
| cinder-moss | UA $249 has two stops (line 701 out); Delta via ATL $296 is lowest logical; $910, VP | yes |
| dove-heath | economy asked; LATAM $1,165 lowest (background offers far dearer); EVP | yes |
| elder-pike | MIA-SEA is domestic: coach (643) regardless of 400 min; Alaska $364 | yes |
| fable-wharf | 361 min > 360: Delta business $2,980 | yes |
| gorse-lantern | 360 min is "six hours or less": coach, Aer Lingus $685 | yes |
| hazel-rook | nonstop $411 is $99 over the $312 connection, connection 430 vs 260 min (+170): nonstop allowed | yes |
| iris-spindle | $100 is not less than $100: the connection $312 | yes |
| jade-copse | window 07:00-11:00; 11:00 United $216 inside (inclusive); 14:30 and 06:45 outside | yes |
| kiln-sorrel | 11:05 is outside; only 08:15 $259 inside | yes |
| lark-basin | every segment <= 300 min: coach; UA via IAH $459 | yes |
| maple-cove | domestic, but 1151 + CEO approval on file + EVP on AA 2007: business $790 on that flight | yes |
| nettle-brook | 5 days < 7, Manager's late exception on file: book WN $179 | yes |
| oriole-fen | EVP approved first, CEO notified: JL first $10,600 | yes |
| plover-dune | Hawaii is domestic (193-195): coach; UA via LAX $584 (one stop) | yes |
| quince-ridge | $750 is in $501-$750: Director suffices; AA $241 | yes |
| rowan-glade | Dec 27 to Jan 3 = 7 days, "at least seven": no exception; WN $223; 6 people is not a group | yes |
| sedge-harbor | AA $924 vs AF $869: frequent flyer may not add cost; AF; miles upgrade is the traveller's own | yes |
| thistle-bay | family holiday is not business travel: refuse | yes |
| umber-wren | spouse is a non-employee (1203): refuse | yes |

Flags (not blind-read, by design): `vale-crocus` (phrase "from the point of origin to the first destination
point"), `willow-shoal` (the "(i.e., ... more than a 2-hour extension ...)" parenthesis), `yarrow-fern`
(approval required: $751 with a Director).

## Unsure

- `birch-quarry`, `fable-wharf`, `maple-cove`, `oriole-fen`: a strict reader could hold that "the lowest logical
  airfare is always required" (635) makes even a permitted business seat economy. I read lines 647/651/1151 as the
  specific permissions "within travel policy" and accept only the premium fare.
- `yarrow-fern` / `quince-ridge`: a reader who applies Table 2 to the airfare alone ($241) would book under the
  Director. The `trip_estimate_cents` description says it is the amount the sign-off was asked for, and Table 2 is
  headed "approvals required for travel expenses", so I kept the whole-trip reading.
- The EVP definition (lines 197-201, "Business Unit/Division Vice President reporting directly to the Chief
  Executive Officer") is not tested: every EVP in the trip records has that exact title role.

## Template change requests

None needed. (Observation only: `instantiate.py` leaves Thornton wording in `product/product.yaml`,
`pyproject.toml` description and `README.md`; they were rewritten here.)

## Acceptance outputs

```
$ uv run pytest -q
204 passed in 1.76s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 4ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .
exit 0 (manifest, 4 tools, 3 tasks printed)
$ nanoagent plugin pack . /tmp/goodman-networks-flight-policy.tar.gz
packed . into /tmp/goodman.tar.gz (164046 bytes)
$ python ../_template/tools/stock_verify.py .
aspen-tarn           right=True score=1.00 identical=True wrong-decision-rejected=True
birch-quarry         right=True score=1.00 identical=True wrong-decision-rejected=True
cinder-moss          right=True score=1.00 identical=True wrong-decision-rejected=True
dove-heath           right=True score=1.00 identical=True wrong-decision-rejected=True
elder-pike           right=True score=1.00 identical=True wrong-decision-rejected=True
fable-wharf          right=True score=1.00 identical=True wrong-decision-rejected=True
gorse-lantern        right=True score=1.00 identical=True wrong-decision-rejected=True
hazel-rook           right=True score=1.00 identical=True wrong-decision-rejected=True
iris-spindle         right=True score=1.00 identical=True wrong-decision-rejected=True
jade-copse           right=True score=1.00 identical=True wrong-decision-rejected=True
kiln-sorrel          right=True score=1.00 identical=True wrong-decision-rejected=True
lark-basin           right=True score=1.00 identical=True wrong-decision-rejected=True
maple-cove           right=True score=1.00 identical=True wrong-decision-rejected=True
nettle-brook         right=True score=1.00 identical=True wrong-decision-rejected=True
oriole-fen           right=True score=1.00 identical=True wrong-decision-rejected=True
plover-dune          right=True score=1.00 identical=True wrong-decision-rejected=True
quince-ridge         right=True score=1.00 identical=True wrong-decision-rejected=True
rowan-glade          right=True score=1.00 identical=True wrong-decision-rejected=True
sedge-harbor         right=True score=1.00 identical=True wrong-decision-rejected=True
thistle-bay          right=True score=1.00 identical=True wrong-decision-rejected=True
umber-wren           right=True score=1.00 identical=True wrong-decision-rejected=True
vale-crocus          right=True score=1.00 identical=True wrong-decision-rejected=True
willow-shoal         right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-fern          right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
