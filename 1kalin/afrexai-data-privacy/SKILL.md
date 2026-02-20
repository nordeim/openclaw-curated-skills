# Data Privacy Compliance Framework

Generate complete data privacy programs covering GDPR, CCPA/CPRA, LGPD, POPIA, and PIPL. From data mapping to breach response — everything a DPO or compliance team needs.

## When to Use
- Building or auditing a privacy program
- Mapping personal data flows across systems
- Preparing for regulatory audits (ICO, CNIL, FTC)
- Creating Data Protection Impact Assessments (DPIAs)
- Drafting privacy policies, consent flows, or DSR procedures

## What You Generate

### 1. Data Inventory & Mapping
```
For each system/process, document:
- Data Category: [identifiers | financial | health | biometric | behavioral | location]
- Lawful Basis: [consent | contract | legitimate interest | legal obligation | vital interest | public task]
- Data Subjects: [customers | employees | prospects | vendors | minors]
- Storage Location: [cloud provider + region]
- Retention Period: [specific timeframe + justification]
- Cross-Border Transfer: [mechanism: SCC | BCR | adequacy | derogation]
- Processor/Controller: [role + DPA status]
```

### 2. Privacy Impact Assessment (DPIA)
Run a DPIA when processing involves:
- Systematic monitoring of public areas
- Large-scale processing of special categories
- Automated decision-making with legal effects
- New technology deployment
- Cross-border data transfers post-Schrems II

**Risk Scoring Matrix:**
| Likelihood | Impact | Risk Level | Action Required |
|-----------|--------|------------|-----------------|
| High | High | Critical | Stop. Consult DPA before proceeding |
| High | Medium | High | Implement additional safeguards, document justification |
| Medium | Medium | Medium | Standard controls + monitoring |
| Low | Low | Low | Document and proceed |

### 3. Data Subject Rights (DSR) Procedures
| Right | GDPR | CCPA/CPRA | Timeline | Process |
|-------|------|-----------|----------|---------|
| Access | Art. 15 | §1798.100 | 30 days (GDPR) / 45 days (CCPA) | Identity verification → data compilation → secure delivery |
| Deletion | Art. 17 | §1798.105 | 30 days / 45 days | Verify → check exemptions → delete across all systems → confirm |
| Portability | Art. 20 | §1798.100 | 30 days / 45 days | Export in machine-readable format (JSON/CSV) |
| Rectification | Art. 16 | §1798.106 | 30 days / 45 days | Verify identity → update records → notify processors |
| Opt-Out (Sale) | N/A | §1798.120 | 15 business days | "Do Not Sell" link → suppress from sale/sharing |
| Restrict Processing | Art. 18 | N/A | Without undue delay | Flag records → limit to storage only |

**Response template:**
```
Subject: Your Data Request — Reference [DSR-YYYY-####]

We received your [access/deletion/correction] request on [date].

Action taken: [description]
Completion date: [date]
Data affected: [categories]

If any data was exempt from [deletion/access], the legal basis is: [exemption + explanation].

Questions? Contact our DPO at [email].
```

### 4. Consent Management Framework
```
Valid consent requires ALL of:
☐ Freely given (no service denial for refusal, except where necessary)
☐ Specific (per-purpose, not bundled)
☐ Informed (plain language, named controller, purposes, rights)
☐ Unambiguous (affirmative action, no pre-ticked boxes)
☐ Withdrawable (as easy as giving consent)
☐ Documented (timestamp, version, method, scope)

Cookie/tracking consent tiers:
- Strictly Necessary: No consent needed (session, security, load balancing)
- Functional: Opt-in recommended (preferences, language)
- Analytics: Opt-in required in EU/UK (Google Analytics, Mixpanel)
- Marketing: Opt-in required everywhere (retargeting, cross-site tracking)
```

### 5. Breach Response Playbook
**72-Hour Timeline (GDPR Art. 33):**

| Hour | Action | Owner |
|------|--------|-------|
| 0-1 | Contain breach, preserve evidence, activate IR team | Security Lead |
| 1-4 | Assess scope: what data, how many subjects, ongoing? | DPO + Security |
| 4-12 | Determine notification obligations by jurisdiction | Legal + DPO |
| 12-24 | Draft supervisory authority notification | DPO |
| 24-48 | Draft individual notifications if high risk | Comms + Legal |
| 48-72 | Submit SA notification, begin individual notifications | DPO |
| 72+ | Ongoing remediation, root cause analysis, control updates | All |

