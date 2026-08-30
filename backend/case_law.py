"""Case-law metadata: single source of truth for both ingestion
(scripts/chunk_case_law.py) and runtime lookups (backend/api/routes/
sources.py's related_cases field). Per-file metadata isn't reliably
recoverable from body text alone, so it's tracked here explicitly.

`related_articles` drives the Source Explorer's "Landmark judgments"
section: looking up an article reverse-looks-up any case here whose
related_articles includes it.

IMPORTANT: CASE_METADATA must only contain cases that are actually
ingested and indexed in Pinecone. A case listed here with no
corresponding indexed content will silently break the Source Explorer's
reverse-lookup. Add an entry here only after scripts/index.py has confirmed
the case's vectors are live. Cases identified but not yet ingested go in
PENDING_CASE_METADATA below instead.
"""

CASE_METADATA = {
	"maneka_gandhi_1978": {
		"case_name": "Maneka Gandhi v. Union of India",
		"year": 1978,
		"court": "Supreme Court of India",
		"related_articles": ["21"],
	},
	"shreya_singhal_2015": {
		"case_name": "Shreya Singhal v. Union of India",
		"year": 2015,
		"court": "Supreme Court of India",
		"related_articles": ["19"],
	},
}

# Cases identified for future ingestion. NOT yet indexed — do not move an
# entry into CASE_METADATA above until scripts/index.py has confirmed it's
# actually live in Pinecone.
PENDING_CASE_METADATA = {
	"kesavananda_bharati_1973": {
		"case_name": "Kesavananda Bharati v. State of Kerala",
		"year": 1973,
		"court": "Supreme Court of India",
		"related_articles": ["368", "13", "19", "31"],
		"note": "Basic structure doctrine",
	},
	"golaknath_1967": {
		"case_name": "I.C. Golaknath v. State of Punjab",
		"year": 1967,
		"court": "Supreme Court of India",
		"related_articles": ["368", "13"],
	},
	"minerva_mills_1980": {
		"case_name": "Minerva Mills v. Union of India",
		"year": 1980,
		"court": "Supreme Court of India",
		"related_articles": ["368", "31C"],
	},
	"sr_bommai_1994": {
		"case_name": "S.R. Bommai v. Union of India",
		"year": 1994,
		"court": "Supreme Court of India",
		"related_articles": ["356"],
	},
	"puttaswamy_2017": {
		"case_name": "K.S. Puttaswamy v. Union of India",
		"year": 2017,
		"court": "Supreme Court of India",
		"related_articles": ["21"],
		"note": "Right to privacy",
	},
	"in_re_article_370_2023": {
		"case_name": "In Re: Article 370 of the Constitution",
		"year": 2023,
		"court": "Supreme Court of India",
		"related_articles": ["370", "356"],
		"note": "VERIFY during ingestion — confirm exact case title/citation before indexing",
	},
	"adr_v_election_commission_2024": {
		"case_name": "Association for Democratic Reforms v. Union of India",
		"year": 2024,
		"court": "Supreme Court of India",
		"related_articles": ["19"],
		"note": "Electoral bonds case — VERIFY exact case title/citation before indexing",
	},
	"state_of_punjab_v_davinder_singh_2024": {
		"case_name": "State of Punjab v. Davinder Singh",
		"year": 2024,
		"court": "Supreme Court of India",
		"related_articles": ["341", "342", "15", "16"],
		"note": "SC/ST sub-classification — VERIFY before indexing",
	},
	"property_owners_association_2024": {
		"case_name": "Property Owners Association v. State of Maharashtra",
		"year": 2024,
		"court": "Supreme Court of India",
		"related_articles": ["39", "31C"],
		"note": "VERIFY exact case title/citation before indexing",
	},
	"pooja_ramesh_singh_v_jk_bank_2026": {
		"case_name": "Pooja Ramesh Singh v. Jammu and Kashmir Bank Ltd. & Anr.",
		"year": 2026,
		"court": "Supreme Court of India",
		"citation": "2026 INSC 668",
		"related_articles": [],
		"note": "AI hallucinated precedents ruling. Left empty as it is not a fundamental rights case.",
	},
}