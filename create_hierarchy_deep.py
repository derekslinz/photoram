#!/usr/bin/env python3
"""
Create deep hierarchical ontology with multiple taxonomic levels.
Example: dog → Canine → Mammal → Animal → Living Thing
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Optional, Tuple


def load_tags(filepath: str = "tags.json") -> List[Dict]:
    """Load tags from JSON file (excluding Chinese tags)."""
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
                   "restaurant", "cafe", "hospital", "school", "library", "museum"}
    scene_words = {w for w in freq if w in scene_seeds or 
                   w.endswith(("room", "park", "field", "forest", "beach", "street", 
                              "stadium", "store", "shop", "market"))}
    
    activity_words = {w for w in freq if w.endswith("ing") and len(w) > 4}
    activity_words.update({"game", "match", "race", "ceremony", "festival", "meeting", 
                          "auction", "sport", "dance", "play", "work", "celebration"})
    
    role_suffixes = ("er", "or", "ist", "man", "woman")
    people_words = {w for w in freq if any(w.endswith(s) for s in role_suffixes)}
    people_words.update({"baby", "adult", "child", "teen", "boy", "girl", "person", 
                        "people", "family", "couple", "crowd", "group", "male", "female"})
    
    animal_words = {"dog", "cat", "bird", "bear", "tiger", "lion", "elephant", 
                   "giraffe", "zebra", "horse", "cow", "pig", "sheep", "goat",
                   "chicken", "duck", "goose", "eagle", "hawk", "owl", "parrot",
                   "fish", "shark", "whale", "dolphin", "snake", "lizard", "frog"}
    
    food_words = {"food", "meal", "dish", "bread", "juice", "fruit", "vegetable", 
                 "meat", "beer", "wine", "cake", "rice", "fish", "apple", "banana"}
    
    object_words = {"car", "truck", "vehicle", "phone", "computer", "camera", 
                   "furniture", "chair", "table", "sofa", "bed", "lamp", "clock"}
    
    attribute_words = {w for w in freq if w.endswith(("y", "ful", "ous", "ive", "al")) and len(w) > 4}
    attribute_words.update({"old", "young", "ancient", "modern", "new", "beautiful", 
                           "natural", "red", "blue", "green", "yellow", "white", "black"})
    
    concept_words = {"love", "success", "adventure", "freedom", "balance", "award", 
                    "achievement", "happiness", "joy", "emotion", "idea", "concept"}
    
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
    """Classify tag into ontology branch."""
    tokens = tokenize(tag)
    
    priority_order = [
        "TECHNICAL_PHOTO", "ATTRIBUTE_STYLE", "ACTIVITY_ACTION", "SCENE_LOCATION",
        "SUBJECT_PEOPLE", "SUBJECT_ANIMAL", "SUBJECT_FOOD", "ATTRIBUTE_VISUAL",
        "CONCEPT_ABSTRACT"
    ]
    
    for branch in priority_order:
        if any(t in keywords[branch] for t in tokens):
            return branch
    
    return "SUBJECT_OBJECT"


def build_deep_hierarchy(tag: str, branch: str) -> List[str]:
    """
    Build deep taxonomic hierarchy for a tag.
    Returns list from most specific (tag) to most general.
    Example: ["dog", "Canine", "Mammal", "Animal", "Living Thing"]
    """
    tag_lower = tag.lower()
    
    # ANIMAL HIERARCHIES
    if branch == "SUBJECT_ANIMAL":
        # Canines
        if any(kw in tag_lower for kw in ['dog', 'wolf', 'fox', 'coyote', 'jackal']):
            return [tag, "Canine", "Mammal", "Animal", "Living Thing"]
        
        # Felines
        elif any(kw in tag_lower for kw in ['cat', 'lion', 'tiger', 'leopard', 'cheetah', 
                                             'jaguar', 'cougar', 'lynx', 'panther']):
            return [tag, "Feline", "Mammal", "Animal", "Living Thing"]
        
        # Ursidae (Bears)
        elif any(kw in tag_lower for kw in ['bear', 'panda', 'grizzly', 'polar bear']):
            return [tag, "Ursidae", "Mammal", "Animal", "Living Thing"]
        
        # Primates
        elif any(kw in tag_lower for kw in ['monkey', 'ape', 'gorilla', 'chimpanzee', 
                                             'orangutan', 'baboon', 'lemur']):
            return [tag, "Primate", "Mammal", "Animal", "Living Thing"]
        
        # Equines
        elif any(kw in tag_lower for kw in ['horse', 'zebra', 'donkey', 'mule']):
            return [tag, "Equine", "Mammal", "Animal", "Living Thing"]
        
        # Bovines
        elif any(kw in tag_lower for kw in ['cow', 'bull', 'cattle', 'buffalo', 'bison']):
            return [tag, "Bovine", "Mammal", "Animal", "Living Thing"]
        
        # Cervidae (Deer)
        elif any(kw in tag_lower for kw in ['deer', 'elk', 'moose', 'reindeer', 'caribou']):
            return [tag, "Cervidae", "Mammal", "Animal", "Living Thing"]
        
        # Rodents
        elif any(kw in tag_lower for kw in ['mouse', 'rat', 'squirrel', 'hamster', 
                                             'rabbit', 'bunny', 'guinea pig']):
            return [tag, "Rodent", "Mammal", "Animal", "Living Thing"]
        
        # Marine Mammals
        elif any(kw in tag_lower for kw in ['whale', 'dolphin', 'porpoise', 'seal', 
                                             'walrus', 'otter']):
            return [tag, "Marine Mammal", "Mammal", "Animal", "Living Thing"]
        
        # Marsupials
        elif any(kw in tag_lower for kw in ['kangaroo', 'koala', 'opossum', 'wallaby']):
            return [tag, "Marsupial", "Mammal", "Animal", "Living Thing"]
        
        # Other Mammals
        elif any(kw in tag_lower for kw in ['elephant', 'giraffe', 'pig', 'sheep', 
                                             'goat', 'hippo']):
            return [tag, "Mammal", "Animal", "Living Thing"]
        
        # Raptors
        elif any(kw in tag_lower for kw in ['eagle', 'hawk', 'falcon', 'owl', 'vulture']):
            return [tag, "Raptor", "Bird", "Animal", "Living Thing"]
        
        # Waterfowl
        elif any(kw in tag_lower for kw in ['duck', 'goose', 'swan', 'pelican', 
                                             'crane', 'heron', 'stork']):
            return [tag, "Waterfowl", "Bird", "Animal", "Living Thing"]
        
        # Songbirds
        elif any(kw in tag_lower for kw in ['sparrow', 'robin', 'crow', 'raven', 
                                             'cardinal', 'finch', 'canary']):
            return [tag, "Songbird", "Bird", "Animal", "Living Thing"]
        
        # Parrots
        elif any(kw in tag_lower for kw in ['parrot', 'macaw', 'cockatoo', 'parakeet']):
            return [tag, "Parrot", "Bird", "Animal", "Living Thing"]
        
        # Other Birds
        elif any(kw in tag_lower for kw in ['bird', 'chicken', 'turkey', 'peacock', 
                                             'penguin', 'flamingo', 'ostrich']):
            return [tag, "Bird", "Animal", "Living Thing"]
        
        # Snakes
        elif any(kw in tag_lower for kw in ['snake', 'python', 'cobra', 'viper', 'boa']):
            return [tag, "Snake", "Reptile", "Animal", "Living Thing"]
        
        # Lizards
        elif any(kw in tag_lower for kw in ['lizard', 'gecko', 'iguana', 'chameleon']):
            return [tag, "Lizard", "Reptile", "Animal", "Living Thing"]
        
        # Turtles
        elif any(kw in tag_lower for kw in ['turtle', 'tortoise']):
            return [tag, "Turtle", "Reptile", "Animal", "Living Thing"]
        
        # Crocodilians
        elif any(kw in tag_lower for kw in ['crocodile', 'alligator', 'caiman']):
            return [tag, "Crocodilian", "Reptile", "Animal", "Living Thing"]
        
        # Amphibians
        elif any(kw in tag_lower for kw in ['frog', 'toad', 'salamander', 'newt']):
            return [tag, "Amphibian", "Animal", "Living Thing"]
        
        # Fish - Sharks
        elif any(kw in tag_lower for kw in ['shark', 'great white', 'hammerhead']):
            return [tag, "Shark", "Fish", "Animal", "Living Thing"]
        
        # Fish - Ray
        elif any(kw in tag_lower for kw in ['ray', 'stingray', 'manta']):
            return [tag, "Ray", "Fish", "Animal", "Living Thing"]
        
        # Other Fish
        elif any(kw in tag_lower for kw in ['fish', 'salmon', 'tuna', 'goldfish', 
                                             'trout', 'bass']):
            return [tag, "Fish", "Animal", "Living Thing"]
        
        # Cephalopods
        elif any(kw in tag_lower for kw in ['octopus', 'squid', 'cuttlefish']):
            return [tag, "Cephalopod", "Mollusk", "Animal", "Living Thing"]
        
        # Crustaceans
        elif any(kw in tag_lower for kw in ['crab', 'lobster', 'shrimp', 'prawn', 'crayfish']):
            return [tag, "Crustacean", "Arthropod", "Animal", "Living Thing"]
        
        # Insects - Butterflies & Moths
        elif any(kw in tag_lower for kw in ['butterfly', 'moth']):
            return [tag, "Lepidoptera", "Insect", "Arthropod", "Animal", "Living Thing"]
        
        # Insects - Beetles
        elif any(kw in tag_lower for kw in ['beetle', 'ladybug']):
            return [tag, "Coleoptera", "Insect", "Arthropod", "Animal", "Living Thing"]
        
        # Insects - Bees & Wasps
        elif any(kw in tag_lower for kw in ['bee', 'wasp', 'hornet']):
            return [tag, "Hymenoptera", "Insect", "Arthropod", "Animal", "Living Thing"]
        
        # Other Insects
        elif any(kw in tag_lower for kw in ['insect', 'ant', 'fly', 'mosquito', 
                                             'dragonfly', 'grasshopper']):
            return [tag, "Insect", "Arthropod", "Animal", "Living Thing"]
        
        # Spiders
        elif any(kw in tag_lower for kw in ['spider', 'tarantula']):
            return [tag, "Arachnid", "Arthropod", "Animal", "Living Thing"]
        
        # Other Animals
        return [tag, "Animal", "Living Thing"]
    
    # FOOD HIERARCHIES
    elif branch == "SUBJECT_FOOD":
        # Citrus Fruits
        if any(kw in tag_lower for kw in ['orange', 'lemon', 'lime', 'grapefruit']):
            return [tag, "Citrus", "Fruit", "Plant-Based Food", "Food"]
        
        # Berries
        elif any(kw in tag_lower for kw in ['strawberry', 'blueberry', 'raspberry', 
                                             'blackberry', 'berry']):
            return [tag, "Berry", "Fruit", "Plant-Based Food", "Food"]
        
        # Stone Fruits
        elif any(kw in tag_lower for kw in ['peach', 'plum', 'cherry', 'apricot', 'nectarine']):
            return [tag, "Stone Fruit", "Fruit", "Plant-Based Food", "Food"]
        
        # Tropical Fruits
        elif any(kw in tag_lower for kw in ['banana', 'pineapple', 'mango', 'papaya', 
                                             'coconut', 'kiwi']):
            return [tag, "Tropical Fruit", "Fruit", "Plant-Based Food", "Food"]
        
        # Other Fruits
        elif any(kw in tag_lower for kw in ['apple', 'grape', 'melon', 'watermelon', 
                                             'pear', 'fruit']):
            return [tag, "Fruit", "Plant-Based Food", "Food"]
        
        # Leafy Vegetables
        elif any(kw in tag_lower for kw in ['lettuce', 'spinach', 'cabbage', 'kale']):
            return [tag, "Leafy Vegetable", "Vegetable", "Plant-Based Food", "Food"]
        
        # Root Vegetables
        elif any(kw in tag_lower for kw in ['carrot', 'potato', 'onion', 'beet', 
                                             'radish', 'turnip']):
            return [tag, "Root Vegetable", "Vegetable", "Plant-Based Food", "Food"]
        
        # Other Vegetables
        elif any(kw in tag_lower for kw in ['vegetable', 'tomato', 'pepper', 'broccoli', 
                                             'cucumber']):
            return [tag, "Vegetable", "Plant-Based Food", "Food"]
        
        # Red Meat
        elif any(kw in tag_lower for kw in ['beef', 'pork', 'lamb', 'steak', 'bacon']):
            return [tag, "Red Meat", "Meat", "Animal-Based Food", "Food"]
        
        # Poultry
        elif any(kw in tag_lower for kw in ['chicken', 'turkey', 'duck', 'poultry']):
            return [tag, "Poultry", "Meat", "Animal-Based Food", "Food"]
        
        # Seafood
        elif any(kw in tag_lower for kw in ['fish', 'salmon', 'tuna', 'shrimp', 'lobster']):
            return [tag, "Seafood", "Animal-Based Food", "Food"]
        
        # Dairy
        elif any(kw in tag_lower for kw in ['milk', 'cheese', 'yogurt', 'butter', 'cream']):
            return [tag, "Dairy", "Animal-Based Food", "Food"]
        
        # Bread
        elif any(kw in tag_lower for kw in ['bread', 'baguette', 'roll', 'bagel', 'toast']):
            return [tag, "Bread", "Baked Goods", "Food"]
        
        # Pastries
        elif any(kw in tag_lower for kw in ['cake', 'pie', 'pastry', 'croissant', 'donut']):
            return [tag, "Pastry", "Baked Goods", "Food"]
        
        # Other Baked Goods
        elif any(kw in tag_lower for kw in ['cookie', 'muffin', 'biscuit']):
            return [tag, "Baked Goods", "Food"]
        
        # Coffee & Tea
        elif any(kw in tag_lower for kw in ['coffee', 'tea', 'espresso', 'latte', 'cappuccino']):
            return [tag, "Hot Beverage", "Beverage", "Food"]
        
        # Alcoholic Drinks
        elif any(kw in tag_lower for kw in ['beer', 'wine', 'cocktail', 'whiskey', 
                                             'vodka', 'alcohol']):
            return [tag, "Alcoholic Beverage", "Beverage", "Food"]
        
        # Soft Drinks
        elif any(kw in tag_lower for kw in ['juice', 'soda', 'water', 'drink']):
            return [tag, "Soft Drink", "Beverage", "Food"]
        
        # Italian Food
        elif any(kw in tag_lower for kw in ['pizza', 'pasta', 'spaghetti', 'lasagna']):
            return [tag, "Italian Cuisine", "Prepared Dish", "Food"]
        
        # Asian Food
        elif any(kw in tag_lower for kw in ['sushi', 'ramen', 'noodle', 'rice', 'stir fry']):
            return [tag, "Asian Cuisine", "Prepared Dish", "Food"]
        
        # Fast Food
        elif any(kw in tag_lower for kw in ['burger', 'hot dog', 'fries', 'sandwich']):
            return [tag, "Fast Food", "Prepared Dish", "Food"]
        
        # Other Prepared Dishes
        elif any(kw in tag_lower for kw in ['salad', 'soup', 'taco', 'burrito', 'meal', 'dish']):
            return [tag, "Prepared Dish", "Food"]
        
        return [tag, "Food"]
    
    # PEOPLE HIERARCHIES
    elif branch == "SUBJECT_PEOPLE":
        # Age-based
        if any(kw in tag_lower for kw in ['baby', 'infant']):
            return [tag, "Infant", "Child", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['toddler']):
            return [tag, "Toddler", "Child", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['child', 'kid', 'boy', 'girl']):
            return [tag, "Child", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['teen', 'teenager', 'adolescent']):
            return [tag, "Teenager", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['senior', 'elderly']):
            return [tag, "Senior", "Adult", "Human", "Living Thing"]
        
        # Medical Professionals
        elif any(kw in tag_lower for kw in ['doctor', 'physician', 'surgeon']):
            return [tag, "Doctor", "Medical Professional", "Professional", "Adult", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['nurse']):
            return [tag, "Nurse", "Medical Professional", "Professional", "Adult", "Human", "Living Thing"]
        
        # Education
        elif any(kw in tag_lower for kw in ['teacher', 'professor', 'instructor']):
            return [tag, "Educator", "Professional", "Adult", "Human", "Living Thing"]
        
        elif any(kw in tag_lower for kw in ['student']):
            return [tag, "Student", "Human", "Living Thing"]
        
        # Food Service
        elif any(kw in tag_lower for kw in ['chef', 'cook']):
            return [tag, "Chef", "Food Service Worker", "Professional", "Adult", "Human", "Living Thing"]
        
        # Artists
        elif any(kw in tag_lower for kw in ['artist', 'painter', 'sculptor']):
            return [tag, "Artist", "Professional", "Adult", "Human", "Living Thing"]
        
        # Performers
        elif any(kw in tag_lower for kw in ['actor', 'actress', 'musician', 'singer', 'dancer']):
            return [tag, "Performer", "Professional", "Adult", "Human", "Living Thing"]
        
        # Athletes
        elif any(kw in tag_lower for kw in ['athlete', 'player', 'runner', 'swimmer']):
            return [tag, "Athlete", "Professional", "Adult", "Human", "Living Thing"]
        
        # Other Adults
        elif any(kw in tag_lower for kw in ['adult', 'man', 'woman', 'male', 'female', 
                                             'person', 'people']):
            return [tag, "Adult", "Human", "Living Thing"]
        
        # Groups
        elif any(kw in tag_lower for kw in ['family', 'couple', 'crowd', 'group']):
            return [tag, "Human Group", "Human", "Living Thing"]
        
        return [tag, "Human", "Living Thing"]
    
    # OBJECT HIERARCHIES
    elif branch == "SUBJECT_OBJECT":
        # Vehicles - Cars
        if any(kw in tag_lower for kw in ['car', 'sedan', 'suv', 'coupe', 'hatchback']):
            return [tag, "Car", "Vehicle", "Man-Made Object"]
        
        # Vehicles - Trucks
        elif any(kw in tag_lower for kw in ['truck', 'pickup']):
            return [tag, "Truck", "Vehicle", "Man-Made Object"]
        
        # Vehicles - Motorcycles
        elif any(kw in tag_lower for kw in ['motorcycle', 'bike', 'scooter']):
            return [tag, "Motorcycle", "Vehicle", "Man-Made Object"]
        
        # Vehicles - Aircraft
        elif any(kw in tag_lower for kw in ['airplane', 'plane', 'jet', 'aircraft', 'helicopter']):
            return [tag, "Aircraft", "Vehicle", "Man-Made Object"]
        
        # Vehicles - Watercraft
        elif any(kw in tag_lower for kw in ['boat', 'ship', 'yacht', 'sailboat']):
            return [tag, "Watercraft", "Vehicle", "Man-Made Object"]
        
        # Electronics - Computers
        elif any(kw in tag_lower for kw in ['computer', 'laptop', 'desktop', 'monitor']):
            return [tag, "Computer", "Electronics", "Man-Made Object"]
        
        # Electronics - Phones
        elif any(kw in tag_lower for kw in ['phone', 'smartphone', 'mobile']):
            return [tag, "Phone", "Electronics", "Man-Made Object"]
        
        # Electronics - Cameras
        elif any(kw in tag_lower for kw in ['camera', 'dslr']):
            return [tag, "Camera", "Electronics", "Man-Made Object"]
        
        # Furniture - Seating
        elif any(kw in tag_lower for kw in ['chair', 'sofa', 'couch', 'bench', 'stool']):
            return [tag, "Seating", "Furniture", "Man-Made Object"]
        
        # Furniture - Tables
        elif any(kw in tag_lower for kw in ['table', 'desk']):
            return [tag, "Table", "Furniture", "Man-Made Object"]
        
        # Furniture - Storage
        elif any(kw in tag_lower for kw in ['bed', 'cabinet', 'shelf', 'dresser']):
            return [tag, "Storage Furniture", "Furniture", "Man-Made Object"]
        
        # Tools
        elif any(kw in tag_lower for kw in ['hammer', 'screwdriver', 'wrench', 'saw', 'tool']):
            return [tag, "Tool", "Man-Made Object"]
        
        # Buildings - Residential
        elif any(kw in tag_lower for kw in ['house', 'home', 'apartment', 'cottage']):
            return [tag, "Residential Building", "Building", "Structure", "Man-Made Object"]
        
        # Buildings - Commercial
        elif any(kw in tag_lower for kw in ['office', 'store', 'shop', 'mall', 'restaurant']):
            return [tag, "Commercial Building", "Building", "Structure", "Man-Made Object"]
        
        # Buildings - Religious
        elif any(kw in tag_lower for kw in ['church', 'temple', 'mosque', 'synagogue']):
            return [tag, "Religious Building", "Building", "Structure", "Man-Made Object"]
        
        # Other Buildings
        elif any(kw in tag_lower for kw in ['building', 'tower', 'skyscraper']):
            return [tag, "Building", "Structure", "Man-Made Object"]
        
        # Infrastructure
        elif any(kw in tag_lower for kw in ['bridge', 'road', 'highway', 'tunnel']):
            return [tag, "Infrastructure", "Structure", "Man-Made Object"]
        
        # Containers
        elif any(kw in tag_lower for kw in ['bottle', 'jar', 'box', 'bag', 'container']):
            return [tag, "Container", "Man-Made Object"]
        
        # Tableware
        elif any(kw in tag_lower for kw in ['plate', 'bowl', 'cup', 'glass', 'fork', 
                                             'knife', 'spoon']):
            return [tag, "Tableware", "Man-Made Object"]
        
        # Books & Paper
        elif any(kw in tag_lower for kw in ['book', 'magazine', 'newspaper', 'paper']):
            return [tag, "Publication", "Man-Made Object"]
        
        # Sports Equipment
        elif any(kw in tag_lower for kw in ['ball', 'bat', 'racket', 'club']):
            return [tag, "Sports Equipment", "Man-Made Object"]
        
        return [tag, "Man-Made Object"]
    
    # LOCATION HIERARCHIES
    elif branch == "SCENE_LOCATION":
        # Natural Landscapes
        if any(kw in tag_lower for kw in ['mountain', 'hill', 'valley', 'canyon']):
            return [tag, "Mountain/Hill", "Natural Landscape", "Location"]
        
        elif any(kw in tag_lower for kw in ['forest', 'jungle', 'woods', 'rainforest']):
            return [tag, "Forest", "Natural Landscape", "Location"]
        
        elif any(kw in tag_lower for kw in ['beach', 'coast', 'shore', 'seaside']):
            return [tag, "Coastal", "Natural Landscape", "Location"]
        
        elif any(kw in tag_lower for kw in ['ocean', 'sea', 'lake', 'river', 'stream']):
            return [tag, "Water Body", "Natural Landscape", "Location"]
        
        elif any(kw in tag_lower for kw in ['desert', 'dune']):
            return [tag, "Desert", "Natural Landscape", "Location"]
        
        elif any(kw in tag_lower for kw in ['field', 'meadow', 'prairie', 'grassland']):
            return [tag, "Field/Meadow", "Natural Landscape", "Location"]
        
        # Urban Spaces
        elif any(kw in tag_lower for kw in ['city', 'downtown', 'urban']):
            return [tag, "City", "Urban Space", "Location"]
        
        elif any(kw in tag_lower for kw in ['street', 'road', 'avenue', 'boulevard']):
            return [tag, "Street", "Urban Space", "Location"]
        
        elif any(kw in tag_lower for kw in ['park', 'playground', 'plaza', 'square']):
            return [tag, "Public Park", "Urban Space", "Location"]
        
        # Indoor Spaces - Residential
        elif any(kw in tag_lower for kw in ['bedroom', 'living room', 'bathroom', 
                                             'kitchen', 'room']):
            return [tag, "Residential Room", "Indoor Space", "Location"]
        
        # Indoor Spaces - Commercial
        elif any(kw in tag_lower for kw in ['office', 'store', 'shop', 'restaurant', 
                                             'cafe', 'bar']):
            return [tag, "Commercial Space", "Indoor Space", "Location"]
        
        # Indoor Spaces - Public
        elif any(kw in tag_lower for kw in ['museum', 'gallery', 'library', 'theater', 
                                             'stadium', 'arena']):
            return [tag, "Public Venue", "Indoor Space", "Location"]
        
        # Transportation Venues
        elif any(kw in tag_lower for kw in ['airport', 'station', 'terminal', 'port']):
            return [tag, "Transportation Hub", "Location"]
        
        return [tag, "Location"]
    
    # ACTIVITY HIERARCHIES
    elif branch == "ACTIVITY_ACTION":
        # Sports
        if any(kw in tag_lower for kw in ['running', 'jogging', 'sprinting']):
            return [tag, "Running", "Athletics", "Sport", "Activity"]
        
        elif any(kw in tag_lower for kw in ['swimming', 'diving']):
            return [tag, "Aquatic Sport", "Sport", "Activity"]
        
        elif any(kw in tag_lower for kw in ['cycling', 'biking']):
            return [tag, "Cycling", "Sport", "Activity"]
        
        elif any(kw in tag_lower for kw in ['skiing', 'snowboarding']):
            return [tag, "Winter Sport", "Sport", "Activity"]
        
        elif any(kw in tag_lower for kw in ['football', 'soccer', 'basketball', 
                                             'baseball', 'tennis', 'golf']):
            return [tag, "Ball Sport", "Sport", "Activity"]
        
        # Arts & Crafts
        elif any(kw in tag_lower for kw in ['painting', 'drawing', 'sketching']):
            return [tag, "Visual Art", "Creative Activity", "Activity"]
        
        elif any(kw in tag_lower for kw in ['playing', 'music', 'singing']):
            return [tag, "Musical Performance", "Creative Activity", "Activity"]
        
        elif any(kw in tag_lower for kw in ['dancing', 'ballet']):
            return [tag, "Dance", "Creative Activity", "Activity"]
        
        # Work & Labor
        elif any(kw in tag_lower for kw in ['working', 'building', 'construction']):
            return [tag, "Labor", "Work", "Activity"]
        
        elif any(kw in tag_lower for kw in ['typing', 'writing', 'reading']):
            return [tag, "Office Work", "Work", "Activity"]
        
        # Social Activities
        elif any(kw in tag_lower for kw in ['meeting', 'talking', 'conversation']):
            return [tag, "Social Interaction", "Activity"]
        
        elif any(kw in tag_lower for kw in ['party', 'celebration', 'festival']):
            return [tag, "Celebration", "Social Event", "Activity"]
        
        elif any(kw in tag_lower for kw in ['wedding', 'ceremony']):
            return [tag, "Ceremony", "Social Event", "Activity"]
        
        # Daily Activities
        elif any(kw in tag_lower for kw in ['eating', 'drinking', 'dining']):
            return [tag, "Eating/Drinking", "Daily Activity", "Activity"]
        
        elif any(kw in tag_lower for kw in ['sleeping', 'resting', 'relaxing']):
            return [tag, "Resting", "Daily Activity", "Activity"]
        
        elif any(kw in tag_lower for kw in ['walking', 'hiking', 'strolling']):
            return [tag, "Walking", "Daily Activity", "Activity"]
        
        # Travel
        elif any(kw in tag_lower for kw in ['traveling', 'touring', 'sightseeing']):
            return [tag, "Travel", "Activity"]
        
        return [tag, "Activity"]
    
    # Default: flat hierarchy
    return [tag]


def build_hierarchical_ontology(tags: List[Dict]) -> Dict:
    """Build deep hierarchical ontology with multi-level taxonomies."""
    print(f"\nLoaded {len(tags)} tags from tags.json")
    
    # Auto-discover keywords
    print("\nAuto-discovering keyword dictionaries from RAM++ vocabulary...")
    keywords = auto_discover_keywords(tags)
    for branch, words in keywords.items():
        print(f"  {branch}: {len(words)} keywords discovered")
    
    # Classify tags and build hierarchies
    print("\nBuilding deep hierarchical ontology...")
    classified_tags = []
    branch_stats = defaultdict(int)
    
    for tag_entry in tags:
        tag = tag_entry["tag"]
        
        # Skip Chinese tags (they contain non-ASCII characters)
        if any(ord(c) > 127 for c in tag):
            continue
        
        branch = classify_tag(tag, keywords)
        hierarchy = build_deep_hierarchy(tag, branch)
        
        classified_tags.append({
            "id": tag_entry["id"],
            "tag": tag,
            "threshold": tag_entry["threshold"],
            "branch": branch,
            "hierarchy": hierarchy,
            "depth": len(hierarchy)
        })
        
        branch_stats[branch] += 1
    
    # Print statistics
    print(f"\nClassified {len(classified_tags)} tags (Chinese tags excluded)")
    print("\nBranch distribution:")
    for branch, count in sorted(branch_stats.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(classified_tags)) * 100
        print(f"  {branch}: {count} tags ({pct:.1f}%)")
    
    # Organize into hierarchical structure
    hierarchy_root = {}
    
    # Group by branch
    for tag_entry in classified_tags:
        branch = tag_entry["branch"]
        if branch not in hierarchy_root:
            hierarchy_root[branch] = {
                "branch": branch,
                "total_tags": 0,
                "tags": []
            }
        
        hierarchy_root[branch]["tags"].append({
            "id": tag_entry["id"],
            "tag": tag_entry["tag"],
            "threshold": tag_entry["threshold"],
            "hierarchy": tag_entry["hierarchy"],
            "depth": tag_entry["depth"]
        })
        hierarchy_root[branch]["total_tags"] += 1
    
    # Create output structure
    output = {
        "model": "ram_plus_plus",
        "source": "https://huggingface.co/xinyu1205/recognize-anything-plus-model",
        "total_tags": len(classified_tags),
        "description": "Deep hierarchical ontology with multi-level taxonomies",
        "branches": []
    }
    
    for branch_name in sorted(hierarchy_root.keys()):
        branch_data = hierarchy_root[branch_name]
        output["branches"].append(branch_data)
    
    return output


def main():
    tags = load_tags()
    ontology = build_hierarchical_ontology(tags)
    
    output_file = "ontology_deep_hierarchy.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ontology, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("DEEP HIERARCHICAL ONTOLOGY SUMMARY")
    print('='*60)
    print(f"\nTotal tags: {ontology['total_tags']}")
    print(f"\nBranches: {len(ontology['branches'])}")
    for branch in ontology['branches']:
        print(f"  {branch['branch']}: {branch['total_tags']} tags")
    
    # Show depth statistics
    depth_counts = defaultdict(int)
    for branch in ontology['branches']:
        for tag in branch['tags']:
            depth_counts[tag['depth']] += 1
    
    print(f"\nHierarchy depths:")
    for depth in sorted(depth_counts.keys()):
        count = depth_counts[depth]
        pct = (count / ontology['total_tags']) * 100
        print(f"  Depth {depth}: {count} tags ({pct:.1f}%)")
    
    # Show example hierarchies
    print(f"\n{'='*60}")
    print("EXAMPLE HIERARCHIES")
    print('='*60)
    
    examples = [
        ("SUBJECT_ANIMAL", "dog"),
        ("SUBJECT_ANIMAL", "eagle"),
        ("SUBJECT_FOOD", "apple"),
        ("SUBJECT_FOOD", "pizza"),
        ("SUBJECT_PEOPLE", "doctor"),
        ("SUBJECT_OBJECT", "car"),
        ("ACTIVITY_ACTION", "running"),
    ]
    
    for branch_name, example_tag in examples:
        branch = next((b for b in ontology['branches'] if b['branch'] == branch_name), None)
        if branch:
            tag_entry = next((t for t in branch['tags'] if example_tag in t['tag'].lower()), None)
            if tag_entry:
                hierarchy_str = " → ".join(tag_entry['hierarchy'])
                print(f"\n{tag_entry['tag']}:")
                print(f"  {hierarchy_str}")
    
    print(f"\nDeep hierarchical ontology saved to {output_file}")


if __name__ == "__main__":
    main()
