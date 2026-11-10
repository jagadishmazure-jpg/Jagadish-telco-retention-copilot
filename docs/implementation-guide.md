# Implementation guide: adopting a retention copilot safely

For retention, CRM and data teams who want an assistant that suggests offers to desk agents.

## 1. Measure value, not churn accuracy

A good churn score says who may leave, not who an offer would keep. Score every policy by the money it
keeps minus what it spends, on customers it did not learn from, and compare with "no offer", a blanket
discount and your current playbook.

## 2. Run a randomised campaign first

Uplift needs a campaign where offers were assigned at random (or at least logged with their assignment
probabilities). Budget enough customers per offer: in this repo about 670 per offer was not enough to
beat a blanket discount, about 2,000 was.

## 3. Let the model do the reading, not the maths

The uplift model ranks offers from account data. A language model adds what only the note says: the
customer is moving abroad, the complaint is about the phone, not the price. Give it the model's
shortlist and the note, and let it pick and explain.

## 4. Guard every reply in code

Check the offer exists, is eligible and within the cost limit; block promises that are not on the menu;
strip contact details; check every number in the talk track against the account. Anything that fails
goes to a supervisor with the uplift model's offer.

## 5. Keep protected attributes out, and still measure by group

Do not give the model or the rules age, region or other protected fields. Report offer rates by group
anyway, because other fields can act as proxies.

## 6. Roll out in stages

| Stage | What the copilot does | Exit criterion |
|---|---|---|
| Shadow | Suggestion logged, agent does not see it | Net value on a holdout above the current playbook |
| Assist | Agent sees offer and talk track, chooses | Acceptance rate, guard escalation rate, complaint rate tracked |
| Default | Suggested offer pre-selected | Holdout group kept to keep measuring uplift |

## 7. Keep learning

Log every suggestion, what the agent did and the outcome. Keep a small random-offer holdout so the
uplift model can be refitted without bias.
