#!/usr/bin/env python3
"""
Create a dual-tree ontology structure:
1. FACETS - Source-of-truth organization by ontology branches
2. GENRES - Photography-centric browsing view
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Optional


def load_tags(filepath: str = "tags.json") -> List[Dict]:
    """Load tags from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tags']


def tokenize(tag: str) -> List[str]:
    """Tokenize a tag into normalized tokens."""
    tag = tag.lower()
    tag = re.sub(r"[^a-z0-9 ]", " ", tag)
    return [t for t in tag.split() if len(t) > 1]


def auto_discover_keywords(tags: List[Dict]) -> Dict[str, Set[str]]:
    """Auto-discover keyword dictionaries from the RAM++ vocabulary."""
    all_tokens = []
    for t in tags:
        all_tokens.extend(tokenize(t["tag"]))
    
    freq = Counter(all_tokens)
    
    tech_words = {"hdr", "macro", "panorama", "aerial", "backlight", "closeup", 
                  "bokeh", "exposure", "rendering", "cgi"}
    
    style_words = {"anime", "cartoon", "illustration", "3d", "cg", "vector", 
                   "watercolor", "abstract", "surreal", "vintage"}
    
    scene_seeds = {"park", "beach", "forest", "room", "stadium", "street", "temple", 
                   "barn", "airport", "office", "kitchen", "bathroom", "bedroom", 
                   "restaurant", "cafe", "hospital", "school", "library", "museum",
                   "gallery", "theater", "garden", "field", "mountain", "desert",
                   "ocean", "sea", "lake", "river", "city", "village", "town"}
    scene_words = {w for w in freq if w in scene_seeds or 
                   w.endswith(("room", "park", "field", "forest", "beach", "street", 
                              "stadium", "store", "shop", "market"))}
    
    activity_words = {w for w in freq if w.endswith("ing") and len(w) > 4}
    activity_words.update({"game", "match", "race", "ceremony", "festival", "meeting", 
                          "auction", "sport", "dance", "play", "work", "celebration",
                          "wedding", "party", "concert", "show", "performance"})
    
    role_suffixes = ("er", "or", "ist", "man", "woman")
    people_words = {w for w in freq if any(w.endswith(s) for s in role_suffixes)}
    people_words.update({"baby", "adult", "child", "teen", "boy", "girl", "person", 
                        "people", "family", "couple", "crowd", "group", "male", 
                        "female", "bride", "groom", "student", "actor", "actress"})
    
    animal_words = {"dog", "cat", "bird", "bear", "tiger", "lion", "elephant", 
                   "giraffe", "zebra", "horse", "cow", "pig", "sheep", "goat",
                   "chicken", "duck", "goose", "eagle", "hawk", "owl", "parrot",
                   "fish", "shark", "whale", "dolphin", "snake", "lizard", "frog",
                   "deer", "wolf", "fox", "rabbit", "squirrel", "monkey", "ape"}
    
    food_words = {"food", "meal", "dish", "bread", "juice", "fruit", "vegetable", 
                 "meat", "beer", "wine", "cake", "rice", "fish", "apple", "banana",
                 "orange", "pizza", "pasta", "salad", "sandwich", "burger", "soup",
                 "dessert", "chocolate", "coffee", "tea", "cheese", "chicken"}
    
    object_words = {"car", "truck", "vehicle", "phone", "computer", "camera", 
                   "furniture", "chair", "table", "sofa", "bed", "lamp", "clock",
                   "book", "bottle", "cup", "plate", "bowl", "bag", "box",
                   "tool", "machine", "building", "house", "tower", "bridge"}
    
    attribute_words = {w for w in freq if w.endswith(("y", "ful", "ous", "ive", "al")) and len(w) > 4}
    attribute_words.update({"old", "young", "ancient", "modern", "new", "beautiful", 
                           "natural", "red", "blue", "green", "yellow", "white", "black",
                           "large", "small", "big", "tiny", "bright", "dark", "light"})
    
    concept_words = {"love", "success", "adventure", "freedom", "balance", "award", 
                    "achievement", "happiness", "joy", "emotion", "idea", "concept",
                    "symbol", "peace", "hope", "dream", "future", "past"}
    
    return {
        "TECHNICAL_PHOTO": tech_words,
        "ATTRIBUTE_STYLE": style_words,
        "ACTIVITY_ACTION": activity_words,
        "SCENE_LOCATION": scene_words,
        "SUBJECT_PEOPLE": people_words,
        "SUBJECT_ANIMAL": animal_words,
        "SUBJECT_FOOD": food_words,
        "SUBJECT_OBJECT": object_words,
        "ATTRIBUTE_VISUAL": attribute_words,
        "CONCEPT_ABSTRACT": concept_words
    }


