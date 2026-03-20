"""
Seed script — creates the initial Pulsio channel definitions.
Run once after first deploy: python -m scripts.seed_channels
"""
CHANNELS = [
    {
        "id": "ot-ics-security",
        "name": "OT/ICS Security",
        "description": "Operational technology and industrial control system security findings, CVEs, mitigations.",
        "launch_priority": 1,
    },
    {
        "id": "secrets-infra",
        "name": "Secrets & Infrastructure",
        "description": "Vault, HashiCorp, secrets management, infrastructure-as-code patterns.",
        "launch_priority": 2,
    },
    {
        "id": "cybersecurity",
        "name": "Cybersecurity",
        "description": "Threat intel, vulnerability research, incident response, detection engineering.",
        "launch_priority": 3,
    },
    {
        "id": "finance-risk",
        "name": "Finance & Risk",
        "description": "Quant strategies, market signals, credit/risk models, regulatory findings.",
        "launch_priority": 4,
    },
    {
        "id": "real-estate",
        "name": "Real Estate",
        "description": "Market data, deal analysis, STR/LTR strategies, zoning, REITs.",
        "launch_priority": 5,
    },
    {
        "id": "healthcare-ai",
        "name": "Healthcare AI",
        "description": "Clinical NLP, imaging models, compliance (HIPAA), drug discovery.",
        "launch_priority": 6,
    },
    {
        "id": "legal-ai",
        "name": "Legal AI",
        "description": "Contract analysis, case law research, compliance automation.",
        "launch_priority": 7,
    },
    {
        "id": "software-engineering",
        "name": "Software Engineering",
        "description": "Architecture patterns, code review findings, tooling, DevOps.",
        "launch_priority": 8,
    },
    {
        "id": "science-research",
        "name": "Science & Research",
        "description": "Paper summaries, reproducibility findings, cross-domain discoveries.",
        "launch_priority": 9,
    },
]

if __name__ == "__main__":
    print("Pulsio Channels:")
    for ch in sorted(CHANNELS, key=lambda x: x["launch_priority"]):
        print(f"  [{ch['launch_priority']}] #{ch['id']} — {ch['description'][:60]}")
    print(f"\nTotal: {len(CHANNELS)} channels ready to seed.")
