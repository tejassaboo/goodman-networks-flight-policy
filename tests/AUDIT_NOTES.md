# Independent audit: goodman-networks-flight-policy (2026-11-24)

Audited commit f1232f1 against MASTER_PLAN section 4, EDGE_CASES sections 1-3 and 5, `_template/SYNC_NOTES.md`
(including 4'), and the defect classes that the paid runs found (`validation_2026-11-24/VALIDATION.md` and the
lsu-pm13, njc-v328 and anixter `REVALIDATION_NOTES.md`). I read the frozen handbook myself
(`pilot_work/originals/goodman-networks/frozen/goodman-networks_policy.txt`). For each scenario I worked out the
answer from the handbook and the `get_trip` / `search_flights` outputs only, not from `rules.py`.

## Verdict

**Pass after fixes.** On every scenario my reading agrees with the key's decision and offer. The defects below
were accept-set gaps, request wording and one world fact. None changes a decision, and every scenario keeps its
id, category and twin.

## Defects found and fixed

| Scenario(s) | Class | Problem | Fix |
|---|---|---|---|
| sedge-harbor | request names only a banned choice, with no fallback (Anixter zinnia-loch) | "Please book American though": the key books Air France, and nothing in the request says what to do if American is not possible | The request adds "If American isn't possible, book what the policy allows; I have to be at the review." |
| elder-pike, lark-basin, plover-dune, gorse-lantern (+ twin fable-wharf) | same class, for a cabin the policy denies | A business request with no fallback, and the key is economy. Anixter's denied-business requests state a fallback | Each request adds "economy is fine; I have to be there". In fable-wharf, where business is allowed, it changes nothing and keeps the twins identical |
| fable-wharf, gorse-lantern | task text echoes a threshold; same-day timing | "It's about a six-hour flight" repeats line 643/647's six hours. "I have to present the morning I land" makes the 05:40 against 07:15 landing matter (line 623, "accommodates the ... needs") | Now "It's a long overnight flight and I present the afternoon I land" |
| lark-basin | task text echoes a threshold | "well over six hours of flying" | Now "a long day of flying" |
| nettle-brook | ambiguous same-day arrival with no deadline (LSU tupelo-wren) | "drive test to Monday the 15th ... Dallas to Denver that morning" gave no start time | The test is now "Monday afternoon". The traveller asks to leave "around 8" (`requested_departure` 08:00), and the 12:10 American fare drops to $169, outside the window. Key unchanged (WN 09:05 $179). It also accepts OUTSIDE_REQUESTED_TIME_WINDOW and cites lines 697-705. This also covers the baseline target below |
| kiln-sorrel (+ twin jade-copse) | second reading of a clause | Line 705 says "Departure/arrival must be no more than 2 hours before and 2 hours after the requested time". Read as "either end", the 06:45 flight (lands 08:45) is inside the window, and at $229 it beat the keyed 08:15 at $259 | The 06:45 fare is now $269 in both twins. Both readings give 08:15 (kiln) and 11:00 (jade). The twins still differ in one fact (11:00 against 11:05) |
| thistle-bay | clause a right answer can use | With OUTSIDE_POLICY_SCOPE accepted, SCOPE (line 89, "covers all business travel activity") was not | SCOPE added, with must_keep line 89 |
| umber-wren | reason a right answer can use | The companion's trip is not company business for her | PERSONAL_TRAVEL_NOT_COVERED added |
| vale-crocus, willow-shoal | approver a right hold can name | Line 329 sends exceptions "through their respective EVP organization, in addition to the CFO and/or CEO", but the unclear holds accepted only NOT_NAMED, TRAVEL_DEPARTMENT and the trip's signer | `rules.UNCLEAR_ROLES` adds EXECUTIVE_VP, CHIEF_FINANCIAL_OFFICER and CHIEF_EXECUTIVE, with must_keep line 329. NONE is still never accepted on a hold (4') |

**Coordinator target, always-cheapest baseline:** it passed 11 and now passes 10 (nettle-brook dropped out). The
10 are aspen-tarn, dove-heath, elder-pike, gorse-lantern, iris-spindle, lark-basin, plover-dune, quince-ridge,
rowan-glade and sedge-harbor. `MAX_PASS_ALWAYS_LOWEST = 10`. The always-flag baseline still passes 2
(`MAX_PASS_ALWAYS_FLAG = 2`). The category mix (5/6/4/2/2/2/3) and the overlay counts are unchanged.