def classify_tag(tag: str, keywords: Dict[str, Set[str]]) -> str:
    """Classify a tag into an ontology branch (FACET)."""
    tokens = tokenize(tag)
    
    if any(t in keywords["TECHNICAL_PHOTO"] for t in tokens):
        return "TECHNICAL_PHOTO"
    if any(t in keywords["ATTRIBUTE_STYLE"] for t in tokens):
        return "ATTRIBUTE_STYLE"
    if any(t in keywords["ACTIVITY_ACTION"] for t in tokens):
        return "ACTIVITY_ACTION"
    if any(t in keywords["SCENE_LOCATION"] for t in tokens):
        return "SCENE_LOCATION"
    if any(t in keywords["SUBJECT_PEOPLE"] for t in tokens):
        return "SUBJECT_PEOPLE"
    if any(t in keywords["SUBJECT_ANIMAL"] for t in tokens):
        return "SUBJECT_ANIMAL"
    if any(t in keywords["SUBJECT_FOOD"] for t in tokens):
        return "SUBJECT_FOOD"
    if any(t in keywords["ATTRIBUTE_VISUAL"] for t in tokens):
        return "ATTRIBUTE_VISUAL"
    if any(t in keywords["CONCEPT_ABSTRACT"] for t in tokens):
        return "CONCEPT_ABSTRACT"
    
    return "SUBJECT_OBJECT"