**Notification decision tree:**
1. Is personal data involved? → No = no notification required
2. Is there a risk to rights/freedoms? → No = document internally only
3. Is the risk HIGH? → No = notify SA only (72 hrs)
4. High risk confirmed → Notify SA (72 hrs) AND individuals (without undue delay)

### 6. Vendor Privacy Assessment
Before engaging any processor/sub-processor:
```
☐ DPA signed with Art. 28 GDPR clauses (or CCPA service provider addendum)
☐ Technical measures verified (encryption at rest + transit, access controls)
☐ Sub-processor list reviewed and approved
☐ Data residency confirmed (adequate jurisdiction or transfer mechanism)
☐ Breach notification clause: ≤24 hours to controller
☐ Audit rights included
☐ Insurance: cyber liability ≥$5M (for processors handling >100K records)
☐ SOC 2 Type II or ISO 27001 current certification
☐ Deletion/return clause on contract termination
```

### 7. Cross-Border Transfer Mechanisms (Post-Schrems II)
| Mechanism | When to Use | Risk Level |
|-----------|-------------|------------|
| Adequacy Decision | Transferring to EU-approved countries (UK, Japan, Korea, etc.) | Low |
| Standard Contractual Clauses (new 2021 SCCs) | Most common — US, India, etc. | Medium — requires Transfer Impact Assessment |
| Binding Corporate Rules | Intra-group transfers for multinationals | Medium — 18+ month approval |
| Derogations (Art. 49) | One-off, necessary transfers only | High — narrow interpretation |
| EU-US Data Privacy Framework | US companies on DPF list | Low-Medium — check certification |

### 8. Privacy Program Maturity Scorecard
Rate each area 1-5:
| Area | Score | Evidence Required |
|------|-------|-------------------|
| Data Inventory | _/5 | Complete ROPA, updated quarterly |
| Lawful Basis Documentation | _/5 | Per-processing activity, reviewed annually |
| DSR Process | _/5 | <30 day response, automated where possible |
| Consent Management | _/5 | CMP deployed, audit trail, withdrawal mechanism |
| Breach Response | _/5 | Tested annually, <72hr capability proven |
| Vendor Management | _/5 | DPAs signed, annual assessments |
| Training | _/5 | Annual all-staff + role-specific |
| Cross-Border Transfers | _/5 | TIAs completed, SCCs current |
| Privacy by Design | _/5 | Integrated into SDLC, DPIAs for high-risk |
| Accountability Documentation | _/5 | Board reporting, DPO appointed, policies current |

**Scoring:**
- 40-50: Mature — ready for any audit
- 30-39: Developing — address gaps within 90 days
- 20-29: Basic — significant risk exposure
- <20: Critical — immediate remediation needed

### 9. Regulatory Fine Reference
| Regulation | Maximum Fine | Notable Examples |
|-----------|-------------|-----------------|
| GDPR | €20M or 4% global turnover | Meta €1.2B (2023), Amazon €746M (2021) |
| CCPA/CPRA | $7,500 per intentional violation | Sephora $1.2M (2022) |
| LGPD (Brazil) | 2% revenue, max R$50M | Cyrela $14K (first fine, 2021) |
| POPIA (South Africa) | R10M or imprisonment | Department of Justice R5M (2023) |
| PIPL (China) | ¥50M or 5% revenue | Didi $1.2B (2022) |

## Industry Packs
For sector-specific privacy frameworks (healthcare HIPAA + GDPR, fintech PCI + GDPR, legal privilege + GDPR), check out our deep-dive context packs:

**[AfrexAI Context Packs — $47 each](https://afrexai-cto.github.io/context-packs/)**
- Healthcare AI Pack (HIPAA + GDPR + state laws)
- Fintech AI Pack (PCI DSS + GDPR + SOX)
- Legal AI Pack (privilege rules + cross-border discovery)
- Professional Services Pack (client confidentiality + multi-jurisdiction)

**Free tools:**
- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — find where manual compliance work costs you
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — configure your AI agent stack

**Bundles:** Playbook $27 | Pick 3 $97 | All 10 $197 | Everything $247
