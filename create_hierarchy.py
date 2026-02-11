"""Create a hierarchical categorization of RAM++ tags."""
import json
from collections import defaultdict

with open("tags.json", encoding="utf-8") as f:
    data = json.load(f)

tags = [(t["id"], t["tag"], t["tag_chinese"], t["threshold"]) for t in data["tags"]]

# Define top-level categories with keyword patterns
categories = {
    "Animals & Wildlife": [
        "animal", "bird", "fish", "dog", "cat", "horse", "bear", "elephant", "lion",
        "tiger", "deer", "rabbit", "squirrel", "fox", "wolf", "monkey", "ape", "gorilla",
        "zebra", "giraffe", "rhino", "hippo", "kangaroo", "koala", "panda", "penguin",
        "owl", "eagle", "hawk", "parrot", "duck", "goose", "swan", "flamingo", "hen",
        "rooster", "turkey", "chicken", "pig", "cow", "sheep", "goat", "cattle", "bull",
        "insect", "bee", "butterfly", "moth", "dragonfly", "beetle", "ant", "spider",
        "snake", "lizard", "turtle", "tortoise", "frog", "toad", "crocodile", "alligator",
        "shark", "whale", "dolphin", "seal", "otter", "walrus", "crab", "lobster", "shrimp",
        "octopus", "squid", "jellyfish", "starfish", "coral", "alpaca", "llama", "camel",
    ],
    "People & Body": [
        "person", "people", "man", "woman", "child", "baby", "boy", "girl", "face",
        "head", "eye", "nose", "mouth", "lip", "ear", "hair", "hand", "finger", "arm",
        "leg", "foot", "toe", "body", "skin", "neck", "shoulder", "chest", "back",
        "belly", "waist", "hip", "knee", "ankle", "wrist", "elbow", "portrait",
        "selfie", "group", "crowd", "audience", "spectator", "actor", "actress",
        "model", "athlete", "dancer", "musician", "singer", "artist", "bride", "groom",
    ],
    "Food & Dining": [
        "food", "meal", "dish", "plate", "bowl", "cuisine", "restaurant", "dining",
        "breakfast", "lunch", "dinner", "dessert", "snack", "fruit", "vegetable",
        "meat", "fish", "seafood", "bread", "cake", "pie", "pizza", "pasta", "rice",
        "noodle", "soup", "salad", "sandwich", "burger", "sushi", "cheese", "egg",
        "milk", "coffee", "tea", "drink", "beverage", "juice", "wine", "beer", "cocktail",
        "chocolate", "candy", "cookie", "ice cream", "strawberry", "apple", "banana",
        "orange", "grape", "watermelon", "lemon", "cherry", "peach", "pear", "pineapple",
    ],
    "Architecture & Buildings": [
        "building", "house", "home", "apartment", "tower", "skyscraper", "castle",
        "palace", "temple", "church", "mosque", "cathedral", "monastery", "bridge",
        "arch", "gate", "door", "window", "roof", "wall", "column", "pillar", "stairs",
        "balcony", "porch", "deck", "fence", "shed", "barn", "warehouse", "factory",
        "office", "shop", "store", "mall", "market", "station", "terminal", "airport",
        "museum", "library", "theater", "cinema", "stadium", "arena", "gym", "pool",
    ],
    "Nature & Landscape": [
        "nature", "landscape", "scenery", "mountain", "hill", "valley", "canyon",
        "cliff", "rock", "stone", "cave", "forest", "woods", "tree", "plant", "bush",
        "grass", "flower", "leaf", "branch", "trunk", "root", "field", "meadow", "farm",
        "garden", "park", "beach", "coast", "shore", "ocean", "sea", "lake", "river",
        "stream", "waterfall", "pond", "island", "desert", "sand", "dune", "sky",
        "cloud", "sun", "moon", "star", "rainbow", "sunrise", "sunset", "weather",
        "snow", "ice", "glacier", "volcano", "jungle", "savanna", "tundra",
    ],
    "Transportation": [
        "car", "vehicle", "automobile", "truck", "bus", "van", "taxi", "motorcycle",
        "bike", "bicycle", "scooter", "train", "subway", "tram", "locomotive", "rail",
        "boat", "ship", "yacht", "sailboat", "ferry", "cruise", "aircraft", "airplane",
        "plane", "jet", "helicopter", "airport", "runway", "hangar", "road", "street",
        "highway", "traffic", "parking", "wheel", "tire", "engine", "windshield",
    ],
    "Clothing & Fashion": [
        "clothing", "clothes", "wear", "dress", "shirt", "blouse", "pants", "trousers",
        "jeans", "shorts", "skirt", "suit", "jacket", "coat", "sweater", "hoodie",
        "cardigan", "vest", "shoes", "boot", "sandal", "sneaker", "heel", "hat", "cap",
        "beanie", "helmet", "scarf", "tie", "bow", "belt", "bag", "backpack", "purse",
        "wallet", "glasses", "sunglasses", "watch", "jewelry", "necklace", "earring",
        "bracelet", "ring", "fashion", "style", "accessory", "uniform", "costume",
    ],
    "Sports & Recreation": [
        "sport", "game", "play", "ball", "football", "soccer", "basketball", "baseball",
        "tennis", "golf", "volleyball", "hockey", "cricket", "rugby", "badminton",
        "swimming", "diving", "surfing", "skiing", "snowboard", "skateboard", "skating",
        "cycling", "running", "jogging", "hiking", "climbing", "camping", "fishing",
        "hunting", "yoga", "fitness", "exercise", "workout", "gym", "competition",
        "tournament", "stadium", "arena", "court", "field", "track", "pool", "rink",
    ],
    "Technology & Electronics": [
        "computer", "laptop", "desktop", "monitor", "screen", "keyboard", "mouse",
        "phone", "smartphone", "mobile", "tablet", "camera", "television", "tv",
        "radio", "speaker", "headphone", "microphone", "printer", "scanner", "router",
        "modem", "server", "device", "gadget", "electronics", "circuit", "wire", "cable",
        "battery", "charger", "remote", "controller", "drone", "robot", "app", "software",
    ],
    "Art & Design": [
        "art", "artwork", "painting", "drawing", "sketch", "illustration", "sculpture",
        "statue", "mural", "graffiti", "canvas", "frame", "gallery", "museum", "exhibition",
        "design", "pattern", "texture", "color", "palette", "brush", "paint", "ink",
        "pencil", "marker", "crayon", "craft", "handmade", "creative", "artistic",
        "abstract", "modern", "contemporary", "traditional", "vintage", "antique",
    ],
    "Home & Interior": [
        "room", "bedroom", "bathroom", "kitchen", "living room", "dining room", "furniture",
        "table", "chair", "sofa", "couch", "bed", "desk", "shelf", "cabinet", "drawer",
        "closet", "wardrobe", "mirror", "lamp", "light", "chandelier", "curtain", "blind",
        "rug", "carpet", "pillow", "cushion", "blanket", "sheet", "towel", "appliance",
        "refrigerator", "oven", "stove", "microwave", "dishwasher", "washer", "dryer",
    ],
    "Objects & Items": [
        "object", "item", "thing", "tool", "equipment", "instrument", "device", "container",
        "box", "bottle", "jar", "can", "bucket", "basket", "bag", "package", "paper",
        "book", "magazine", "newspaper", "card", "envelope", "pen", "pencil", "notebook",
        "clock", "watch", "calendar", "key", "lock", "switch", "button", "handle",
        "knob", "screw", "nail", "hammer", "wrench", "scissors", "knife", "fork", "spoon",
    ],
    "Events & Activities": [
        "event", "party", "celebration", "festival", "ceremony", "wedding", "birthday",
        "concert", "show", "performance", "exhibition", "conference", "meeting", "class",
        "lesson", "workshop", "parade", "protest", "demonstration", "competition",
        "race", "match", "game", "tournament", "vacation", "travel", "trip", "tour",
        "shopping", "cooking", "baking", "cleaning", "reading", "writing", "studying",
    ],
    "Weather & Environment": [
        "weather", "climate", "temperature", "rain", "snow", "storm", "thunder",
        "lightning", "wind", "breeze", "fog", "mist", "haze", "sunshine", "cloudy",
        "overcast", "clear", "hot", "cold", "warm", "cool", "humid", "dry", "wet",
        "flood", "drought", "pollution", "smoke", "dust", "environment", "ecology",
    ],
    "Abstract & Concepts": [
        "concept", "idea", "thought", "emotion", "feeling", "happy", "sad", "angry",
        "fear", "love", "peace", "war", "freedom", "justice", "truth", "beauty",
        "time", "space", "infinity", "future", "past", "present", "life", "death",
        "dream", "reality", "fantasy", "imagination", "memory", "hope", "faith",
        "symbol", "sign", "icon", "logo", "emblem", "flag", "pattern", "shape",
    ],
}