def classify_genre(tag: str, facet_branch: str) -> str:
    """
    Route a tag to a photography GENRE based on its facet branch and tag content.
    This creates a browsing-oriented view over the ontology.
    """
    tag_lower = tag.lower()
    
    # High-value genre-defining overrides
    genre_overrides = {
        # Architecture
        'architecture': 'Architecture & Interiors',
        'building': 'Architecture & Interiors',
        'skyscraper': 'Architecture & Interiors',
        'tower': 'Architecture & Interiors',
        'bridge': 'Architecture & Interiors',
        'cathedral': 'Architecture & Interiors',
        'church': 'Architecture & Interiors',
        'temple': 'Architecture & Interiors',
        'mosque': 'Architecture & Interiors',
        
        # Landscape
        'landscape': 'Landscape & Nature',
        'mountain': 'Landscape & Nature',
        'valley': 'Landscape & Nature',
        'canyon': 'Landscape & Nature',
        'forest': 'Landscape & Nature',
        'beach': 'Landscape & Nature',
        'ocean': 'Landscape & Nature',
        'sunset': 'Landscape & Nature',
        'sunrise': 'Landscape & Nature',
        
        # Street & Documentary
        'street': 'Street & Documentary',
        'urban': 'Street & Documentary',
        'city': 'Street & Documentary',
        'graffiti': 'Street & Documentary',
        'documentary': 'Street & Documentary',
        
        # Travel
        'travel': 'Travel',
        'tourist': 'Travel',
        'vacation': 'Travel',
        'landmark': 'Travel',
        
        # Product & Commercial
        'product': 'Product & Commercial',
        'commercial': 'Product & Commercial',
        'advertisement': 'Product & Commercial',
        'packaging': 'Product & Commercial',
        
        # Still Life
        'still life': 'Still Life',
        'arrangement': 'Still Life',
        'vase': 'Still Life',
        'bouquet': 'Still Life',
    }
    
    # Check overrides first
    for keyword, genre in genre_overrides.items():
        if keyword in tag_lower:
            return genre
    
    # Route based on facet branch
    if facet_branch == "SUBJECT_PEOPLE":
        # Check for sports/action signals
        if any(kw in tag_lower for kw in ['sport', 'athlete', 'runner', 'player', 'game']):
            return 'Sports & Action'
        # Check for documentary/street signals
        elif any(kw in tag_lower for kw in ['street', 'protest', 'crowd', 'rally']):
            return 'Street & Documentary'
        else:
            return 'People & Portrait'
    
    elif facet_branch == "SUBJECT_ANIMAL":
        # Check if it's a pet or wildlife
        if any(kw in tag_lower for kw in ['pet', 'dog', 'cat', 'domestic']):
            return 'People & Portrait'  # Pets often go with portrait photography
        else:
            return 'Wildlife'
    
    elif facet_branch == "SUBJECT_FOOD":
        return 'Food & Drink'
    
    elif facet_branch == "SCENE_LOCATION":
        # Interior vs exterior
        if any(kw in tag_lower for kw in ['room', 'interior', 'kitchen', 'bedroom', 'bathroom', 'office', 'lobby']):
            return 'Architecture & Interiors'
        elif any(kw in tag_lower for kw in ['mountain', 'forest', 'beach', 'ocean', 'river', 'lake', 'desert']):
            return 'Landscape & Nature'
        elif any(kw in tag_lower for kw in ['city', 'street', 'urban', 'downtown']):
            return 'Street & Documentary'
        elif any(kw in tag_lower for kw in ['museum', 'temple', 'palace', 'castle', 'monument']):
            return 'Travel'
        else:
            return 'Architecture & Interiors'
    
    elif facet_branch == "ACTIVITY_ACTION":
        # Sports vs events
        if any(kw in tag_lower for kw in ['sport', 'game', 'race', 'match', 'competition', 
                                           'soccer', 'football', 'basketball', 'tennis', 'golf']):
            return 'Sports & Action'
        elif any(kw in tag_lower for kw in ['wedding', 'party', 'festival', 'celebration', 'concert']):
            return 'People & Portrait'  # Events are often portrait-like
        else:
            return 'Sports & Action'
    
    elif facet_branch == "CONCEPT_ABSTRACT":
        return 'Conceptual'
    
    elif facet_branch == "ATTRIBUTE_VISUAL":
        return 'Abstract & Texture'
    
    elif facet_branch == "ATTRIBUTE_STYLE":
        return 'Conceptual'  # Art styles are conceptual
    
    elif facet_branch == "TECHNICAL_PHOTO":
        # Don't route technical terms to genres - they're technique facets
        return None
    
    elif facet_branch == "SUBJECT_OBJECT":
        # Products vs still life
        if any(kw in tag_lower for kw in ['product', 'package', 'bottle', 'phone', 
                                           'computer', 'camera', 'electronic']):
            return 'Product & Commercial'
        elif any(kw in tag_lower for kw in ['vase', 'bowl', 'cup', 'flower', 'candle']):
            return 'Still Life'
        elif any(kw in tag_lower for kw in ['building', 'house', 'tower', 'bridge', 'architecture']):
            return 'Architecture & Interiors'
        else:
            return 'Still Life'
    
    return None


