"""Article category/range definitions powering the sidebar's Fundamental
Rights and Directive Principles sub-menus (Ui updates and features.md
2.2 A1). Reuses the same Pinecone article metadata already indexed —
no new ingestion needed, just a curated static index into it.

DPSP category boundaries (unlike Fundamental Rights) aren't labeled by
the Constitution's own text — different constitutional-law sources
classify a few borderline articles (47, 48) differently. This is the
one locked, chosen mapping for this app, not the only valid one.
"""

FUNDAMENTAL_RIGHTS_CATEGORIES = {
	"equality": {
		"label": "Right to Equality",
		"articles": ["14", "15", "16", "17", "18"],
	},
	"freedom": {
		"label": "Right to Freedom",
		"articles": ["19", "20", "21", "22"],
	},
	"against_exploitation": {
		"label": "Right against Exploitation",
		"articles": ["23", "24"],
	},
	"religion": {
		"label": "Freedom of Religion",
		"articles": ["25", "26", "27", "28"],
	},
	"cultural_educational": {
		"label": "Cultural and Educational Rights",
		"articles": ["29", "30"],
	},
	"constitutional_remedies": {
		"label": "Right to Constitutional Remedies",
		"articles": ["32"],
	},
}

DIRECTIVE_PRINCIPLES_CATEGORIES = {
	"socialist": {
		"label": "Socialist Principles",
		"articles": ["38", "39", "39A", "41", "42", "43", "43A"],
	},
	"gandhian": {
		"label": "Gandhian Principles",
		"articles": ["40", "43B", "46", "47", "48"],
	},
	"liberal_intellectual": {
		"label": "Liberal-Intellectual Principles",
		"articles": ["44", "45", "48A", "49", "50", "51"],
	},
}

ARTICLE_CATEGORIES = {**FUNDAMENTAL_RIGHTS_CATEGORIES, **DIRECTIVE_PRINCIPLES_CATEGORIES}
