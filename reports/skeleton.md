# Indonesia Growth and Distribution Analysis Skeleton

## 1. Show Real GDP First

Start with real GDP in local currency.

This keeps the first growth claim clean: Indonesia's economy expanded after removing the effect of inflation.

Real GDP answers: how much did the economy produce after holding prices constant?

Do not lead with nominal GDP in the main story. Nominal GDP is useful context, but it includes both real output growth and price changes.

## 2. Explain What Was Removed

Briefly explain the distinction:

- Nominal GDP measures output using the prices of each year.
- Real GDP removes the price effect, so it is better for measuring actual output growth.

Because the analysis uses local-currency real GDP, the story does not need a deep dive into US-dollar exchange-rate changes.

Mention only as a caveat: US-dollar GDP is useful for international comparison, but it can move because of rupiah-to-dollar exchange-rate movement. CPI captures domestic price changes, not currency conversion.

## 3. Show Absolute Group-Level Consumption

Use World Bank PIP percentile data to show average consumption by group.

For Indonesia, the current PIP `welfare_type` is `consumption`, so this is better than the earlier GDP-share approximation.

The chart should show:

- Bottom 40% average consumption
- Middle 40% average consumption
- Top 20% average consumption

Metric:

```text
average consumption per person per day
2017 PPP USD
```

This answers: did each broad group improve in absolute welfare terms?

Expected claim to test:

> All broad groups increased in average consumption over the period.

## 4. Then Show Distribution Shares

After showing absolute gains, show the distribution-share chart.

This answers a different question: not whether each group gained, but whether each group received a larger or smaller slice of the total.

Current interpretation:

- The bottom 40% can gain in absolute terms while still losing share.
- The middle 40% can also gain in absolute terms while losing share.
- The top 20% gains both in absolute terms and in share.

## 5. Deep Dive: Bottom 10% vs Top 10%

After the broad group chart, zoom into the tails.

Use two adjacent views:

- Bottom 10% and Top 10% average consumption
- Bottom 10% and Top 10% share of total consumption

This should make the contrast sharper than the bottom 40% / middle 40% / top 20% view.

Expected interpretation:

- The bottom 10% improved in absolute consumption.
- The top 10% also improved in absolute consumption.
- The top 10% captured a much larger share of total consumption than the bottom 10%.
- Over time, the tail-share pattern makes it clearer that richer households enjoyed more of the overall economic growth.

The wording needs to stay precise. The claim is not that the poorest got worse in absolute terms. The claim is that growth was unevenly captured.

## 6. Normative Question: Is This Good or Bad?

This is the uncomfortable question:

> Is rising inequality acceptable if the poorest people's lives are also getting better?

Economists do not have one universal answer because it depends on the standard being used.

From an absolute welfare view, it can be positive:

- If the bottom group consumes more than before, material living standards improved.
- Poverty reduction matters even if inequality rises.
- A society where everyone is better off may be preferable to one where equality improves only because richer groups fall.

From a distributional and political-economy view, it can still be a problem:

- If the rich capture most of the gains, opportunity and bargaining power may become more unequal.
- Higher inequality can reduce social mobility and make future growth less inclusive.
- The poorest may improve, but still fall further behind the living standard and influence of the rich.
- Public trust can weaken if growth feels visibly unfair.

The report should not answer this with a simple yes or no. The stronger framing is:

> Indonesia's growth appears to have improved absolute consumption across the distribution, including the poorest groups. But the gains were uneven, with the top capturing more of the expanding economic pie. Whether this is considered acceptable depends on whether the benchmark is absolute poverty reduction, proportional fairness, social mobility, or political equality.

## 7. Main Narrative

The stronger story is:

> Indonesia's real economy expanded, and broad population groups gained in average consumption. But the distribution-share data suggests the gains were not proportional. The top group captured a larger slice over time, while the bottom and middle groups received smaller shares than at the start of the period.
