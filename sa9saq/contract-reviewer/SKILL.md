---
description: Detect risk clauses, summarize terms, and rate legal documents for contract review.
---

# Contract Reviewer

Analyze contracts and legal documents for risks, unusual terms, and key obligations.

## Instructions

1. **Accept input**: File path, pasted text, or URL. Supported: plain text, PDF, markdown, HTML.
2. **Analyze and flag** risk clauses in these categories:

   | Category | What to Look For |
   |----------|-----------------|
   | Liability | Caps, exclusions, indemnification |
   | Termination | Penalties, notice periods, auto-renewal |
   | IP Assignment | Broad IP transfers, work-for-hire clauses |
   | Data/Privacy | Data sharing, retention, GDPR compliance |
   | Non-compete | Scope, duration, geographic limits |
   | Dispute Resolution | Arbitration, jury waiver, venue |
   | Payment | Late fees, net terms, currency |

3. **Rate each clause**: 🟢 Standard, 🟡 Review recommended, 🔴 High risk
4. **Output format**:
   ```
   ## Summary
   One-paragraph plain-English overview of the contract.

   ## Risk Analysis
   | # | Clause | Section | Risk | Issue |
   |---|--------|---------|------|-------|
   | 1 | Auto-renewal | §4.2 | 🔴 | 2-year auto-renew with 90-day cancellation notice |
   | 2 | IP Assignment | §7.1 | 🟡 | Broad "all work product" language |

   ## Overall Risk: MEDIUM
   Key concerns: [list top 2-3]

   ## Recommended Actions
   - Negotiate §4.2 to 30-day notice
   - Narrow §7.1 to project-specific deliverables
   ```

5. **Compare contracts**: If two versions provided, highlight what changed between them

## Security

- Never store or transmit contract contents beyond the current session
- Mask sensitive parties' names in logs if requested

## ⚠️ Disclaimer

**This is AI analysis, not legal advice.** Always have important contracts reviewed by a qualified attorney.

## Requirements

- No dependencies or API keys
- For PDF parsing: `pdftotext` (from `poppler-utils`) or read as file
