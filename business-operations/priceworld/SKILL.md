---
name: priceworld
description: SaaS pricing intelligence for email marketing tools (web hosting and domains planned). Query current prices, compare tools, and find hidden costs. Use when users ask about software pricing, plan comparisons, renewal costs, or budget recommendations.
---

# PriceWorld - SaaS Pricing Intelligence

Pricing data sourced from official vendor pages with last-checked dates. Answers questions about current prices, plan limits, hidden costs, and renewal pricing.

## Supported Categories

- ✅ Email marketing (Mailchimp, Kit, Beehiiv, Buttondown)
- 🔜 Web hosting (planned)
- 🔜 Domain registrars (planned)

## Commands

### Lookup Pricing

Query current pricing for a specific tool:

```
priceworld:lookup <tool>
```

Example: `priceworld:lookup mailchimp`

Returns: Plan tiers, monthly/annual prices, subscriber limits, last verified date.

### Compare Tools

Side-by-side comparison of two tools:

```
priceworld:compare <tool1> <tool2>
```

Example: `priceworld:compare mailchimp kit`

Returns: Feature and pricing comparison table.

### Find Cheapest

Find the most cost-effective option for a use case:

```
priceworld:cheapest <category> --subscribers=<count>
```

Example: `priceworld:cheapest email-marketing --subscribers=5000`

Returns: Ranked list by value for specified subscriber count.

## Data Freshness

All pricing data includes a "last checked" date and source URL. Data is sourced from official vendor pricing pages.

## Pricing Notes

- **Currency:** USD
- **Region:** US pricing
- **Annual pricing:** Shown as monthly equivalent (annual total ÷ 12)
- **Excludes:** Tax/VAT, promotional discounts, regional variations
- **Sources:** Official vendor pricing pages only

## Limitations

- Currently in beta with email marketing coverage only
- Pricing is informational — always verify on vendor site before purchasing
- Does not include enterprise/custom pricing tiers
- Not affiliated with Mailchimp, Kit, Beehiiv, Buttondown, or any listed vendors

## Privacy & Security

- This skill does not require personal information to function
- **Do not paste API keys, invoices, or account screenshots**
- Queries are processed by the assistant runtime; we do not store user queries

## Tool Aliases

- Kit = ConvertKit (rebranded 2024)

---

*PriceWorld — Pricing sourced from vendors, not marketing pages.*
