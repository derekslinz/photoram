# RAM++ Deep Hierarchical Ontology

## Overview

This ontology implements **multi-level taxonomic hierarchies** for the 4,585 tags in the RAM++ vocabulary. Tags are organized in deep parent-child relationships up to 7 levels deep.

## Example Hierarchies

### Animals
```
dog → Canine → Mammal → Animal → Living Thing
cat → Feline → Mammal → Animal → Living Thing
eagle → Raptor → Bird → Animal → Living Thing
whale → Marine Mammal → Mammal → Animal → Living Thing
butterfly → Lepidoptera → Insect → Arthropod → Animal → Living Thing
spider → Arachnid → Arthropod → Animal → Living Thing
```

### Food
```
orange → Citrus → Fruit → Plant-Based Food → Food
strawberry → Berry → Fruit → Plant-Based Food → Food
beef → Red Meat → Meat → Animal-Based Food → Food
pizza → Italian Cuisine → Prepared Dish → Food
coffee → Hot Beverage → Beverage → Food
```

### People
```
baby → Infant → Child → Human → Living Thing
doctor → Doctor → Medical Professional → Professional → Adult → Human → Living Thing
teacher → Educator → Professional → Adult → Human → Living Thing
athlete → Athlete → Professional → Adult → Human → Living Thing
```

### Objects
```
car → Car → Vehicle → Man-Made Object
airplane → Aircraft → Vehicle → Man-Made Object
house → Residential Building → Building → Structure → Man-Made Object
bridge → Infrastructure → Structure → Man-Made Object
```

### Activities
```
running → Running → Athletics → Sport → Activity
swimming → Aquatic Sport → Sport → Activity
painting → Visual Art → Creative Activity → Activity
wedding → Ceremony → Social Event → Activity
```

## Hierarchy Depths

| Depth | Tag Count | Percentage | Description |
|-------|-----------|------------|-------------|
| 1 | 363 | 7.9% | Flat (no hierarchy) |
| 2 | 2,851 | 62.2% | Tag → Category |
| 3 | 713 | 15.6% | Tag → Subcategory → Category |
| 4 | 509 | 11.1% | Tag → Type → Subcategory → Category |
| 5 | 100 | 2.2% | Deep taxonomies (animals, food) |
| 6 | 43 | 0.9% | Very deep (professionals, food types) |
| 7 | 6 | 0.1% | Deepest (specific professionals) |

## Branch Distribution

| Branch | Tags | Percentage |
|--------|------|------------|
| SUBJECT_OBJECT | 3,007 | 65.6% |
| SUBJECT_PEOPLE | 649 | 14.2% |
| ATTRIBUTE_VISUAL | 338 | 7.4% |
| ACTIVITY_ACTION | 263 | 5.7% |
| SCENE_LOCATION | 179 | 3.9% |
| SUBJECT_ANIMAL | 73 | 1.6% |
| SUBJECT_FOOD | 51 | 1.1% |
| ATTRIBUTE_STYLE | 14 | 0.3% |
| CONCEPT_ABSTRACT | 8 | 0.2% |
| TECHNICAL_PHOTO | 3 | 0.1% |

## Taxonomic Structure

### Animals (SUBJECT_ANIMAL)

**Mammals:**
- Canines: dog, wolf, fox, coyote
- Felines: cat, lion, tiger, leopard, cheetah
- Ursidae: bear, panda, grizzly
- Primates: monkey, ape, gorilla, chimpanzee
- Equines: horse, zebra, donkey
- Bovines: cow, bull, buffalo, bison
- Cervidae: deer, elk, moose, reindeer
- Rodents: mouse, rat, squirrel, rabbit
- Marine Mammals: whale, dolphin, seal, walrus
- Marsupials: kangaroo, koala, opossum

**Birds:**
- Raptors: eagle, hawk, falcon, owl
- Waterfowl: duck, goose, swan, pelican
- Songbirds: sparrow, robin, crow, cardinal
- Parrots: parrot, macaw, cockatoo

**Reptiles:**
- Snakes: python, cobra, viper, boa
- Lizards: gecko, iguana, chameleon
- Turtles: turtle, tortoise
- Crocodilians: crocodile, alligator

**Amphibians:**
- Frogs, toads, salamanders

**Fish:**
- Sharks, rays, bony fish

**Invertebrates:**
- Insects: butterflies, beetles, bees
- Arachnids: spiders
- Crustaceans: crabs, lobsters
- Mollusks: octopus, squid

### Food (SUBJECT_FOOD)

**Plant-Based:**
- Citrus: orange, lemon, lime
- Berries: strawberry, blueberry, raspberry
- Stone Fruits: peach, plum, cherry
- Tropical Fruits: banana, pineapple, mango
- Leafy Vegetables: lettuce, spinach, cabbage
- Root Vegetables: carrot, potato, onion

**Animal-Based:**
- Red Meat: beef, pork, lamb
- Poultry: chicken, turkey, duck
- Seafood: fish, shrimp, lobster
- Dairy: milk, cheese, yogurt

**Prepared:**
- Bread: baguette, bagel, toast
- Pastries: cake, pie, croissant
- Italian: pizza, pasta, lasagna
- Asian: sushi, ramen, stir fry
- Fast Food: burger, sandwich, fries

**Beverages:**
- Hot Beverages: coffee, tea, espresso
- Alcoholic: beer, wine, cocktails
- Soft Drinks: juice, soda, water

### People (SUBJECT_PEOPLE)

**Age Groups:**
- Infant → Child → Human
- Toddler → Child → Human
- Child → Human
- Teenager → Human
- Adult → Human
- Senior → Adult → Human