# Categorize tags
categorized = defaultdict(list)
uncategorized = []

for tag_id, tag, tag_zh, threshold in tags:
    tag_lower = tag.lower()
    matched = False
    
    for category, keywords in categories.items():
        if any(keyword in tag_lower for keyword in keywords):
            categorized[category].append({
                "id": tag_id,
                "tag": tag,
                "tag_chinese": tag_zh,
                "threshold": threshold,
            })
            matched = True
            break
    
    if not matched:
        uncategorized.append({
            "id": tag_id,
            "tag": tag,
            "tag_chinese": tag_zh,
            "threshold": threshold,
        })

# Build hierarchical output
hierarchy = {
    "model": "RAM++ (recognize-anything-plus-model)",
    "source": "xinyu1205/recognize-anything-plus-model",
    "total_tags": len(tags),
    "description": "Hierarchical categorization of RAM++ tags. Tags are grouped by semantic category.",
    "categories": []
}

for category in sorted(categories.keys()):
    if categorized[category]:
        hierarchy["categories"].append({
            "category": category,
            "count": len(categorized[category]),
            "tags": sorted(categorized[category], key=lambda x: x["tag"])
        })

if uncategorized:
    hierarchy["categories"].append({
        "category": "Other",
        "count": len(uncategorized),
        "tags": sorted(uncategorized, key=lambda x: x["tag"])
    })

with open("tags_hierarchical.json", "w", encoding="utf-8") as f:
    json.dump(hierarchy, f, indent=2, ensure_ascii=False)

# Print summary
print("Hierarchical categorization complete:")
print(f"  Total tags: {len(tags)}")
print(f"  Categories: {len(hierarchy['categories'])}")
print()
for cat in hierarchy["categories"]:
    print(f"  {cat['category']}: {cat['count']} tags")
print()
print("Saved to tags_hierarchical.json")
