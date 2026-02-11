# What to build from ontology_deep_hierarchy.json #

## FACETS tree (canonical; derived directly from hierarchy) ##

For each tag record, treat its hierarchy list as a path. Example shape shown in your deep file:
 • award ceremony → Ceremony → Social Event → Activity (depth 4)
 • baseball game → Ball Sport → Sport → Activity (depth 4)
This is exactly what you want to materialize as a hierarchical tag structure.  ￼

Rule: reverse the path into FACETS/{branch}/{top…}/{leaf_tag} (or keep the order as-is, but be consistent).

## GENRES tree (photography-centric “view”; routed) ##

Use the deep hierarchy and branch to route tags into photographic genres (without destroying the facet truth).

Practical, deterministic routing (examples grounded in ontology.json structure and tags):
 • If branch/facet is Style (ATTRIBUTE_STYLE) → GENRES/Digital Art & Illustration/... (e.g., “cartoon”, “watercolor”) ￼
 • If branch/facet is Technique (TECHNICAL_PHOTO) → GENRES/Technique/... (or keep technique only under FACETS) ￼
 • If deep hierarchy contains ... → Sport → Activity (e.g., “baseball game”, “football match”) → GENRES/Sports & Action/...  ￼
 • If deep hierarchy contains ... → Social Event → Activity (e.g., “award ceremony”) → GENRES/Events/...  ￼

This matches your existing ontology.json intent (“Dual-tree ontology: FACETS … and GENRES …”). ￼

## Why the GENRES view must be a routed overlay ##

Your ontology.json samples show significant misplacements (e.g., non-people items inside SUBJECT_PEOPLE), so treating facets as ground truth for browsing will frustrate users; using GENRES as a routed view lets you correct/override without rewriting the ontology. (The “People & Portrait” list example contains obvious non-people entries.) ￼

### Concrete output format (recommended) ####

 • FACETS/{Branch}/{Hierarchy...}/{tag}
 • GENRES/{Genre}/{optional_subgenre}/{tag}

Where {Hierarchy...} comes straight from each tag’s hierarchy path in ontology_deep_hierarchy.json.
