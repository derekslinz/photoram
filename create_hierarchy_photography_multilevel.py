#!/usr/bin/env python3
"""
Create a true multi-level hierarchical categorization of RAM++ tags organized by photography genres.
"""

import json
from typing import Dict, List


def load_tags(filepath: str = "tags.json") -> List[Dict]:
    """Load tags from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tags']


def categorize_tags(tags: List[Dict]) -> Dict:
    """Categorize tags into a true multi-level hierarchical structure."""
    
    # Define hierarchy with parent-child relationships
    # Structure: category name -> (keywords, parent_category, subcategories)
    hierarchy_def = {
        # Top-level photography genres
        "Portrait Photography": {
            "keywords": ["portrait", "face", "selfie", "headshot", "model pose"],
            "parent": None,
            "subcategories": ["People & Expression", "Body Parts & Details"]
        },
        "People & Expression": {
            "keywords": ["people", "person", "man", "woman", "child", "boy", "girl", "baby",
                        "couple", "family", "crowd", "group", "male", "female", "expression",
                        "smile", "laugh", "cry", "emotion", "actor", "actress", "celebrity",
                        "bride", "groom"],
            "parent": "Portrait Photography",
            "subcategories": []
        },
        "Body Parts & Details": {
            "keywords": ["face", "head", "eye", "nose", "mouth", "ear", "hair", "hand", "finger",
                        "arm", "leg", "foot", "toe", "body", "skin", "neck", "shoulder", "chest",
                        "back", "belly", "waist", "hip", "knee", "ankle", "wrist", "elbow",
                        "cheek", "chin", "forehead"],
            "parent": "Portrait Photography",
            "subcategories": []
        },
        
        "Landscape Photography": {
            "keywords": ["landscape", "vista", "scenery", "horizon", "panorama", "overlook",
                        "countryside", "rural"],
            "parent": None,
            "subcategories": ["Mountains & Hills", "Deserts & Valleys", "Plains & Fields"]
        },
        "Mountains & Hills": {
            "keywords": ["mountain", "hill", "peak", "ridge", "cliff", "canyon", "plateau",
                        "alp", "slope"],
            "parent": "Landscape Photography",
            "subcategories": []
        },
        "Deserts & Valleys": {
            "keywords": ["desert", "dune", "valley", "mesa", "butte", "badlands", "oasis"],
            "parent": "Landscape Photography",
            "subcategories": []
        },
        "Plains & Fields": {
            "keywords": ["plain", "prairie", "farmland", "grassland", "savanna"],
            "parent": "Landscape Photography",
            "subcategories": []
        },
        
        "Wildlife Photography": {
            "keywords": ["wildlife", "wild animal", "safari", "predator", "prey"],
            "parent": None,
            "subcategories": ["Large Mammals", "Birds in Wild", "Reptiles & Amphibians"]
        },
        "Large Mammals": {
            "keywords": ["lion", "tiger", "elephant", "giraffe", "zebra", "rhino", "hippo",
                        "bear", "wolf", "deer", "moose", "elk", "buffalo", "bison", "antelope",
                        "gazelle", "leopard", "cheetah", "hyena", "fox", "coyote", "kangaroo",
                        "gorilla", "baboon", "camel"],
            "parent": "Wildlife Photography",
            "subcategories": []
        },
        "Birds in Wild": {
            "keywords": ["eagle", "hawk", "falcon", "owl", "vulture", "pelican", "stork",
                        "heron", "egret", "crane", "peacock", "pheasant", "quail", "wild bird"],
            "parent": "Wildlife Photography",
            "subcategories": []
        },
        "Reptiles & Amphibians": {
            "keywords": ["snake", "lizard", "crocodile", "alligator", "turtle wild",
                        "tortoise", "frog wild", "toad wild", "iguana", "gecko"],
            "parent": "Wildlife Photography",
            "subcategories": []
        },
        
        "Nature Photography": {
            "keywords": ["nature", "forest", "woodland", "jungle", "wilderness"],
            "parent": None,
            "subcategories": ["Trees & Large Plants", "Gardens & Landscapes"]
        },
        "Trees & Large Plants": {
            "keywords": ["tree", "trunk", "branch large", "forest", "woods", "pine", "oak",
                        "maple", "birch", "willow", "palm", "fir", "bamboo grove"],
            "parent": "Nature Photography",
            "subcategories": []
        },
        "Gardens & Landscapes": {
            "keywords": ["garden", "park", "botanical", "arboretum", "grove", "orchard",
                        "vineyard", "hedge large"],
            "parent": "Nature Photography",
            "subcategories": []
        },
        
        "Macro & Close-up Photography": {
            "keywords": ["macro", "close-up", "closeup", "detail shot", "extreme close"],
            "parent": None,
            "subcategories": ["Food Photography", "Flowers & Small Plants", 
                            "Insects & Small Creatures", "Textures & Materials"]
        },
        "Food Photography": {
            "keywords": ["food", "meal", "dish", "cuisine", "plate", "bowl", "culinary"],
            "parent": "Macro & Close-up Photography",
            "subcategories": ["Main Dishes & Meals", "Beverages & Drinks", 
                            "Fruits & Vegetables", "Desserts & Sweets"]
        },
        "Main Dishes & Meals": {
            "keywords": ["meal", "dish", "plate", "entree", "main course", "recipe",
                        "pizza", "pasta", "soup", "salad", "sandwich", "burger", "sushi",
                        "steak", "chicken", "pork", "lamb", "beef", "meat", "seafood",
                        "bento", "bibimbap", "curry", "taco", "burrito", "rice bowl",
                        "noodle", "dumpling", "kebab", "barbecue", "grilled",
                        "bacon", "egg", "omelet", "pancake", "waffle", "toast",
                        "bagel", "croissant", "muffin", "biscuit", "bread",
                        "cheese", "ham", "sausage", "fish", "salmon", "tuna",
                        "shrimp", "crab", "lobster", "oyster", "mussel", "clam",
                        "lasagna", "spaghetti", "ravioli", "risotto", "paella",
                        "enchilada", "fajita", "quesadilla", "nacho",
                        "ramen", "pho", "udon", "dim sum", "spring roll",
                        "hot dog", "corn dog", "pretzel"],
            "parent": "Food Photography",
            "subcategories": []
        },
        "Beverages & Drinks": {
            "keywords": ["drink", "beverage", "coffee", "tea", "juice", "smoothie", "cocktail",
                        "wine", "beer", "whiskey", "vodka", "rum", "champagne", "soda",
                        "water bottle", "cup", "mug", "glass drink", "bottle", "latte",
                        "cappuccino", "espresso", "milkshake", "shake"],
            "parent": "Food Photography",
            "subcategories": []
        },
        "Fruits & Vegetables": {
            "keywords": ["fruit", "vegetable", "produce", "apple", "banana", "orange", "grape",
                        "strawberry", "blueberry", "raspberry", "cherry", "peach", "pear",
                        "plum", "apricot", "mango", "pineapple", "watermelon", "melon",
                        "kiwi", "lemon", "lime", "grapefruit", "avocado", "tomato",
                        "carrot", "potato", "onion", "garlic", "pepper", "cucumber",
                        "lettuce", "cabbage", "broccoli", "cauliflower", "spinach",
                        "celery", "asparagus", "bean", "peas", "corn", "pumpkin",
                        "squash", "zucchini", "eggplant", "mushroom", "radish",
                        "beet", "turnip", "parsnip", "leek", "shallot", "scallion",
                        "bok choy", "kale", "arugula", "endive", "radicchio",
                        "artichoke", "fennel", "rhubarb", "okra",
                        "tangerine", "clementine", "mandarin", "pomegranate",
                        "fig", "date", "persimmon", "guava", "papaya",
                        "passion fruit", "dragon fruit", "lychee", "coconut",
                        "almond", "walnut", "cashew", "peanut", "pistachio",
                        "hazelnut", "pecan", "chestnut"],
            "parent": "Food Photography",
            "subcategories": []
        },
        "Desserts & Sweets": {
            "keywords": ["dessert", "cake", "pastry", "cookie", "chocolate", "ice cream",
                        "candy", "sweet", "pie", "tart", "cupcake", "muffin", "donut",
                        "brownie", "pudding", "mousse", "tiramisu", "cheesecake",
                        "macaron", "croissant", "waffle", "pancake", "crepe",
                        "biscuit", "scone", "danish", "eclair", "profiterole",
                        "truffle", "fudge", "caramel", "toffee", "brittle",
                        "marshmallow", "gelatin", "jello", "sorbet", "frozen yogurt",
                        "sundae", "parfait", "cream puff", "cannoli",
                        "baklava", "strudel", "cobbler", "crisp dessert"],
            "parent": "Food Photography",
            "subcategories": []
        },
        "Flowers & Small Plants": {
            "keywords": ["flower", "blossom", "bloom", "petal", "rose", "lily", "tulip",
                        "daisy", "sunflower", "orchid", "lotus", "hibiscus", "carnation",
                        "chrysanthemum", "daffodil", "iris", "lavender", "lilac",
                        "magnolia", "marigold", "pansy", "peony", "petunia", "poppy",
                        "violet", "azalea", "begonia", "cactus flower", "clover",
                        "dandelion", "fern small", "moss", "lichen", "succulent",
                        "herb small", "leaf detail", "stem close", "bud",
                        "geranium", "hyacinth", "hydrangea", "jasmine",
                        "zinnia", "cosmos", "dahlia", "gladiolus", "freesia",
                        "amaryllis", "anemone", "aster", "camellia",
                        "calendula", "calla lily", "columbine", "crocus",
                        "cyclamen", "delphinium", "forget-me-not", "foxglove",
                        "gardenia", "heather", "hollyhock", "honeysuckle",
                        "impatiens", "larkspur", "lupine", "morning glory",
                        "nasturtium", "primrose", "ranunculus", "snapdragon",
                        "stock", "sweet pea", "verbena", "wisteria"],
            "parent": "Macro & Close-up Photography",
            "subcategories": []
        },
        "Insects & Small Creatures": {
            "keywords": ["insect", "bug", "butterfly", "moth", "bee", "beetle", "dragonfly",
                        "ladybug", "spider", "ant", "fly", "wasp", "hornet", "caterpillar",
                        "cricket", "grasshopper", "mantis", "flea", "mosquito", "tick",
                        "snail", "slug", "worm", "centipede", "millipede", "scorpion"],
            "parent": "Macro & Close-up Photography",
            "subcategories": []
        },
        "Textures & Materials": {
            "keywords": ["texture", "surface detail", "material close", "fabric detail",
                        "wood grain", "metal surface", "stone texture", "wall texture",
                        "pattern detail", "weave", "grain", "rough surface"],
            "parent": "Macro & Close-up Photography",
            "subcategories": []
        },
        
        "Architectural Photography": {
            "keywords": ["architecture", "building", "structure", "construction"],
            "parent": None,
            "subcategories": ["Modern Buildings", "Historical Buildings", "Bridges & Infrastructure"]
        },
        "Modern Buildings": {
            "keywords": ["skyscraper", "tower modern", "office building", "apartment building",
                        "condo", "mall", "hotel modern", "glass building", "contemporary"],
            "parent": "Architectural Photography",
            "subcategories": []
        },
        "Historical Buildings": {
            "keywords": ["church", "cathedral", "temple", "mosque", "synagogue", "palace",
                        "castle", "fortress", "monument", "memorial", "ancient building",
                        "historical", "heritage"],
            "parent": "Architectural Photography",
            "subcategories": []
        },
        "Bridges & Infrastructure": {
            "keywords": ["bridge", "viaduct", "aqueduct", "dam", "tunnel", "overpass",
                        "arch structure", "column", "pillar", "infrastructure"],
            "parent": "Architectural Photography",
            "subcategories": []
        },
        
        "Urban & Street Photography": {
            "keywords": ["street", "urban", "city", "downtown", "metropolitan"],
            "parent": None,
            "subcategories": ["Street Scenes", "Urban Details"]
        },
        "Street Scenes": {
            "keywords": ["street scene", "sidewalk", "crosswalk", "intersection", "traffic",
                        "pedestrian", "alley", "avenue", "square", "plaza", "market street"],
            "parent": "Urban & Street Photography",
            "subcategories": []
        },
        "Urban Details": {
            "keywords": ["graffiti", "mural", "street art", "storefront", "shop front",
                        "sign urban", "billboard", "neon", "street light", "urban texture"],
            "parent": "Urban & Street Photography",
            "subcategories": []
        },
        
        "Sports Photography": {
            "keywords": ["sport", "athletic", "athlete", "competition", "game"],
            "parent": None,
            "subcategories": ["Team Sports", "Individual Sports", "Extreme Sports"]
        },
        "Team Sports": {
            "keywords": ["soccer", "football", "basketball", "baseball", "volleyball",
                        "hockey", "cricket", "rugby", "team sport"],
            "parent": "Sports Photography",
            "subcategories": []
        },
        "Individual Sports": {
            "keywords": ["tennis", "golf", "boxing", "wrestling", "gymnastics", "swimming race",
                        "track", "marathon", "sprint", "badminton", "fencing"],
            "parent": "Sports Photography",
            "subcategories": []
        },
        "Extreme Sports": {
            "keywords": ["ski", "snowboard", "surf", "skate", "skateboard", "bmx",
                        "motocross", "parkour", "rock climb", "bungee", "paraglide"],
            "parent": "Sports Photography",
            "subcategories": []
        },
        
        "Transportation Photography": {
            "keywords": ["transport", "vehicle", "travel mode"],
            "parent": None,
            "subcategories": ["Automotive", "Aviation", "Marine & Nautical", "Rail & Public Transit"]
        },
        "Automotive": {
            "keywords": ["car", "automobile", "truck", "van", "suv", "sedan", "coupe",
                        "convertible", "sports car", "race car", "vintage car", "motorcycle",
                        "scooter", "engine", "wheel", "tire"],
            "parent": "Transportation Photography",
            "subcategories": []
        },
        "Aviation": {
            "keywords": ["airplane", "aircraft", "plane", "jet", "helicopter", "chopper",
                        "flight", "airport", "runway", "hangar", "cockpit", "pilot",
                        "airline", "airliner", "propeller", "wing", "aviation"],
            "parent": "Transportation Photography",
            "subcategories": []
        },
        "Marine & Nautical": {
            "keywords": ["boat", "ship", "vessel", "yacht", "sailboat", "cruise ship",
                        "ferry", "submarine", "port", "harbor", "dock", "pier", "marina",
                        "nautical", "maritime", "naval", "sailor", "captain"],
            "parent": "Transportation Photography",
            "subcategories": []
        },
        "Rail & Public Transit": {
            "keywords": ["train", "railway", "railroad", "locomotive", "subway", "metro",
                        "tram", "trolley", "bus", "transit"],
            "parent": "Transportation Photography",
            "subcategories": []
        },
        
        "Animal Photography": {
            "keywords": ["animal domestic", "pet", "farm animal", "domesticated"],
            "parent": None,
            "subcategories": ["Pets", "Livestock & Farm Animals", "Small Domestic Animals"]
        },
        "Pets": {
            "keywords": ["pet", "dog", "puppy", "cat", "kitten", "domestic animal",
                        "golden retriever", "labrador", "poodle", "bulldog", "terrier",
                        "shepherd", "collie", "husky", "chihuahua", "persian cat",
                        "siamese", "tabby", "bichon", "cocker"],
            "parent": "Animal Photography",
            "subcategories": []
        },
        "Livestock & Farm Animals": {
            "keywords": ["livestock", "farm animal", "cow", "bull", "cattle", "horse",
                        "pony", "donkey", "mule", "pig", "sheep", "goat", "chicken",
                        "rooster", "hen", "turkey", "duck farm", "goose farm"],
            "parent": "Animal Photography",
            "subcategories": []
        },
        "Small Domestic Animals": {
            "keywords": ["rabbit pet", "hamster", "guinea pig", "gerbil", "ferret pet",
                        "rat pet", "mouse pet", "bird cage", "parrot pet", "canary"],
            "parent": "Animal Photography",
            "subcategories": []
        },
        
        "Water Photography": {
            "keywords": ["water", "aquatic", "marine"],
            "parent": None,
            "subcategories": ["Seascape & Ocean", "Rivers & Lakes", "Underwater"]
        },
        "Seascape & Ocean": {
            "keywords": ["ocean", "sea", "beach", "shore", "coast", "coastline", "seaside",
                        "wave", "surf", "tide", "seashell", "sand beach"],
            "parent": "Water Photography",
            "subcategories": []
        },
        "Rivers & Lakes": {
            "keywords": ["river", "stream", "creek", "brook", "lake", "pond", "waterfall",
                        "cascade", "rapids", "dam", "reservoir"],
            "parent": "Water Photography",
            "subcategories": []
        },
        "Underwater": {
            "keywords": ["underwater", "scuba", "dive", "diving", "snorkel", "coral reef",
                        "reef", "marine life", "fish underwater", "shark", "whale",
                        "dolphin", "octopus", "jellyfish", "sea turtle"],
            "parent": "Water Photography",
            "subcategories": []
        },
        
        "Astrophotography": {
            "keywords": ["star", "planet", "moon", "sun", "galaxy", "nebula", "constellation",
                        "astronomy", "space", "cosmos", "celestial", "milky way", "meteor",
                        "comet", "eclipse", "night sky"],
            "parent": None,
            "subcategories": []
        },
        
        "Weather Photography": {
            "keywords": ["weather", "rain", "storm", "lightning", "snow", "fog", "mist",
                        "cloud", "wind", "tornado", "hurricane", "rainbow", "aurora"],
            "parent": None,
            "subcategories": []
        },
        
        "Interior Photography": {
            "keywords": ["interior", "indoor", "room"],
            "parent": None,
            "subcategories": ["Residential Interiors", "Commercial Interiors"]
        },
        "Residential Interiors": {
            "keywords": ["home", "house interior", "apartment", "bedroom", "bathroom",
                        "living room", "kitchen", "dining room", "furniture", "chair",
                        "table", "sofa", "couch", "bed", "decor"],
            "parent": "Interior Photography",
            "subcategories": []
        },
        "Commercial Interiors": {
            "keywords": ["office", "lobby", "hotel lobby", "restaurant interior", "shop interior",
                        "mall", "hallway", "corridor", "reception", "boardroom"],
            "parent": "Interior Photography",
            "subcategories": []
        },
        
        "Fashion & Apparel Photography": {
            "keywords": ["fashion", "style", "clothing", "apparel", "wear"],
            "parent": None,
            "subcategories": ["Fashion Editorial", "Clothing & Garments", "Accessories"]
        },
        "Fashion Editorial": {
            "keywords": ["fashion shoot", "runway", "catwalk", "fashion show", "designer",
                        "haute couture", "model fashion"],
            "parent": "Fashion & Apparel Photography",
            "subcategories": []
        },
        "Clothing & Garments": {
            "keywords": ["dress", "suit", "shirt", "pants", "skirt", "jacket", "coat",
                        "sweater", "hoodie", "shoe", "boot", "sneaker", "uniform"],
            "parent": "Fashion & Apparel Photography",
            "subcategories": []
        },
        "Accessories": {
            "keywords": ["jewelry", "necklace", "bracelet", "ring", "earring", "watch",
                        "hat", "cap", "scarf", "tie", "belt", "bag", "purse", "sunglasses"],
            "parent": "Fashion & Apparel Photography",
            "subcategories": []
        },
        
        "Event Photography": {
            "keywords": ["event", "celebration", "ceremony"],
            "parent": None,
            "subcategories": ["Weddings", "Festivals & Holidays", "Performances"]
        },
        "Weddings": {
            "keywords": ["wedding", "marriage", "bride", "groom", "ceremony wedding",
                        "reception", "bridal"],
            "parent": "Event Photography",
            "subcategories": []
        },
        "Festivals & Holidays": {
            "keywords": ["festival", "carnival", "parade", "christmas", "halloween",
                        "easter", "birthday", "anniversary", "holiday", "thanksgiving",
                        "celebration", "party", "gift", "present", "ornament holiday",
                        "santa", "elf", "pumpkin decoration", "candy cane"],
            "parent": "Event Photography",
            "subcategories": []
        },
        "Performances": {
            "keywords": ["concert", "show", "performance", "theater", "stage", "ballet",
                        "dance", "music performance", "band performance", "singer",
                        "musician", "orchestra", "choir"],
            "parent": "Event Photography",
            "subcategories": []
        },
        
        "Still Life & Product Photography": {
            "keywords": ["still life", "product", "commercial photo", "arrangement"],
            "parent": None,
            "subcategories": ["Product Photography", "Still Life Arrangements", 
                            "Technology Products", "Household Products", 
                            "Materials & Surfaces", "Gemstones & Minerals", "Common Objects"]
        },
        "Product Photography": {
            "keywords": ["product shot", "merchandise", "goods", "packaging", "package",
                        "box product", "container", "brand", "logo", "label product",
                        "bottle product", "can product", "jar product"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Still Life Arrangements": {
            "keywords": ["still life", "arrangement", "composition", "tabletop",
                        "vase", "bouquet", "centerpiece", "display"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Technology Products": {
            "keywords": ["phone", "smartphone", "laptop", "computer", "tablet", "ipad",
                        "camera product", "headphone", "speaker", "keyboard", "mouse",
                        "monitor", "screen", "television", "tv", "radio", "CD", "DVD",
                        "USB", "remote control", "gaming console", "Wii", "controller"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Household Products": {
            "keywords": ["appliance", "refrigerator", "fridge", "stove", "oven",
                        "microwave", "washing machine", "dishwasher", "vacuum", "iron",
                        "toaster", "blender", "kettle", "pot", "pan", "knife", "fork",
                        "spoon", "cup", "mug", "plate", "bowl", "basket", "bucket",
                        "broom", "mop", "lamp", "clock", "alarm clock", "candle",
                        "mirror", "curtain", "pillow", "blanket", "towel", "cutlery"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Materials & Surfaces": {
            "keywords": ["material", "surface", "texture", "wood", "wooden", "timber",
                        "metal", "metallic", "steel", "iron", "copper", "brass", "bronze",
                        "aluminum", "tin", "zinc", "lead", "nickel",
                        "stone", "rock", "marble", "granite", "slate", "limestone",
                        "sandstone", "basalt", "quartz", "obsidian",
                        "brick", "concrete", "cement", "mortar", "plaster", "stucco",
                        "plastic", "polymer", "resin", "acrylic", "vinyl",
                        "rubber", "latex", "silicone", "foam",
                        "glass", "crystal", "mirror surface",
                        "fabric", "cloth", "textile", "canvas", "linen", "cotton",
                        "wool", "silk", "velvet", "satin", "denim", "polyester",
                        "leather", "suede", "hide", "fur",
                        "paper", "cardboard", "parchment",
                        "ceramic", "porcelain", "clay", "terra cotta",
                        "wax", "paraffin", "beeswax",
                        "cork", "bamboo material", "rattan", "wicker"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Gemstones & Minerals": {
            "keywords": ["gem", "gemstone", "jewel", "precious stone",
                        "diamond", "ruby", "emerald", "sapphire", "pearl",
                        "amethyst", "topaz", "opal", "jade", "turquoise",
                        "amber", "garnet", "aquamarine", "onyx", "agate",
                        "jasper", "malachite", "lapis lazuli", "moonstone",
                        "mineral", "ore", "coal", "salt rock", "sulfur"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        "Common Objects": {
            "keywords": ["object", "item", "thing", "box", "container", "bag",
                        "bottle", "jar", "can", "tube", "package", "wrapper",
                        "key", "lock", "chain", "rope", "string", "cord", "cable",
                        "hook", "hanger", "clip", "pin", "button",
                        "lens", "glasses", "3D glasses", "sunglasses",
                        "umbrella", "cane", "crutch", "walker", "wheelchair",
                        "crayon", "marker", "brush", "sponge",
                        "atlas", "map", "globe", "chart",
                        "frame", "picture frame", "album", "scrapbook",
                        "trophy", "medal", "badge", "ribbon", "certificate"],
            "parent": "Still Life & Product Photography",
            "subcategories": []
        },
        
        "Business & Professional Photography": {
            "keywords": ["business", "professional", "corporate", "office", "workplace"],
            "parent": None,
            "subcategories": ["Office & Workplace", "Business People", "Financial"]
        },
        "Office & Workplace": {
            "keywords": ["office", "workplace", "desk", "cubicle", "meeting room",
                        "boardroom", "conference", "reception", "lobby business",
                        "workspace", "computer work", "document", "paper", "file",
                        "folder", "notebook", "pen", "pencil", "calculator", "stapler",
                        "briefcase", "whiteboard", "presentation"],
            "parent": "Business & Professional Photography",
            "subcategories": []
        },
        "Business People": {
            "keywords": ["businessman", "businesswoman", "executive", "manager",
                        "employee", "worker", "colleague", "professional person",
                        "secretary", "accountant", "lawyer"],
            "parent": "Business & Professional Photography",
            "subcategories": []
        },
        "Financial": {
            "keywords": ["money", "cash", "currency", "coin", "banknote", "dollar",
                        "bank", "ATM", "credit card", "wallet", "finance", "payment"],
            "parent": "Business & Professional Photography",
            "subcategories": []
        },
        
        "Medical & Healthcare Photography": {
            "keywords": ["medical", "health", "healthcare", "hospital", "clinic"],
            "parent": None,
            "subcategories": ["Medical Facilities", "Medical Professionals", "Medical Equipment"]
        },
        "Medical Facilities": {
            "keywords": ["hospital", "clinic", "emergency room", "operating room",
                        "ward", "ambulance", "pharmacy", "laboratory medical"],
            "parent": "Medical & Healthcare Photography",
            "subcategories": []
        },
        "Medical Professionals": {
            "keywords": ["doctor", "physician", "nurse", "surgeon", "dentist",
                        "paramedic", "therapist"],
            "parent": "Medical & Healthcare Photography",
            "subcategories": []
        },
        "Medical Equipment": {
            "keywords": ["stethoscope", "syringe", "x-ray", "scan", "MRI", "CT",
                        "medicine", "medication", "pill", "tablet", "capsule",
                        "bandage", "gauze", "medical instrument"],
            "parent": "Medical & Healthcare Photography",
            "subcategories": []
        },
        
        "Education Photography": {
            "keywords": ["education", "school", "academic", "learning", "teaching"],
            "parent": None,
            "subcategories": ["Educational Facilities", "Students & Teachers", "Educational Materials"]
        },
        "Educational Facilities": {
            "keywords": ["school building", "classroom", "university", "college",
                        "academy", "library", "auditorium", "laboratory", "campus",
                        "playground", "gymnasium"],
            "parent": "Education Photography",
            "subcategories": []
        },
        "Students & Teachers": {
            "keywords": ["student", "pupil", "teacher", "professor", "instructor",
                        "lecturer", "graduate", "graduation", "class photo"],
            "parent": "Education Photography",
            "subcategories": []
        },
        "Educational Materials": {
            "keywords": ["book", "textbook", "notebook", "bookshelf", "blackboard",
                        "whiteboard", "chalkboard", "chalk", "eraser", "ruler",
                        "compass", "calculator", "pencil case", "backpack school"],
            "parent": "Education Photography",
            "subcategories": []
        },
        
        "Industrial & Manufacturing Photography": {
            "keywords": ["industry", "industrial", "factory", "manufacturing", "production"],
            "parent": None,
            "subcategories": ["Factories & Plants", "Machinery", "Tools & Equipment", 
                            "Agriculture & Farming"]
        },
        "Factories & Plants": {
            "keywords": ["factory", "plant", "warehouse", "facility", "workshop",
                        "assembly line", "production line", "refinery", "mill"],
            "parent": "Industrial & Manufacturing Photography",
            "subcategories": []
        },
        "Machinery": {
            "keywords": ["machine", "machinery", "equipment industrial", "engine",
                        "motor", "generator", "pump", "turbine", "conveyor",
                        "robot", "automation"],
            "parent": "Industrial & Manufacturing Photography",
            "subcategories": []
        },
        "Tools & Equipment": {
            "keywords": ["tool", "equipment", "hammer", "screwdriver", "wrench",
                        "pliers", "saw", "drill", "axe", "shovel", "rake", "ladder",
                        "toolbox", "anvil", "chisel", "clamp", "crowbar", "file",
                        "grinder", "hose", "level", "nail", "screw", "bolt", "nut"],
            "parent": "Industrial & Manufacturing Photography",
            "subcategories": []
        },
        "Agriculture & Farming": {
            "keywords": ["agriculture", "farming", "farm", "farmer", "crop", "harvest",
                        "tractor", "plow", "barn", "silo", "greenhouse", "orchard",
                        "vineyard", "field farming", "plantation", "irrigation",
                        "scarecrow", "haystack", "windmill farm"],
            "parent": "Industrial & Manufacturing Photography",
            "subcategories": []
        },
        
        "Arts & Crafts Photography": {
            "keywords": ["art", "craft", "handmade", "artistic creation"],
            "parent": None,
            "subcategories": ["Fine Art", "Crafts & DIY", "Musical Instruments"]
        },
        "Fine Art": {
            "keywords": ["artwork", "painting", "drawing", "sculpture", "statue",
                        "installation", "canvas", "gallery", "exhibition", "museum",
                        "abstract art", "portrait art", "landscape art", "mural"],
            "parent": "Arts & Crafts Photography",
            "subcategories": []
        },
        "Crafts & DIY": {
            "keywords": ["craft", "handcraft", "DIY", "knitting", "sewing", "embroidery",
                        "pottery", "ceramics", "woodworking", "carving", "weaving",
                        "quilting", "origami", "scrapbook"],
            "parent": "Arts & Crafts Photography",
            "subcategories": []
        },
        "Musical Instruments": {
            "keywords": ["instrument", "musical instrument", "guitar", "piano", "violin",
                        "cello", "bass", "drum", "trumpet", "saxophone", "flute",
                        "clarinet", "harp", "banjo", "accordion", "harmonica",
                        "organ", "synthesizer", "ukulele", "mandolin"],
            "parent": "Arts & Crafts Photography",
            "subcategories": []
        },
        
        "Documentary & Journalism Photography": {
            "keywords": ["documentary", "journalism", "photojournalism", "reportage"],
            "parent": None,
            "subcategories": ["News & Current Events", "Social Issues", "Historical Documentation"]
        },
        "News & Current Events": {
            "keywords": ["news", "current event", "breaking news", "reporter",
                        "journalist", "press", "media", "coverage", "newspaper"],
            "parent": "Documentary & Journalism Photography",
            "subcategories": []
        },
        "Social Issues": {
            "keywords": ["protest", "demonstration", "rally", "march", "activism",
                        "charity", "volunteer", "community", "social"],
            "parent": "Documentary & Journalism Photography",
            "subcategories": []
        },
        "Historical Documentation": {
            "keywords": ["historical", "history", "heritage", "archive", "vintage",
                        "antique", "old", "ancient", "traditional", "legacy"],
            "parent": "Documentary & Journalism Photography",
            "subcategories": []
        },
        
        "Emergency & Safety Photography": {
            "keywords": ["emergency", "safety", "rescue", "protection"],
            "parent": None,
            "subcategories": ["Emergency Services", "Military", "Police & Security"]
        },
        "Emergency Services": {
            "keywords": ["firefighter", "fire truck", "fire engine", "fire station",
                        "ambulance", "paramedic", "rescue", "first responder"],
            "parent": "Emergency & Safety Photography",
            "subcategories": []
        },
        "Military": {
            "keywords": ["military", "army", "navy", "air force", "marine", "soldier",
                        "troop", "veteran", "uniform military", "weapon", "gun",
                        "rifle", "tank", "missile", "aircraft military", "warship",
                        "battle", "combat", "war"],
            "parent": "Emergency & Safety Photography",
            "subcategories": []
        },
        "Police & Security": {
            "keywords": ["police", "cop", "officer", "police car", "patrol", "security",
                        "guard", "surveillance", "safety"],
            "parent": "Emergency & Safety Photography",
            "subcategories": []
        },
        
        "Religious & Spiritual Photography": {
            "keywords": ["religion", "religious", "spiritual", "faith", "worship"],
            "parent": None,
            "subcategories": []
        },
        
        "Entertainment & Leisure Photography": {
            "keywords": ["entertainment", "leisure", "recreation", "fun"],
            "parent": None,
            "subcategories": ["Gaming & Toys", "Shopping & Retail", "Recreation Activities"]
        },
        "Gaming & Toys": {
            "keywords": ["game", "gaming", "video game", "toy", "doll", "puzzle",
                        "board game", "card game", "console", "arcade", "playground",
                        "swing", "slide"],
            "parent": "Entertainment & Leisure Photography",
            "subcategories": []
        },
        "Shopping & Retail": {
            "keywords": ["shop", "store", "retail", "shopping", "mall", "boutique",
                        "supermarket", "grocery", "market", "bazaar", "customer",
                        "cashier", "checkout", "sale"],
            "parent": "Entertainment & Leisure Photography",
            "subcategories": []
        },
        "Recreation Activities": {
            "keywords": ["recreation", "leisure activity", "hobby", "pastime",
                        "picnic", "camping", "fishing", "hunting", "boating",
                        "amusement park", "theme park", "fair", "carnival ride"],
            "parent": "Entertainment & Leisure Photography",
            "subcategories": []
        },
        
        "Abstract & Conceptual Photography": {
            "keywords": ["abstract", "conceptual", "concept", "idea", "symbol",
                        "metaphor", "surreal", "artistic concept", "pattern",
                        "texture abstract", "shape", "form", "line", "geometry"],
            "parent": None,
            "subcategories": []
        },
        
        "Signs & Text Photography": {
            "keywords": ["sign", "signage", "text", "word", "letter", "number",
                        "alphabet", "writing", "inscription", "caption", "title",
                        "banner", "poster", "billboard", "placard", "notice"],
            "parent": None,
            "subcategories": []
        },
    }
    
    # Track categorized tags
    categorized = {}  # tag_id -> (category_name, tag_obj)
    
    # Categorize tags (prioritize more specific subcategories first)
    # Sort categories by depth (deeper first) to ensure specific matches
    categories_by_depth = []
    for cat_name, cat_data in hierarchy_def.items():
        depth = 0
        parent = cat_data["parent"]
        while parent:
            depth += 1
            parent = hierarchy_def[parent]["parent"] if parent in hierarchy_def else None
        categories_by_depth.append((depth, cat_name, cat_data))
    
    categories_by_depth.sort(reverse=True, key=lambda x: x[0])
    
    # First pass: categorize using keywords
    for tag_obj in tags:
        tag = tag_obj['tag'].lower()
        
        for depth, category_name, category_data in categories_by_depth:
            if tag_obj['id'] in categorized:
                break
            
            keywords = category_data['keywords']
            if any(keyword in tag for keyword in keywords):
                categorized[tag_obj['id']] = (category_name, tag_obj)
                break
    
    # Build hierarchical structure
    result = {
        "model": "RAM++ (recognize-anything-plus-model)",
        "source": "xinyu1205/recognize-anything-plus-model",
        "total_tags": len(tags),
        "description": "Multi-level hierarchical categorization of RAM++ tags organized by photography genres.",
        "hierarchy": []
    }
    
    # Build category tree
    def build_category_tree(cat_name):
        cat_data = hierarchy_def[cat_name]
        node = {
            "category": cat_name,
            "tags": [],
            "subcategories": []
        }
        
        # Add tags directly in this category
        for tag_id, (assigned_cat, tag_obj) in categorized.items():
            if assigned_cat == cat_name:
                node["tags"].append(tag_obj)
        
        # Add subcategories
        for subcat in cat_data["subcategories"]:
            node["subcategories"].append(build_category_tree(subcat))
        
        # Sort tags
        node["tags"] = sorted(node["tags"], key=lambda x: x['tag'])
        node["count"] = len(node["tags"])
        
        return node
    
    # Add top-level categories
    top_level = [name for name, data in hierarchy_def.items() if data["parent"] is None]
    for cat_name in top_level:
        result["hierarchy"].append(build_category_tree(cat_name))
    
    # Add uncategorized tags
    uncategorized = [tag_obj for tag_obj in tags if tag_obj['id'] not in categorized]
    if uncategorized:
        result["hierarchy"].append({
            "category": "Other",
            "count": len(uncategorized),
            "tags": sorted(uncategorized, key=lambda x: x['tag']),
            "subcategories": []
        })
    
    return result


def print_hierarchy(node, indent=0):
    """Recursively print the hierarchy."""
    prefix = "  " * indent
    print(f"{prefix}{node['category']}: {node['count']}")
    for subcat in node.get('subcategories', []):
        print_hierarchy(subcat, indent + 1)


def main():
    """Main function."""
    tags = load_tags()
    hierarchy = categorize_tags(tags)
    
    # Save to file
    output_file = "tags_hierarchical.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    
    print("Multi-level hierarchical categorization complete!")
    print(f"  Total tags: {hierarchy['total_tags']}")
    print(f"  Top-level categories: {len([n for n in hierarchy['hierarchy'] if n['category'] != 'Other'])}")
    print()
    
    # Print hierarchy
    for node in hierarchy['hierarchy']:
        print_hierarchy(node)
    
    # Calculate Other percentage
    other_node = next((n for n in hierarchy['hierarchy'] if n['category'] == 'Other'), None)
    if other_node:
        other_percentage = (other_node['count'] / hierarchy['total_tags']) * 100
        print(f"\nOther category: {other_percentage:.1f}% of total tags")
        if other_percentage <= 5:
            print("  ✓ Target achieved: Other category is ≤ 5%")
        else:
            print(f"  ✗ Target not met: Other category should be ≤ 5% (currently {other_percentage:.1f}%)")
    
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()
