# Data card: simulated customer base

| Field | Value |
|---|---|
| What | Customers of a fictional mobile and broadband operator, Halvorsk Mobile |
| Generator | `retention/simulate.py`, deterministic from each customer id (SHA-256 seed); `scripts/build_data.py --check` rebuilds and compares in CI |
| Real data | None. No real customers, phone numbers, notes or companies |
| Files | `train.jsonl` (12,000 customers, account data and note only), `campaign.jsonl` (the offer each training customer got in a past randomised campaign and whether they left), `test.jsonl` (2,000 held-out customers with their hidden truth), `queue.json` (the 150 test customers the churn model ranks highest) |
| Account data | plan, contract, tenure, monthly charge, data use, dropped-call rate, support tickets, late payments, device age, autopay, discount in the last 12 months |
| Protected fields | age band and region exist so offer rates can be compared across groups; no model, rule or prompt reads them |
| Notes | one line from the last call, written to hint at the churn driver three times out of four, plus a made-up callback number; about one in ten carries an injected instruction |
| Hidden truth (test only) | churn driver (price, network, device, service, relocation, none), churn probability with and without each offer, two-year margin value, net value of each offer |

## How a customer is built

1. A hidden churn driver is drawn. It shifts the account data (price-driven customers pay more and pay
   late, network-driven ones see more dropped calls, device-driven ones have older phones).
2. Baseline churn comes from the driver, contract, tenure, late payments and autopay.
3. Each offer cuts churn by a driver-specific amount: the matching offer works well, others barely.
   Nothing keeps a customer who is leaving the country, and an offer to a settled customer makes them
   slightly more likely to shop around.
4. Net value of an offer = churn reduction x two years of margin - offer cost x chance the customer
   stays. This is the number every policy is scored on.

## Known limits

Effects are constant per driver, every customer has exactly one driver, notes are short template lines,
and the campaign is perfectly randomised. Real retention data is messier on every count. Results show
how methods compare on this simulation, not what they will earn in a real business.
