# Dual-Tree Ontology

The `ontology_dual_tree.json` provides two complementary views of the RAM++ tag taxonomy: **FACETS** (canonical hierarchy) and **GENRES** (photography-centric routing).

## Overview

This dual-tree structure addresses the need for both taxonomic accuracy and user-friendly browsing:

- **FACETS**: Canonical hierarchical structure derived directly from the deep hierarchy
- **GENRES**: Photography-centric view with intelligent routing for easier navigation

## Structure

```text
ontology_dual_tree.json
├── model: "ram_plus_plus"
├── source: HuggingFace model URL
├── description: Format description
├── format_version: "1.0"
├── statistics: Tag counts per branch/genre
├── FACETS: { Branch → Hierarchy → Tag }
└── GENRES: { Genre → Subgenre → Tag }
```

## FACETS Tree

The FACETS tree preserves the canonical hierarchy from `ontology_deep_hierarchy.json`. Each tag's hierarchy path is materialized as a nested structure.

### FACETS Structure

```text
FACETS/{Branch}/{Root}/{...}/{Leaf Tag}
```

### FACETS Example

```text
FACETS/
  ACTIVITY_ACTION/
    Activity/
      Sport/
        Ball Sport/
          baseball game
          basketball game
      Social Event/
        Ceremony/
          award ceremony
          wedding
```

### Branches

- `ACTIVITY_ACTION` (263 tags)
- `ATTRIBUTE_STYLE` (14 tags)
- `ATTRIBUTE_VISUAL` (338 tags)
- `CONCEPT_ABSTRACT` (8 tags)
- `SCENE_LOCATION` (179 tags)
- `SUBJECT_ANIMAL` (73 tags)
- `SUBJECT_FOOD` (51 tags)
- `SUBJECT_OBJECT` (3,007 tags)
- `SUBJECT_PEOPLE` (649 tags)
- `TECHNICAL_PHOTO` (3 tags)

## Total: 4,585 tags across 10 branches ##

## GENRES Tree

The GENRES tree provides a photography-centric organization that routes tags based on their semantic meaning and photographic context. This view is optimized for browsing and discovery.

### GENRES Structure

```text
GENRES/{Genre}/{Subgenre}/{Tag}
```

### GENRES Example

```text
GENRES/
  Sports & Action/
    Ball Sport/
      baseball game
      basketball game
  Events/
    Ceremony/
      award ceremony
      wedding
  People & Portrait/
    Athlete/
      baseball player
```

### Routing Rules

| Source | Condition | Genre | Example |
|--------|-----------|-------|---------|
| `ATTRIBUTE_STYLE` | Any | Digital Art & Illustration | cartoon, anime, watercolor |
| `TECHNICAL_PHOTO` | Any | Technique | HDR, long exposure |
| Any | "Sport" in hierarchy | Sports & Action | baseball game, football match |
| Any | "Social Event" in hierarchy | Events | award ceremony, wedding |
| `SUBJECT_ANIMAL` | Any | Wildlife & Nature | tiger, bird |
| Any | "Architecture" in hierarchy | Architecture & Built Environment | building, bridge |
| `SUBJECT_FOOD` | Any | Food & Culinary | pizza, sushi |
| `SUBJECT_PEOPLE` | Any | People & Portrait | portrait, face |
| Any | "Landscape" in hierarchy | Landscape & Scenic | mountain, beach |
| `SCENE_LOCATION` | Other | Places & Travel | airport, street |
| `SUBJECT_OBJECT` | Other | Objects & Still Life | car, furniture |
| `CONCEPT_ABSTRACT` | Any | Concept & Abstract | love, time |
| `ACTIVITY_ACTION` | Other | Activities & Lifestyle | cooking, reading |

### Genres