def infer_facet_subcategory(tag: str, branch: str) -> Optional[str]:
    """Infer a subcategory within a facet branch."""
    tag_lower = tag.lower()
    
    if branch == "SUBJECT_ANIMAL":
        if any(kw in tag_lower for kw in ['dog', 'cat', 'bear', 'wolf', 'fox', 'lion', 
                                           'tiger', 'elephant', 'giraffe', 'zebra', 
                                           'horse', 'cow', 'pig', 'sheep', 'deer',
                                           'rabbit', 'squirrel', 'monkey', 'ape', 'whale', 
                                           'dolphin', 'seal', 'walrus']):
            return "Mammals"
        elif any(kw in tag_lower for kw in ['bird', 'eagle', 'hawk', 'owl', 'parrot', 
                                             'duck', 'goose', 'chicken', 'turkey', 
                                             'peacock', 'penguin', 'flamingo', 'swan',
                                             'crow', 'raven', 'sparrow', 'robin']):
            return "Birds"
        elif any(kw in tag_lower for kw in ['snake', 'lizard', 'turtle', 'tortoise', 
                                             'crocodile', 'alligator', 'frog', 'toad',
                                             'salamander', 'iguana', 'gecko']):
            return "Reptiles & Amphibians"
        elif any(kw in tag_lower for kw in ['fish', 'shark', 'salmon', 'tuna', 
                                             'goldfish', 'octopus', 'jellyfish', 
                                             'squid', 'crab', 'lobster']):
            return "Fish & Aquatic"
        elif any(kw in tag_lower for kw in ['insect', 'butterfly', 'bee', 'beetle', 
                                             'spider', 'ant', 'fly', 'mosquito',
                                             'dragonfly', 'grasshopper', 'cricket']):
            return "Insects & Arthropods"
        return "Other Animals"
    
    elif branch == "SUBJECT_FOOD":
        if any(kw in tag_lower for kw in ['apple', 'banana', 'orange', 'grape', 
                                           'strawberry', 'berry', 'melon', 'peach',
                                           'pear', 'plum', 'cherry', 'lemon', 'lime']):
            return "Fruits"
        elif any(kw in tag_lower for kw in ['vegetable', 'carrot', 'tomato', 'potato', 
                                             'onion', 'pepper', 'lettuce', 'broccoli',
                                             'cabbage', 'cucumber', 'spinach']):
            return "Vegetables"
        elif any(kw in tag_lower for kw in ['meat', 'beef', 'pork', 'chicken', 'fish',
                                             'lamb', 'steak', 'bacon', 'sausage']):
            return "Meat & Protein"
        elif any(kw in tag_lower for kw in ['bread', 'cake', 'pie', 'cookie', 'pastry',
                                             'donut', 'muffin', 'bagel', 'croissant']):
            return "Baked Goods"
        elif any(kw in tag_lower for kw in ['drink', 'juice', 'coffee', 'tea', 'beer',
                                             'wine', 'cocktail', 'soda', 'water']):
            return "Beverages"
        elif any(kw in tag_lower for kw in ['pizza', 'pasta', 'salad', 'sandwich',
                                             'burger', 'soup', 'sushi', 'taco']):
            return "Prepared Dishes"
        return "Other Foods"
    
    elif branch == "SUBJECT_PEOPLE":
        if any(kw in tag_lower for kw in ['baby', 'infant', 'toddler']):
            return "Infants & Toddlers"
        elif any(kw in tag_lower for kw in ['child', 'kid', 'boy', 'girl']):
            return "Children"
        elif any(kw in tag_lower for kw in ['teen', 'teenager', 'adolescent']):
            return "Teenagers"
        elif any(kw in tag_lower for kw in ['adult', 'man', 'woman', 'male', 'female']):
            return "Adults"
        elif any(kw in tag_lower for kw in ['senior', 'elderly', 'old']):
            return "Seniors"
        elif any(kw in tag_lower for kw in ['doctor', 'nurse', 'surgeon', 'physician']):
            return "Medical Professionals"
        elif any(kw in tag_lower for kw in ['teacher', 'professor', 'instructor', 'student']):
            return "Education Professionals"
        elif any(kw in tag_lower for kw in ['chef', 'cook', 'baker', 'waiter']):
            return "Food Service Workers"
        elif any(kw in tag_lower for kw in ['artist', 'painter', 'sculptor', 'photographer']):
            return "Artists & Creatives"
        elif any(kw in tag_lower for kw in ['athlete', 'player', 'runner', 'swimmer']):
            return "Athletes"
        elif any(kw in tag_lower for kw in ['worker', 'employee', 'manager', 'executive']):
            return "Business Professionals"
        return "People"
    
    # Add more facet subcategories as needed
    return None