**Professionals:**
- Medical: Doctor, Nurse → Medical Professional → Professional
- Education: Teacher, Professor → Educator → Professional
- Food Service: Chef, Cook → Food Service Worker → Professional
- Artists: Painter, Sculptor → Artist → Professional
- Performers: Actor, Musician → Performer → Professional
- Athletes: Runner, Swimmer → Athlete → Professional

### Objects (SUBJECT_OBJECT)

**Vehicles:**
- Cars: sedan, SUV, coupe
- Trucks, motorcycles, bicycles
- Aircraft: airplane, helicopter
- Watercraft: boat, ship, yacht

**Electronics:**
- Computers: laptop, desktop, monitor
- Phones: smartphone, mobile
- Cameras, tablets, devices

**Furniture:**
- Seating: chair, sofa, bench
- Tables: desk, dining table
- Storage: bed, cabinet, shelf

**Buildings:**
- Residential: house, apartment, cottage
- Commercial: office, store, restaurant
- Religious: church, temple, mosque
- Infrastructure: bridge, tower, tunnel

### Locations (SCENE_LOCATION)

**Natural Landscapes:**
- Mountains: mountain, hill, valley, canyon
- Forests: forest, jungle, rainforest
- Coastal: beach, shore, seaside
- Water Bodies: ocean, sea, lake, river
- Deserts, fields, meadows

**Urban Spaces:**
- Cities: downtown, urban areas
- Streets: road, avenue, boulevard
- Parks: playground, plaza, square

**Indoor Spaces:**
- Residential: bedroom, living room, kitchen
- Commercial: office, store, restaurant, cafe
- Public Venues: museum, gallery, theater, stadium
- Transportation Hubs: airport, station, terminal

### Activities (ACTIVITY_ACTION)

**Sports:**
- Athletics: running, jogging, sprinting
- Aquatic Sports: swimming, diving
- Cycling, winter sports
- Ball Sports: football, basketball, tennis

**Creative Activities:**
- Visual Art: painting, drawing, sketching
- Musical Performance: playing music, singing
- Dance: ballet, contemporary

**Work:**
- Labor: construction, building
- Office Work: typing, writing, reading

**Social:**
- Social Interaction: meeting, talking
- Celebrations: party, festival
- Ceremonies: wedding, ceremony

**Daily:**
- Eating, drinking, dining
- Sleeping, resting, relaxing
- Walking, hiking, strolling

## Data Structure

Each tag includes:

```json
{
  "id": 101,
  "tag": "dog",
  "threshold": 0.9,
  "branch": "SUBJECT_ANIMAL",
  "hierarchy": ["dog", "Canine", "Mammal", "Animal", "Living Thing"],
  "depth": 5
}
```

## Use Cases

### 1. Hierarchical Filtering
```python
# Find all mammals
tags_with_mammal = [t for t in tags if "Mammal" in t['hierarchy']]

# Find all living things
living_things = [t for t in tags if "Living Thing" in t['hierarchy']]

# Find all professionals
professionals = [t for t in tags if "Professional" in t['hierarchy']]
```

### 2. Parent-Child Navigation
```python
# Get parent of "dog"
dog_tag = find_tag("dog")
parent = dog_tag['hierarchy'][1]  # "Canine"

# Get all ancestors
ancestors = dog_tag['hierarchy'][1:]  # ["Canine", "Mammal", "Animal", "Living Thing"]
```

### 3. Sibling Discovery
```python
# Find all canines (siblings of dog)
canines = [t for t in tags 
           if len(t['hierarchy']) >= 2 and t['hierarchy'][1] == "Canine"]
# Result: dog, wolf, fox, coyote
```

### 4. Depth-Based Queries
```python
# Find tags with deep taxonomies (5+ levels)
deep_taxonomies = [t for t in tags if t['depth'] >= 5]

# Find flat tags (no hierarchy)
flat_tags = [t for t in tags if t['depth'] == 1]
```

### 5. Taxonomy Trees
```python
# Build tree structure
def build_tree(tags):
    tree = {}
    for tag in tags:
        node = tree
        for level in tag['hierarchy']:
            if level not in node:
                node[level] = {}
            node = node[level]
    return tree
```

## Benefits

1. **Semantic Search**
   - Query at any level: "show me all mammals" includes dogs, cats, bears, etc.
   - Navigate up/down the hierarchy

2. **Smart Filtering**
   - Filter by broad categories (Animal, Food) or specific types (Canine, Citrus)
   - Exclude unwanted branches

3. **Relationship Discovery**
   - Find related tags through common ancestors
   - Suggest similar tags from same taxonomic family

4. **Flexible Granularity**
   - Use shallow levels for browsing (Animal, Food, Human)
   - Use deep levels for precision (Canine, Citrus, Medical Professional)

5. **Knowledge Graph Ready**
   - Export to RDF, OWL, or graph databases
   - Build ontology-driven AI systems

## Files

- `ontology_deep_hierarchy.json` - Complete deep hierarchy structure
- `create_hierarchy_deep.py` - Generator script
- `tags.json` - Source RAM++ vocabulary

## Regenerating

```bash
python3 create_hierarchy_deep.py
```

Output:
- Classifies all 4,585 tags (excluding Chinese)
- Builds multi-level hierarchies (1-7 levels deep)
- Outputs structured JSON with hierarchy paths

## Future Enhancements

1. **Automated taxonomy expansion** - Learn new hierarchies from data
2. **Multiple inheritance** - Tags can have multiple parent paths
3. **Synonym mapping** - Link related terms
4. **Confidence scores** - Rate classification certainty
5. **Cross-branch relationships** - Link related concepts across branches
6. **Temporal hierarchies** - Add historical/modern distinctions
7. **Geographic hierarchies** - Add location-based taxonomies