## The builder's "unsure" items, decided

- **yarrow-fern: whole trip against airfare only (Table 2).** I kept it as an approval hold, not an unclear
  flag. Line 355 needs authorization "for all travel prior to booking any travel arrangements". Line 363 says
  "All travel must be approved based on ... approval hierarchy levels". Table 2 is "the hierarchy of approvals
  required for travel expenses". The trip record states that `trip_estimate_cents` is "the amount the trip's
  sign-off was asked for", and the request says the director "signed off on the trip". An airfare-only reading
  ($241 against the Manager row) leans on the "$1,200 + or first class tickets" row. But that row is a separate
  CEO-notification line, and the reading ignores the stated sign-off amount. It is a minority reading, not an
  equally defensible one. A one-fact 750/751 twin cannot be made robust to it either, because the trip estimate
  always includes the fare. Residual risk: if a paid run books yarrow-fern for that reason, read it as a model
  slip unless the reasoning cites the ticket row.
- **Premium cabins against "the lowest logical airfare is always required" (line 635)** in birch-quarry,
  fable-wharf, maple-cove and oriole-fen. Only the premium fare stays accepted. Line 635 opens "Within travel
  policy" and points to 7.4, whose criteria are routing and time window, not cabin. The strict reading would make
  lines 647, 651 and 1151 permissions that could never be used. EDGE_CASES 3.17 (permission is not obligation)
  says the request decides. In maple-cove the CEO's approval (line 1151, which line 691 points to) is on file. In
  oriole-fen the EVP's first-class approval and the CEO notification (line 651) are both on file.
- **CEO notification.** Reading it as notice, not approval, is right. Table 2 calls the row "Notification", and
  line 319 has the travel department "notifying management through CEO level" after the fact. Residual risk: a
  model may hold a trip of $1,200 or more for CEO notice (birch-quarry, dove-heath, fable-wharf, gorse-lantern,
  lark-basin, sedge-harbor, vale-crocus). Treat that as a model slip.

## Checked and left alone

- Flags. vale-crocus ("from the point of origin to the first destination point") is unclear, and one offer also
  sells business on the domestic hop. willow-shoal (the "(i.e., ...)" parenthesis of line 707) is unclear too.
  Both readings give different bookings in each, and the clear twins sit on both sides (birch-quarry and
  lark-basin; hazel-rook and iris-spindle). lark-basin does not hinge on the vale-crocus phrase: line 643 puts
  every one of its segments, each six hours or less, in coach.
- Twins: 361/360 minutes, $99/$100, 11:00/11:05 and $750/$751 each differ in one fact. Flight numbers differ
  between jade-copse and kiln-sorrel, which is immaterial.
- iris-spindle / hazel-rook: "I'd much rather take the nonstop" is a preference, so the connection is an
  acceptable fallback. willow-shoal is a hold over either offer.
- No unclear hold here also awaits a sign-off, so none needs APPROVAL_REQUIRED beside UNCLEAR_POLICY_TEXT.
- Task instructions and tool descriptions pass the lint. The requests no longer repeat a handbook threshold.
  "almost seven hours" in elder-pike is not the seven-day rule, and "only a week out" in rowan-glade is the
  traveller's own distractor.

## Files changed

`tests/build_scenarios.py` and the 13 regenerated scenario JSON files: elder-pike, fable-wharf, gorse-lantern,
jade-copse, kiln-sorrel, lark-basin, nettle-brook, plover-dune, sedge-harbor, thistle-bay, umber-wren, vale-crocus
and willow-shoal. Also `src/plugin/rules.py` = `verifier/rules.py` (byte-identical), `tests/plugin_spec.py` and
`README.md`. `BUILD_NOTES.md` moved to `tests/`, because stock `plugin inspect` rejects extra root files.
`world.py` is untouched. The pinned searches changed only in jade-copse and kiln-sorrel (one fare) and
nettle-brook (one fare, and its background fares rescale with it).

## Acceptance outputs

```
$ uv run pytest -q
204 passed
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .            (nanoagent/nanoagent/.venv/bin/nanoagent)
exit 0
$ nanoagent plugin pack . <scratch>/goodman.tar.gz
packed (169874 bytes)
$ python ../_template/tools/stock_verify.py .
24 scenarios, 0 failures (every scenario right=True score=1.00 identical=True wrong-decision-rejected=True)
```