def build_dual_tree_ontology(tags: List[Dict]) -> Dict:
    """
    Build dual-tree structure:
    1. FACETS - Source-of-truth by ontology branches
    2. GENRES - Photography-centric browsing view
    """
    print("Auto-discovering keyword dictionaries from RAM++ vocabulary...")
    keywords = auto_discover_keywords(tags)
    
    for branch, words in keywords.items():
        print(f"  {branch}: {len(words)} keywords discovered")
    print()
    
    # Classify each tag
    facets = defaultdict(list)
    genres = defaultdict(list)
    
    for tag_obj in tags:
        # Strip Chinese
        clean_tag = {
            'id': tag_obj['id'],
            'tag': tag_obj['tag'],
            'threshold': tag_obj['threshold']
        }
        
        # Classify into facet
        facet_branch = classify_tag(tag_obj['tag'], keywords)
        clean_tag['facet'] = facet_branch
        facets[facet_branch].append(clean_tag)
        
        # Route to genre
        genre = classify_genre(tag_obj['tag'], facet_branch)
        if genre:
            clean_tag_with_genre = clean_tag.copy()
            clean_tag_with_genre['genre'] = genre
            genres[genre].append(clean_tag_with_genre)
    
    # Build FACETS tree with hierarchies
    print("Building FACETS tree (source-of-truth)...")
    facet_tree = []
    
    facet_info = {
        "SUBJECT_PEOPLE": ("Subject", "People", "Humans, roles, demographics"),
        "SUBJECT_ANIMAL": ("Subject", "Animals", "Animals and species"),
        "SUBJECT_OBJECT": ("Subject", "Objects", "Man-made items"),
        "SUBJECT_FOOD": ("Subject", "Food", "Edible items"),
        "SCENE_LOCATION": ("Scene", "Locations", "Places and environments"),
        "ACTIVITY_ACTION": ("Activity", "Actions", "Activities and events"),
        "CONCEPT_ABSTRACT": ("Concept", "Abstract", "Symbolic ideas"),
        "ATTRIBUTE_VISUAL": ("Visual", "Attributes", "Visual descriptors"),
        "ATTRIBUTE_STYLE": ("Style", "Styles", "Art styles and rendering"),
        "TECHNICAL_PHOTO": ("Technique", "Photography", "Technical terms")
    }
    
    for branch_name, (facet_type, facet_name, description) in facet_info.items():
        if branch_name in facets:
            # Build subcategories
            hierarchy = defaultdict(list)
            for tag_obj in facets[branch_name]:
                subcat = infer_facet_subcategory(tag_obj['tag'], branch_name)
                if subcat:
                    hierarchy[subcat].append(tag_obj)
                else:
                    hierarchy["Other"].append(tag_obj)
            
            subcategories = []
            for subcat_name in sorted(hierarchy.keys()):
                subcategories.append({
                    "name": subcat_name,
                    "count": len(hierarchy[subcat_name]),
                    "tags": sorted(hierarchy[subcat_name], key=lambda x: x['tag'])
                })
            
            facet_tree.append({
                "facet_type": facet_type,
                "facet_name": facet_name,
                "description": description,
                "branch": branch_name,
                "total_count": len(facets[branch_name]),
                "subcategories": subcategories
            })
            
            print(f"  {facet_type}/{facet_name}: {len(subcategories)} subcategories, {len(facets[branch_name])} tags")
    
    # Build GENRES tree
    print("\nBuilding GENRES tree (photography-centric view)...")
    genre_tree = []
    
    genre_descriptions = {
        "People & Portrait": "Portraits, people, roles, and human subjects",
        "Wildlife": "Wild animals in natural habitats",
        "Landscape & Nature": "Natural scenery, mountains, forests, and landscapes",
        "Architecture & Interiors": "Buildings, structures, and interior spaces",
        "Street & Documentary": "Urban scenes, street life, and documentary work",
        "Travel": "Travel destinations, landmarks, and cultural sites",
        "Sports & Action": "Sports, athletics, and action photography",
        "Food & Drink": "Food, beverages, and culinary subjects",
        "Product & Commercial": "Commercial products and advertising",
        "Still Life": "Still life arrangements and compositions",
        "Conceptual": "Conceptual and artistic photography",
        "Abstract & Texture": "Abstract patterns, textures, and visual elements"
    }
    
    genre_order = [
        "People & Portrait",
        "Wildlife",
        "Landscape & Nature",
        "Architecture & Interiors",
        "Street & Documentary",
        "Travel",
        "Sports & Action",
        "Food & Drink",
        "Product & Commercial",
        "Still Life",
        "Conceptual",
        "Abstract & Texture"
    ]
    
    for genre_name in genre_order:
        if genre_name in genres:
            genre_tree.append({
                "genre": genre_name,
                "description": genre_descriptions[genre_name],
                "count": len(genres[genre_name]),
                "tags": sorted(genres[genre_name], key=lambda x: x['tag'])
            })
            print(f"  {genre_name}: {len(genres[genre_name])} tags")
    
    # Build final structure
    result = {
        "model": "RAM++ (recognize-anything-plus-model)",
        "source": "xinyu1205/recognize-anything-plus-model",
        "total_tags": len(tags),
        "description": "Dual-tree ontology: FACETS (source-of-truth) and GENRES (photography-centric view)",
        "facets": facet_tree,
        "genres": genre_tree
    }
    
    return result


