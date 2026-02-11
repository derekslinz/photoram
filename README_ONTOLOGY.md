# RAM++ Dual-Tree Ontology

## Overview

This ontology provides a **dual-tree classification system** for the 4,585 tags in the RAM++ vocabulary:

1. **FACETS/** - Source-of-truth organization by semantic dimensions
2. **GENRES/** - Photography-centric browsing view for end users

## Why Dual-Tree?

The ontology branches naturally map to **facets** (metadata dimensions), not genres:

- **Subject facets**: SUBJECT_PEOPLE, SUBJECT_ANIMAL, SUBJECT_OBJECT, SUBJECT_FOOD
- **Style facet**: ATTRIBUTE_STYLE (anime, cartoon, watercolor, illustration)
- **Technique facet**: TECHNICAL_PHOTO (backlight, panorama, macro)
- **Concept facet**: CONCEPT_ABSTRACT (adventure, happiness, love)
- **Visual attributes**: ATTRIBUTE_VISUAL (color, appearance descriptors)

Photography **genres** are a different dimension - they describe use cases and browsing categories. The same tag can belong to multiple facets AND genres.

## Structure

### 1. FACETS Tree (Source-of-Truth)

**Purpose**: Organize tags by semantic dimensions for search and filtering

```text
FACETS/
├── Subject/
│   ├── People (640 tags)
│   │   ├── Infants & Toddlers
│   │   ├── Children
│   │   ├── Adults
│   │   ├── Medical Professionals
│   │   └── ...
│   ├── Animals (80 tags)
│   │   ├── Mammals
│   │   ├── Birds
│   │   ├── Reptiles & Amphibians
│   │   └── ...
│   ├── Objects (2,892 tags)
│   └── Food (84 tags)
│       ├── Fruits
│       ├── Vegetables
│       ├── Baked Goods
│       └── ...
├── Scene/
│   └── Locations (244 tags)
├── Activity/
│   └── Actions (281 tags)
├── Concept/
│   └── Abstract (10 tags)
├── Visual/
│   └── Attributes (337 tags)
├── Style/
│   └── Styles (14 tags)
└── Technique/
    └── Photography (3 tags)
```

### 2. GENRES Tree (Photography-Centric View)

**Purpose**: Browse tags by photography use cases and subject matter

```
GENRES/
├── People & Portrait (643 tags)
│   └── Includes: people, roles, pets, portraits
├── Wildlife (64 tags)
│   └── Includes: wild animals in natural habitats
├── Landscape & Nature (54 tags)
│   └── Includes: mountains, forests, natural scenery
├── Architecture & Interiors (235 tags)
│   └── Includes: buildings, structures, rooms
├── Street & Documentary (30 tags)
│   └── Includes: urban scenes, street life
├── Travel (8 tags)
│   └── Includes: landmarks, destinations
├── Sports & Action (255 tags)
│   └── Includes: sports, athletics, activities
├── Food & Drink (84 tags)
│   └── Includes: food, beverages, culinary
├── Product & Commercial (26 tags)
│   └── Includes: commercial products
├── Still Life (2,828 tags)
│   └── Includes: objects, arrangements
├── Conceptual (24 tags)
│   └── Includes: abstract ideas, art styles
└── Abstract & Texture (331 tags)
    └── Includes: patterns, visual elements
```

## Coverage

| Tree | Tags Classified | Coverage |
|------|----------------|----------|
| **FACETS** | 4,585 / 4,585 | 100% |
| **GENRES** | 4,582 / 4,585 | 99.9% |

**Note**: Technical photography terms (backlight, panorama, macro) are **technique facets**, not subject genres. They don't map to GENRES but remain in FACETS/Technique.

## Cross-Referencing

Tags can appear in multiple locations:

**Example: "dog"**

- `FACETS/Subject/Animals/Mammals/dog`
- `GENRES/People & Portrait/dog` (pets often grouped with portraits)

**Example: "backlight"**

- `FACETS/Technique/Photography/backlight`
- *(no genre mapping - it's a technique, not a subject)*

## Tag Structure

### In FACETS

```json
{
  "id": 101,
  "tag": "apple",
  "threshold": 0.9,
  "facet": "SUBJECT_FOOD"
}
```

### In GENRES

```json
{
  "id": 101,
  "tag": "apple",
  "threshold": 0.9,
  "facet": "SUBJECT_FOOD",
  "genre": "Food & Drink"
}
```

## Routing Rules

### From FACETS to GENRES

| Facet Branch | Primary Genre | Exceptions |
| -------------- | --------------- | ------------ |
| SUBJECT_PEOPLE | People & Portrait | Sports keywords → Sports & Action |
| SUBJECT_ANIMAL | Wildlife | Pets (dog, cat) → People & Portrait |
| SUBJECT_FOOD | Food & Drink | - |
| SUBJECT_OBJECT | Still Life | Products → Product & Commercial Buildings → Architecture |
| SCENE_LOCATION | Architecture & Interiors | Natural scenes → Landscape & Nature Urban → Street & Documentary |
| ACTIVITY_ACTION | Sports & Action | Events (wedding, party) → People & Portrait |
| CONCEPT_ABSTRACT | Conceptual | - |
| ATTRIBUTE_VISUAL | Abstract & Texture | - |
| ATTRIBUTE_STYLE | Conceptual | - |
| TECHNICAL_PHOTO | *(no genre mapping)* | Techniques are facets only |

### High-Value Overrides

Keywords like `architecture`, `landscape`, `street`, `documentary`, `travel` force specific genre routing regardless of facet.

## Use Cases

### For Search Engines

```sql
-- Find all food-related tags
SELECT * FROM tags WHERE facet = 'SUBJECT_FOOD'

-- Find portrait photography subjects
SELECT * FROM tags WHERE genre = 'People & Portrait'

-- Filter by technique
SELECT * FROM tags 
WHERE facet_type = 'Technique' 
AND tag IN ('macro', 'panorama', 'backlight')
```

### For UI Faceted Search

```
Filters:
  Genre: [People & Portrait] [Landscape] [Wildlife] ...
  Style: [Cartoon] [Watercolor] [Illustration] ...
  Technique: [Macro] [Panorama] [Backlight] ...
  Subject Type: [People] [Animals] [Objects] ...
```

### For Smart Tagging

```python
# Suggest related tags from same genre
def suggest_tags(input_tag):
    genre = get_genre(input_tag)
    return get_tags_in_genre(genre)[:10]

# Suggest complementary techniques
def suggest_techniques(input_tag):
    facet = get_facet(input_tag)
    return get_tags_in_facet("TECHNICAL_PHOTO")
```

## Benefits

1. **Separation of Concerns**
   - FACETS = semantic metadata (what it is)
   - GENRES = browsing categories (how to use it)

2. **Multiple Dimensions**
   - Tags belong to one facet but may appear in multiple genres
   - Techniques exist as facets but don't clutter genre browsing

3. **Flexible Querying**
   - Filter by facet for precision
   - Browse by genre for discovery
   - Combine both for advanced search

4. **Maintainability**
   - Facets are auto-discovered from vocabulary
   - Genre routing uses deterministic rules
   - Easy to add new genres without changing facets

## Files

- `ontology.json` - Complete dual-tree structure
- `create_ontology.py` - Generator script
- `tags.json` - Source RAM++ vocabulary

## Regenerating

```bash
python3 create_ontology.py
```

Output:

- **FACETS tree**: 10 facet types with hierarchical subcategories
- **GENRES tree**: 12 photography genres with routed tags
- **Mapping**: Each tag knows its facet and genre (if applicable)

## Future Enhancements

1. **Multi-genre tagging** - Allow tags in multiple genres
2. **Confidence scores** - Add routing confidence for ambiguous tags
3. **Synonym expansion** - Map tag variations
4. **Deeper hierarchies** - Add more levels (e.g., Dog → Canine → Mammal)
5. **Custom genre definitions** - Allow user-defined genre rules
6. **Cross-facet relationships** - Link related tags across facets