- **Objects & Still Life** (2,973 tags) - Majority of SUBJECT_OBJECT tags
- **People & Portrait** (649 tags) - Human subjects, faces, professions
- **Activities & Lifestyle** (224 tags) - Daily activities not categorized elsewhere
- **Places & Travel** (147 tags) - Locations, buildings, environments
- **Wildlife & Nature** (73 tags) - Animals and natural subjects
- **Food & Culinary** (51 tags) - Food items and dishes
- **Architecture & Built Environment** (34 tags) - Buildings and structures
- **Landscape & Scenic** (32 tags) - Natural landscapes
- **Sports & Action** (21 tags) - Sports and athletic activities
- **Events** (18 tags) - Ceremonies, celebrations, gatherings
- **Digital Art & Illustration** (14 tags) - Artistic styles
- **Concept & Abstract** (8 tags) - Abstract concepts
- **Technique** (3 tags) - Photography techniques

**Total: 4,247 tags across 13 genres** (338 tags not routed to avoid misplacement)

## Tag Metadata

Each tag includes metadata:

```json
{
  "tag_name": {
    "_meta": {
      "id": 201,                    // RAM++ model tag ID
      "threshold": 0.65,            // Confidence threshold
      "depth": 4,                   // Hierarchy depth
      "source_branch": "...",       // GENRES only: original branch
      "hierarchy": ["...", "..."]   // GENRES only: full hierarchy path
    }
  }
}
```

## Usage

### Building the Ontology

```bash
python build_dual_tree_ontology.py
```

This generates `ontology_dual_tree.json` from `ontology_deep_hierarchy.json`.

### Viewing the Ontology

```bash
# List all branches/genres
python view_dual_tree_ontology.py list facets
python view_dual_tree_ontology.py list genres

# Browse a specific path
python view_dual_tree_ontology.py browse facets ACTIVITY_ACTION
python view_dual_tree_ontology.py browse genres "Sports & Action"

# Search for tags
python view_dual_tree_ontology.py search baseball
python view_dual_tree_ontology.py search wedding genres
```

## Design Rationale

### Why Two Trees?

1. **FACETS preserves taxonomic accuracy**: The original RAM++ hierarchy represents semantic relationships that should be preserved for machine learning and ontological correctness.

2. **GENRES enables user-friendly browsing**: Photography users think in terms of genres (portrait, landscape, sports) rather than abstract branches (SUBJECT_PEOPLE, SCENE_LOCATION). The GENRES tree routes tags to intuitive categories.

3. **Routing without rewriting**: The GENRES tree is an overlay that doesn't modify the canonical hierarchy. This allows corrections and improvements to the browsing experience without affecting the underlying taxonomy.

### Routing Strategy

The routing logic prioritizes:

- Semantic meaning over structural location
- Photographic context over technical classification
- User intent over machine taxonomy

Example: "baseball game" appears in:

- **FACETS**: `ACTIVITY_ACTION → Activity → Sport → Ball Sport → baseball game`
- **GENRES**: `Sports & Action → Ball Sport → baseball game`

Both views are valid and serve different purposes.

## Coverage

- **FACETS**: 100% coverage (4,585 / 4,585 tags)
- **GENRES**: 92.6% coverage (4,247 / 4,585 tags)

The 338 unrouted tags are primarily from `ATTRIBUTE_VISUAL` and represent attributes that don't fit photography genres (e.g., "blurry", "bright", "colorful"). These are intentionally excluded from GENRES to avoid misplacement but remain accessible in FACETS.

## Version

- **Format Version**: 1.0
- **Model**: ram_plus_plus
- **Source**: [recognize-anything-plus-model](https://huggingface.co/xinyu1205/recognize-anything-plus-model)
- **Generated**: 2026-02-11

## See Also

- [`README_DEEP_HIERARCHY.md`](README_DEEP_HIERARCHY.md) - Deep hierarchy generation
- [`README_ONTOLOGY.md`](README_ONTOLOGY.md) - Original ontology structure
- [`plan.md`](plan.md) - Implementation plan