def print_summary(ontology: Dict):
    """Print summary of dual-tree structure."""
    print("\n" + "="*60)
    print("DUAL-TREE ONTOLOGY SUMMARY")
    print("="*60)
    
    print(f"\nTotal tags: {ontology['total_tags']}")
    
    print(f"\nFACETS tree (source-of-truth): {len(ontology['facets'])} facet types")
    total_facet_tags = sum(f['total_count'] for f in ontology['facets'])
    for facet in ontology['facets']:
        pct = (facet['total_count'] / ontology['total_tags']) * 100
        print(f"  {facet['facet_type']}/{facet['facet_name']}: {facet['total_count']} tags ({pct:.1f}%)")
    
    print(f"\nGENRES tree (browsing view): {len(ontology['genres'])} genres")
    total_genre_tags = sum(g['count'] for g in ontology['genres'])
    for genre in ontology['genres']:
        pct = (genre['count'] / total_genre_tags) * 100 if total_genre_tags > 0 else 0
        print(f"  {genre['genre']}: {genre['count']} tags ({pct:.1f}%)")
    
    print(f"\nCoverage:")
    print(f"  FACETS: {total_facet_tags}/{ontology['total_tags']} (100%)")
    print(f"  GENRES: {total_genre_tags}/{ontology['total_tags']} ({(total_genre_tags/ontology['total_tags'])*100:.1f}%)")
    print(f"  Note: Technical terms don't map to genres (they're technique facets)")


def main():
    """Main function."""
    tags = load_tags()
    print(f"Loaded {len(tags)} tags from tags.json\n")
    
    ontology = build_dual_tree_ontology(tags)
    
    output_file = "ontology.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ontology, f, indent=2, ensure_ascii=False)
    
    print(f"\nDual-tree ontology saved to {output_file}")
    print_summary(ontology)


if __name__ == "__main__":
    main()
