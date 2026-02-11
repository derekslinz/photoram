#!/usr/bin/env python3
"""
Create a hierarchical categorization of RAM++ tags organized by photography genres.
"""

import json
from pathlib import Path
from typing import Dict, List, Set


def load_tags(filepath: str = "tags.json") -> List[Dict]:
    """Load tags from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tags']


def categorize_tags(tags: List[Dict]) -> Dict:
    """Categorize tags into a hierarchical structure based on photography genres."""
    
    categories = {
        "Portrait Photography": {
            "keywords": ["portrait", "face", "people", "person", "man", "woman", "child", "boy", "girl", 
                        "baby", "selfie", "couple", "family", "crowd", "group", "male", "female",
                        "head", "headshot", "expression", "smile", "laugh", "cry", "emotion",
                        "model", "pose", "poser", "actor", "actress", "celebrity", "bride", "groom",
                        "arm", "ankle", "back", "belly", "cheek", "chin", "forehead", "wrist",
                        "elbow", "knee", "hip", "waist", "neck", "shoulder", "chest"],
            "tags": []
        },
        "Landscape Photography": {
            "keywords": ["landscape", "mountain", "hill", "valley", "vista", "scenery", "horizon",
                        "panorama", "overlook", "cliff", "canyon", "plateau", "ridge", "peak",
                        "countryside", "rural", "farmland", "prairie", "plain", "desert",
                        "dune", "oasis", "mesa", "butte", "alp", "badlands"],
            "tags": []
        },
        "Wildlife Photography": {
            "keywords": ["wildlife", "wild animal", "safari", "predator", "prey", "mammal in nature",
                        "lion", "tiger", "elephant", "giraffe", "zebra", "rhino", "hippo",
                        "bear", "wolf", "deer", "moose", "elk", "buffalo", "bison",
                        "antelope", "gazelle", "leopard", "cheetah", "hyena", "fox", "coyote"],
            "tags": []
        },
        "Nature Photography": {
            "keywords": ["nature", "forest", "tree", "plant", "flower", "garden", "leaf", "foliage",
                        "botanical", "flora", "fern", "moss", "lichen", "fungus", "mushroom",
                        "grass", "meadow", "field", "blossom", "bloom", "petal", "stem",
                        "branch", "trunk", "root", "vine", "bush", "shrub", "hedge",
                        "algae", "aloe vera", "azalea", "bamboo", "birch",
                        "cactus", "carnation", "chrysanthemum", "clover", "daffodil",
                        "daisy", "dandelion", "fir", "geranium", "hibiscus", "holly",
                        "hyacinth", "hydrangea", "iris", "ivy", "jasmine", "lavender",
                        "lilac", "lily", "lotus", "magnolia", "maple", "marigold",
                        "oak", "orchid", "palm", "pansy", "peony", "petunia", "pine",
                        "poppy", "rose", "sage", "sunflower", "tulip", "violet", "willow"],
            "tags": []
        },
        "Macro & Close-up Photography": {
            "keywords": ["macro", "close-up", "closeup", "detail", "insect", "butterfly", "bee",
                        "beetle", "dragonfly", "ladybug", "spider", "ant", "fly", "moth",
                        "caterpillar", "cricket", "grasshopper", "magnify", "magnified",
                        "texture detail", "water drop", "dewdrop", "crystal"],
            "tags": []
        },
        "Architectural Photography": {
            "keywords": ["architecture", "building", "structure", "skyscraper", "tower", "bridge",
                        "church", "cathedral", "temple", "mosque", "synagogue", "palace", "castle",
                        "fortress", "monument", "memorial", "statue", "construction", "facade",
                        "column", "pillar", "arch", "dome", "spire", "steeple",
                        "aqueduct", "arena", "balustrade", "big ben"],
            "tags": []
        },
        "Urban & Street Photography": {
            "keywords": ["street", "urban", "city", "downtown", "metro", "metropolitan", "alley",
                        "sidewalk", "crosswalk", "intersection", "traffic", "pedestrian",
                        "graffiti", "mural", "street art", "storefront", "shop", "market",
                        "square", "plaza", "district", "neighborhood", "cityscape", "skyline",
                        "avenue", "aisle", "arcade"],
            "tags": []
        },
        "Food Photography": {
            "keywords": ["food", "meal", "dish", "cuisine", "plate", "bowl", "culinary", "recipe",
                        "ingredient", "fruit", "vegetable", "meat", "seafood", "dessert", "cake",
                        "pastry", "bread", "pizza", "pasta", "soup", "salad", "sandwich", "burger",
                        "sushi", "steak", "cheese", "chocolate", "ice cream", "cookie",
                        "fries", "toast", "bacon", "egg", "avocado", "almond", "apricot",
                        "asparagus", "abalone", "acorn", "banana", "berry", "biscuit",
                        "bagel", "barbecue", "barley", "basil", "bean", "beef", "bento",
                        "bibimbap", "chicken", "pork", "lamb", "rice", "noodle", "dumpling",
                        "apple", "baguette", "bell pepper", "baozi", "baking",
                        "brussels sprout", "cashew", "cherry tomato", "crab", "cream",
                        "daffodil", "herb", "jujube", "lavender", "lilac", "melon",
                        "cannoli", "caramel", "carrot", "celery", "cereal", "cherry", "chestnut",
                        "cinnamon", "clam", "coconut", "cod", "corn", "crab", "cracker",
                        "cranberry", "croissant", "cucumber", "cupcake", "curry", "donut",
                        "edamame", "eggplant", "enchilada", "fig", "flatbread", "fondue",
                        "garlic", "ginger", "grape", "grapefruit", "gravy", "guacamole",
                        "ham", "hazelnut", "honey", "hot dog", "hummus", "jam", "jelly",
                        "kale", "kebab", "ketchup", "kiwi", "kumquat", "lasagna", "leek",
                        "lemon", "lentil", "lettuce", "lime", "lobster", "lychee", "mango",
                        "maple syrup", "marshmallow", "mayonnaise", "meatball", "miso",
                        "muffin", "mushroom", "mussel", "mustard", "nacho", "nectar",
                        "nutmeg", "oatmeal", "olive", "omelette", "onion", "orange",
                        "oregano", "oyster", "pancake", "papaya", "paprika", "parsley",
                        "parsnip", "passion fruit", "peach", "peanut", "pear", "peas",
                        "pecan", "pepper", "pickle", "pie", "pineapple", "pistachio",
                        "plum", "pomegranate", "popcorn", "potato", "pretzel", "prune",
                        "pudding", "pumpkin", "quinoa", "radish", "raisin", "raspberry",
                        "rhubarb", "rosemary", "sage", "salmon", "salt", "sardine",
                        "sauce", "sausage", "scallion", "scallop", "seaweed", "sesame",
                        "shallot", "shrimp", "snack", "sorbet", "soy", "spaghetti",
                        "spinach", "squash", "strawberry", "sugar", "sushi", "sweet potato",
                        "taco", "tangerine", "tart", "thyme", "tiramisu", "tofu", "tomato",
                        "tuna", "turkey", "turmeric", "turnip", "vanilla", "vinegar",
                        "waffle", "walnut", "watermelon", "yam", "yogurt", "zucchini"],
            "tags": []
        },
        "Beverage & Drink Photography": {
            "keywords": ["drink", "beverage", "coffee", "tea", "juice", "smoothie", "cocktail",
                        "wine", "beer", "whiskey", "vodka", "rum", "champagne", "soda",
                        "water bottle", "cup", "mug", "glass", "bottle", "bar", "bartend"],
            "tags": []
        },
        "Fashion Photography": {
            "keywords": ["fashion", "style", "clothing", "clothes", "dress", "suit", "gown",
                        "outfit", "attire", "wear", "garment", "textile", "fabric", "runway",
                        "catwalk", "designer", "haute couture", "trendy", "fashionable"],
            "tags": []
        },
        "Apparel & Accessories": {
            "keywords": ["shirt", "pants", "skirt", "jacket", "coat", "sweater", "hoodie",
                        "shoe", "boot", "sneaker", "sandal", "hat", "cap", "beanie", "helmet",
                        "scarf", "tie", "belt", "glove", "sock", "underwear", "swimsuit",
                        "uniform", "costume", " jewelry", "necklace", "bracelet", "ring", "earring",
                        "accessory", "anklet", "armband", "apron", "backpack", "beret",
                        "bib", "bikini"],
            "tags": []
        },
        "Sports Photography": {
            "keywords": ["sport", "athletic", "athlete", "competition", "championship", "tournament",
                        "soccer", "football", "basketball", "baseball", "tennis", "golf", "hockey",
                        "volleyball", "cricket", "rugby", "boxing", "wrestling", "race", "racing",
                        "marathon", "sprint", "jump", "throw", "kick", "score", "goal",
                        "badminton", "ballet", "ballerina", "billard"],
            "tags": []
        },
        "Action & Recreation Photography": {
            "keywords": ["action", "recreation", "activity", "exercise", "fitness", "gym", "workout",
                        "run", "jog", "hike", "climb", "ski", "snowboard", "surf", "skate",
                        "dive", "swim", "bike", "cycle", "kayak", "canoe", "raft", "paraglide",
                        "aerobics", "athletic", "adventure"],
            "tags": []
        },
        "Automotive Photography": {
            "keywords": ["car", "automobile", "vehicle", "truck", "van", "suv", "sedan", "coupe",
                        "convertible", "sports car", "race car", "classic car", "vintage car",
                        "muscle car", "luxury car", "engine", "wheel", "tire", "dashboard",
                        "garage", "parking", "auto show", "dealership"],
            "tags": []
        },
        "Transportation Photography": {
            "keywords": ["transport", "bus", "train", "railway", "railroad", "locomotive", "subway",
                        "tram", "trolley", "taxi", "motorcycle", "scooter", "bicycle", "bike",
                        "road", "highway", "freeway", "turnpike", "route", "journey"],
            "tags": []
        },
        "Aviation Photography": {
            "keywords": ["airplane", "aircraft", "plane", "jet", "fighter jet", "helicopter", "chopper",
                        "aviation", "flight", "fly", "airport", "runway", "hangar", "cockpit",
                        "pilot", "airline", "airliner", "propeller", "wing", "tail"],
            "tags": []
        },
        "Marine & Nautical Photography": {
            "keywords": ["boat", "ship", "vessel", "yacht", "sailboat", "catamaran", "cruise ship",
                        "ferry", "cargo ship", "tanker", "submarine", "port", "harbor", "dock",
                        "pier", "marina", "nautical", "maritime", "naval", "sailor", "captain"],
            "tags": []
        },
        "Aerial & Drone Photography": {
            "keywords": ["aerial", "overhead", "bird's eye", "drone", "bird view", "top view",
                        "from above", "fly over", "airborne", "elevated view"],
            "tags": []
        },
        "Astrophotography": {
            "keywords": ["star", "planet", "moon", "sun", "galaxy", "nebula", "constellation",
                        "astronomy", "space", "cosmos", "celestial", "milky way", "meteor",
                        "comet", "eclipse", "aurora", "night sky", "telescope", "observatory"],
            "tags": []
        },
        "Travel Photography": {
            "keywords": ["travel", "tourism", "tourist", "vacation", "holiday", "destination",
                        "landmark", "attraction", "sightseeing", "tour", "trip", "journey",
                        "explore", "expedition", "resort", "hotel", "hostel",
                        "disneyland", "ancient"],
            "tags": []
        },
        "Event Photography": {
            "keywords": ["event", "ceremony", "celebration", "festival", "carnival", "parade",
                        "concert", "show", "performance", "exhibition", "conference", "convention",
                        "wedding", "marriage", "reception", "birthday", "anniversary", "graduation",
                        "party", "gathering", "meeting", "banquet", "baptism", "auction"],
            "tags": []
        },
        "Documentary Photography": {
            "keywords": ["documentary", "journalism", "photojournalism", "news", "reporter",
                        "press", "media", "coverage", "report", "story", "narrative",
                        "social issue", "protest", "demonstration", "rally", "conflict"],
            "tags": []
        },
        "Fine Art Photography": {
            "keywords": ["art", "artwork", "artistic", "fine art", "installation", "sculpture",
                        "painting", "drawing", "canvas", "gallery", "exhibition", "museum",
                        "abstract", "surreal", "conceptual", "creative", "imagination"],
            "tags": []
        },
        "Still Life Photography": {
            "keywords": ["still life", "arrangement", "composition", "tabletop", "setup",
                        "vase", "bouquet", "flower arrangement"],
            "tags": []
        },
        "Product Photography": {
            "keywords": ["product", "commercial", "merchandise", "goods", "item for sale",
                        "packaging", "package", "box", "container", "brand", "branding",
                        "logo", "label", "advertisement", "marketing", "catalog"],
            "tags": []
        },
        "Interior Photography": {
            "keywords": ["interior", "room", "bedroom", "bathroom", "living room", "kitchen",
                        "dining room", "office", "lobby", "hallway", "corridor", "staircase",
                        "furniture", "chair", "table", "sofa", "couch", "bed", "desk",
                        "shelf", "cabinet", "closet", "decor", "decoration",
                        "alcove", "atrium", "balcony", "basement", "bench",
                        "ceiling", "ceiling fan", "chandelier", "clock", "counter",
                        "curtain", "door", "elevator", "entrance", "fireplace",
                        "fixture", "floor", "futon", "lamp", "ledge", "mirror",
                        "tile", "wall", "window"],
            "tags": []
        },
        "Real Estate Photography": {
            "keywords": ["house", "home", "apartment", "condo", "loft", "cottage", "cabin",
                        "mansion", "villa", "estate", "property", "residence", "dwelling",
                        "real estate", "for sale", "listing"],
            "tags": []
        },
        "Underwater Photography": {
            "keywords": ["underwater", "scuba", "dive", "diving", "snorkel", "submarine",
                        "coral reef", "reef", "marine life", "fish", "shark", "whale", "dolphin",
                        "octopus", "jellyfish", "sea turtle", "tropical fish", "aquatic"],
            "tags": []
        },
        "Pet Photography": {
            "keywords": ["pet", "dog", "puppy", "cat", "kitten", "domestic animal", "companion animal",
                        "golden retriever", "labrador", "poodle", "bulldog", "terrier", "shepherd",
                        "collie", "husky", "chihuahua", "persian cat", "siamese", "tabby",
                        "american shorthair", "bichon"],
            "tags": []
        },
        "Animal Photography": {
            "keywords": ["animal", "creature", "beast", "bird", "parrot", "eagle", "owl", "hawk",
                        "pigeon", "sparrow", "crow", "swan", "duck", "goose", "flamingo", "penguin",
                        "horse", "pony", "donkey", "cow", "bull", "pig", "sheep", "goat",
                        "chicken", "rooster", "hen", "turkey", "rabbit", "hamster", "guinea pig",
                        "reptile", "lizard", "snake", "turtle", "tortoise", "frog", "toad",
                        "alpaca", "armadillo", "ape", "baboon", "beaver", "bat", "camel",
                        "canary", "chipmunk", "cockatoo", "cocker", "coyote", "cub",
                        "dragon", "dragonfly", "egret", "falcon", "fawn", "ferret", "finch",
                        "flea", "gerbil", "gorilla", "grasshopper", "gull", "hamster",
                        "hedgehog", "heron", "hornet", "hyena", "iguana", "jackal",
                        "jaguar", "jay", "kangaroo", "koala", "lemur", "leopard",
                        "llama", "lynx", "macaw", "mole", "mongoose", "mule", "otter",
                        "panther", "peacock", "pelican", "pheasant", "porcupine", "possum",
                        "quail", "raccoon", "raven", "scorpion", "seal", "skunk",
                        "sloth", "snail", "squirrel", "stork", "swallow", "vulture",
                        "weasel", "woodpecker", "worm", "yak", "zebra"],
            "tags": []
        },
        "Aquarium & Zoo Photography": {
            "keywords": ["aquarium", "zoo", "cage", "enclosure", "exhibit", "sanctuary",
                        "animal park", "safari park", "captivity", "captive animal"],
            "tags": []
        },
        "Seascape & Beach Photography": {
            "keywords": ["ocean", "sea", "beach", "shore", "coast", "coastline", "seaside",
                        "wave", "surf", "tide", "sand", "seashell", "driftwood", "boardwalk"],
            "tags": []
        },
        "Water Photography": {
            "keywords": ["water", "lake", "pond", "river", "stream", "creek", "brook",
                        "waterfall", "cascade", "rapids", "dam", "reservoir"],
            "tags": []
        },
        "Weather Photography": {
            "keywords": ["weather", "rain", "storm", "thunderstorm", "lightning", "thunder",
                        "snow", "snowfall", "blizzard", "hail", "fog", "mist", "cloud",
                        "wind", "tornado", "hurricane", "rainbow"],
            "tags": []
        },
        "Season & Time Photography": {
            "keywords": ["season", "spring", "summer", "autumn", "fall", "winter",
                        "sunrise", "sunset", "dawn", "dusk", "twilight", "golden hour",
                        "blue hour", "day", "night", "evening", "morning", "afternoon"],
            "tags": []
        },
        "Light & Color Photography": {
            "keywords": ["light", "lighting", "illumination", "glow", "shine", "bright",
                        "shadow", "silhouette", "backlight", "sunlight", "moonlight",
                        "color", "red", "blue", "green", "yellow", "orange", "purple",
                        "pink", "brown", "black", "white", "gray", "grey", "colorful"],
            "tags": []
        },
        "Materials & Textures": {
            "keywords": ["material", "texture", "surface", "wood", "wooden", "timber", "lumber",
                        "metal", "metallic", "steel", "iron", "copper", "brass", "bronze",
                        "gold", "silver", "aluminum", "stone", "rock", "marble", "granite",
                        "brick", "concrete", "cement", "plastic", "rubber", "glass",
                        "fabric", "cloth", "textile", "leather", "silk", "cotton", "wool",
                        "paper", "cardboard", "ceramic", "porcelain", "clay"],
            "tags": []
        },
        "Gemstones & Minerals": {
            "keywords": ["gem", "gemstone", "jewel", "diamond", "ruby", "emerald", "sapphire",
                        "pearl", "crystal", "quartz", "amethyst", "topaz", "opal", "jade",
                        "amber", "mineral", "ore"],
            "tags": []
        },
        "Tools & Equipment": {
            "keywords": ["tool", "equipment", "instrument", "device", "apparatus", "implement",
                        "hammer", "screwdriver", "wrench", "pliers", "saw", "drill",
                        "axe", "shovel", "rake", "ladder", "workbench", "toolbox",
                        "abacus", "anchor", "anvil", "cable", "chain", "chisel",
                        "clamp", "cleaner", "compass", "crowbar", "eraser", "file",
                        "grinder", "hose", "knitting needle", "laser", "level",
                        "magnet", "measuring tape", "nail", "needle", "nut", "padlock",
                        "pulley", "pump", "razor", "rope", "ruler", "sandpaper",
                        "screw", "shears", "sickle", "spool", "tongs", "trowel",
                        "tweezers", "vise", "wedge", "wire"],
            "tags": []
        },
        "Technology & Electronics": {
            "keywords": ["technology", "electronic", "digital", "computer", "laptop", "desktop",
                        "phone", "smartphone", "mobile", "tablet", "ipad", "screen", "monitor",
                        "keyboard", "mouse", "printer", "scanner", "camera", "lens",
                        "television", "tv", "radio", "speaker", "headphone", "microphone",
                        "projector", "remote control", "CD", "DVD", "USB", "hard drive",
                        "Wii", "app", "atm", "amplifier", "alarm"],
            "tags": []
        },
        "Musical Instruments": {
            "keywords": ["instrument", "music", "musical", "guitar", "piano", "keyboard", "violin",
                        "cello", "bass", "drum", "trumpet", "saxophone", "flute", "clarinet",
                        "harp", "banjo", "accordion", "harmonica"],
            "tags": []
        },
        "Household Items": {
            "keywords": ["household", "appliance", "refrigerator", "fridge", "stove", "oven",
                        "microwave", "dishwasher", " washing machine", "dryer", "vacuum",
                        "iron", "toaster", "blender", "mixer", "kettle", "pot", "pan",
                        "knife", "fork", "spoon", "cup", "mug", "glass", "plate", "bowl",
                        "basket", "bucket", "broom", "mop", "air conditioner", "alarm clock",
                        "ashtray", "bag", "backpack", "balloon", "band aid", "bandage",
                        "basin", "bath mat", "bath towel", "bathrobe", "battery", "binder",
                        "binocular"],
            "tags": []
        },
        "Business & Office": {
            "keywords": ["office", "business", "corporate", "workplace", "desk", "cubicle",
                        "meeting room", "boardroom", "reception", "lobby", "secretary",
                        "manager", "executive", "employee", "worker", "colleague",
                        "document", "paper", "file", "folder", "notebook", "pen", "pencil",
                        "calculator", "stapler", "briefcase", "bank", "atm"],
            "tags": []
        },
        "Education & Learning": {
            "keywords": ["education", "school", "classroom", "university", "college", "academy",
                        "student", "teacher", "professor", "instructor", "lesson", "lecture",
                        "study", "learn", "book", "textbook", "library", "bookshelf",
                        "blackboard", "whiteboard", "chalkboard", "graduation", "auditorium",
                        "atlas"],
            "tags": []
        },
        "Medical & Healthcare": {
            "keywords": ["medical", "health", "healthcare", "hospital", "clinic", "doctor",
                        "physician", "nurse", "patient", "surgery", "operation", "emergency",
                        "ambulance", "medicine", "medication", "pill", "syringe", "stethoscope",
                        "x-ray", "scan", "diagnosis", "treatment", "therapy"],
            "tags": []
        },
        "Science & Research": {
            "keywords": ["science", "scientific", "research", "laboratory", "lab", "experiment",
                        "test", "analyze", "microscope", "telescope", "beaker", "flask",
                        "scientist", "researcher", "chemist", "biologist", "physicist",
                        "chemistry", "biology", "physics", "astronomy", "astronomer"],
            "tags": []
        },
        "Religion & Spirituality": {
            "keywords": ["religion", "religious", "spiritual", "worship", "prayer", "pray",
                        "altar", "shrine", "icon", "cross", "crucifix", "rosary",
                        "bible", "quran", "torah", "monk", "nun", "priest", "pastor",
                        "rabbi", "imam", "meditation", "zen"],
            "tags": []
        },
        "Holiday & Seasonal Celebrations": {
            "keywords": ["christmas", "halloween", "easter", "thanksgiving", "valentine",
                        "new year", "birthday", "holiday decoration", "santa", "elf",
                        "pumpkin", "candy", "gift", "present", "ornament"],
            "tags": []
        },
        "Cosmetics & Beauty Products": {
            "keywords": ["cosmetics", "makeup", "lipstick", "beauty", "perfume", "fragrance",
                        "nail polish", "powder", "mascara", "eyeshadow", "blush"],
            "tags": []
        },
        "Decorative & Home Decor": {
            "keywords": ["decor", "decoration", "ornament", "statue figurine", "candle",
                        "curtain", "drape", "lamp post", "chandelier", "centerpiece",
                        "wreath", "garland"],
            "tags": []
        },
        "Abstract Concepts & Actions": {
            "keywords": ["concept", "idea", "abstract art", "pattern design", "graphic design",
                        "appear", "disappear", "transform", "create", "destroy", "move"],
            "tags": []
        },
        "Military & Defense": {
            "keywords": ["military", "army", "navy", "air force", "soldier", "troop", "veteran",
                        "uniform military", "weapon", "gun", "rifle", "pistol", "tank",
                        "missile", "bomb", "warfare", "combat", "battle", "war"],
            "tags": []
        },
        "Emergency Services": {
            "keywords": ["emergency", "rescue", "firefighter", "fire truck", "fire engine",
                        "police", "cop", "officer", "police car", "patrol"],
            "tags": []
        },
        "Agriculture & Farming": {
            "keywords": ["agriculture", "farming", "farm", "farmer", "crop", "harvest",
                        "tractor", "plow", "barn", "silo", "greenhouse", "orchard",
                        "vineyard", "field crop", "plantation", "irrigation"],
            "tags": []
        },
        "Industry & Manufacturing": {
            "keywords": ["industry", "industrial", "factory", "manufacturing", "manufacture",
                        "production", "assembly", "warehouse", "machinery", "machine",
                        "conveyor", "pipeline", "refinery", "plant"],
            "tags": []
        },
        "Professions & Occupations": {
            "keywords": ["profession", "occupation", "job", "career", "work", "worker",
                        "chef", "cook", "waiter", "waitress", "barista", "mechanic",
                        "carpenter", "plumber", "electrician", "painter", "builder",
                        "architect", "engineer", "designer", "artist", "photographer",
                        "writer", "author", "journalist", "lawyer", "judge", "accountant",
                        "astronaut", "baker"],
            "tags": []
        },
        "Shopping & Retail": {
            "keywords": ["shop", "store", "retail", "shopping", "mall", "boutique",
                        "supermarket", "grocery", "bakery", "butcher", "market", "bazaar",
                        "customer", "shopper", "cashier", "checkout", "sale", "discount"],
            "tags": []
        },
        "Entertainment & Media": {
            "keywords": ["entertainment", "entertain", "theatre", "theater", "cinema", "movie",
                        "film", "screen", "stage", "audience", "cartoon", "anime", "animation",
                        "comedy", "drama", "action film", "documentary film", "animator",
                        "album", "audio"],
            "tags": []
        },
        "Gaming & Toys": {
            "keywords": ["game", "gaming", "video game", "console", "controller", "Wii",
                        "toy", "doll", "teddy bear", "puzzle", "board game", "card game",
                        "play", "playground", "swing", "slide"],
            "tags": []
        },
        "Signs & Text": {
            "keywords": ["sign", "signage", "banner", "poster", "billboard", "placard",
                        "text", "word", "letter", "number", "alphabet", "writing",
                        "inscription", "graffiti text", "caption", "title", "label"],
            "tags": []
        },
        "Symbols & Icons": {
            "keywords": ["symbol", "icon", "emblem", "badge", "logo", "flag", "banner symbol"],
            "tags": []
        },
    }
    
    # Track which tags have been categorized
    categorized = set()
    
    # First pass: categorize tags based on keywords - use simple substring matching
    for tag_obj in tags:
        tag = tag_obj['tag'].lower()
        
        for category_name, category_data in categories.items():
            # Check if any keyword matches using simple substring matching
            keywords = category_data['keywords']
            if any(keyword in tag for keyword in keywords):
                category_data['tags'].append(tag_obj)
                categorized.add(tag_obj['id'])
                break
    
    # Second pass: collect remaining tags into "Other"
    other_tags = [tag_obj for tag_obj in tags if tag_obj['id'] not in categorized]
    
    # Build the final structure
    result = {
        "model": "RAM++ (recognize-anything-plus-model)",
        "source": "xinyu1205/recognize-anything-plus-model",
        "total_tags": len(tags),
        "description": "Hierarchical categorization of RAM++ tags organized by photography genres and subject matter.",
        "categories": []
    }
    
    # Add categories with tags
    for category_name, category_data in categories.items():
        if category_data['tags']:
            result['categories'].append({
                "category": category_name,
                "count": len(category_data['tags']),
                "tags": sorted(category_data['tags'], key=lambda x: x['tag'])
            })
    
    # Add "Other" category
    if other_tags:
        result['categories'].append({
            "category": "Other",
            "count": len(other_tags),
            "tags": sorted(other_tags, key=lambda x: x['tag'])
        })
    
    # Sort categories by count (descending)
    result['categories'].sort(key=lambda x: x['count'], reverse=True)
    
    return result


def main():
    """Main function."""
    tags = load_tags()
    hierarchy = categorize_tags(tags)
    
    # Save to file
    output_file = "tags_hierarchical.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    
    print(f"Hierarchical categorization complete!")
    print(f"  Total tags: {hierarchy['total_tags']}")
    print(f"  Categories: {len(hierarchy['categories'])}")
    print()
    
    # Calculate "Other" percentage
    other_count = 0
    for category in hierarchy['categories']:
        print(f"  {category['category']}: {category['count']}")
        if category['category'] == 'Other':
            other_count = category['count']
    
    if other_count > 0:
        other_percentage = (other_count / hierarchy['total_tags']) * 100
        print(f"\n  Other category: {other_percentage:.1f}% of total tags")
        if other_percentage <= 5:
            print("  ✓ Target achieved: Other category is ≤ 5%")
        else:
            print(f"  ✗ Target not met: Other category should be ≤ 5% (currently {other_percentage:.1f}%)")
    
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()
