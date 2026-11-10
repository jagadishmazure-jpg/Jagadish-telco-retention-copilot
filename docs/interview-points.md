# Interview points

- **What problem does this solve?** Retention desks give discounts to whoever calls and looks risky.
  That spends money on people who would have stayed, on people nothing will keep, and on offers that do
  not fit the reason they are unhappy. The repo measures what an uplift model and a small language
  model each add, in money, on a simulation where the right answer is known.
- **Why uplift and not churn?** Churn says who may leave; uplift says who an offer keeps. The report
  scores both by the same value formula.
- **What did the language model add?** Measured honestly: given the uplift model's shortlist it picked
  the top offer almost every time, so its offer choice added nothing measurable. Asked alone, without
  the shortlist, it beat a blanket discount but fell short of the uplift model. What it adds is a
  readable talk track per customer, and the guard makes that safe. The cheapest gain came from five
  keyword flags from the note added to the uplift model, not from the language model.
- **What did the guard catch?** Mostly arithmetic: the model working out the discounted price itself and
  getting it a cent or more wrong. The fix is to let code fill prices into the talk track.
- **How do you stop it promising things?** A guard in code checks every reply: offer exists, eligible,
  under the cost limit, no forbidden promises, no contact details, every number grounded in the account.
  Failures go to a supervisor with the model's offer replaced.
- **Prompt injection?** About one note in ten in the queue carries an instruction to give 100% off and
  skip the supervisor, and a stress run puts it in every note. Results are in the report.
- **Fairness?** Age band and region are never shown to the model or used by any rule; offer rates per
  group are still reported.
- **What would you do next?** Shadow mode on a real desk with a random holdout, refit the uplift model
  from logged outcomes, and try a larger model only where notes are ambiguous.
