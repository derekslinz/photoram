#!/usr/bin/env python3
"""
Build dual-tree ontology from ontology_deep_hierarchy.json

FACETS tree: Use hierarchy paths as-is (ground truth)
GENRES tree: Route tags to photography genres based on hierarchy + branch
"""

import json
from collections import defaultdict
from typing import Dict, List, Set


def load_deep_hierarchy(filepath: str = "ontology_deep_hierarchy.json") -> Dict:
    """Load the deep hierarchy ontology."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def classify_genre(tag: str, hierarchy: List[str], branch: str) -> str:
    """
    Route a tag to a photography genre based on its hierarchy and branch.
    
    Rules:
    - Style branches → Digital Art & Illustration
    - Technique branches → stay in FACETS only
    - Sport hierarchies → Sports & Action
    - Social Event hierarchies → Events
    - People hierarchies → People & Portrait
    - Animal hierarchies (wild) → Wildlife
    - Animal hierarchies (pets) → People & Portrait
    - Food hierarchies → Food & Drink
    - Natural landscapes → Landscape & Nature
    - Urban spaces → Street & Documentary / Architecture
    - Buildings → Architecture & Interiors
    - Vehicles → Transportation
    - Abstract/Visual → Abstract & Texture
    """
    tag_lower = tag.lower()
    hierarchy_str = " → ".join(hierarchy).lower()
    
    # Technique branches don't map to genres
    if branch == "TECHNICAL_PHOTO":
        return None
    
    # Style branches
    if branch == "ATTRIBUTE_STYLE":
        return "Digital Art & Illustration"
    
    # Sport activities
    if "sport" in hierarchy_str or "athletics" in hierarchy_str:
        return "Sports & Action"
    
    # Social events
    if "social event" in hierarchy_str or "ceremony" in hierarchy_str:
        return "Events"
    
    # Creative activities
    if "creative activity" in hierarchy_str:
        return "Creative & Artistic"
    
    # People
    if branch == "SUBJECT_PEOPLE" or "human" in hierarchy_str:
        return "People & Portrait"
    
    # Animals - distinguish pets from wildlife
    if branch == "SUBJECT_ANIMAL" or "animal" in hierarchy_str:
        # Pets go to People & Portrait
        pet_keywords = ['dog', 'cat', 'puppy', 'kitten', 'pet']
        if any(kw in tag_lower for kw in pet_keywords):
            return "People & Portrait"
        # Wild animals go to Wildlife
        return "Wildlife"
    
    # Food
    if branch == "SUBJECT_FOOD" or "food" in hierarchy_str:
        return "Food & Drink"
    
    # Locations - natural vs urban
    if branch == "SCENE_LOCATION":
        # Natural landscapes
        if any(term in hierarchy_str for term in ['natural landscape', 'mountain', 'forest', 
                                                   'coastal', 'water body', 'desert', 'field']):
            return "Landscape & Nature"
        
        # Urban spaces
        if any(term in hierarchy_str for term in ['urban space', 'city', 'street']):
            return "Street & Documentary"
        
        # Indoor commercial/public spaces
        if any(term in hierarchy_str for term in ['commercial space', 'public venue']):
            return "Architecture & Interiors"
        
        # Transportation hubs
        if 'transportation hub' in hierarchy_str:
            return "Travel"
        
        # Default indoor spaces
        if 'indoor space' in hierarchy_str:
            return "Architecture & Interiors"
        
        # Default location
        return "Landscape & Nature"
    
    # Objects - categorize by type
    if branch == "SUBJECT_OBJECT":
        # Vehicles
        if 'vehicle' in hierarchy_str:
            return "Transportation"
        
        # Buildings
        if 'building' in hierarchy_str or 'structure' in hierarchy_str:
            return "Architecture & Interiors"
        
        # Electronics & tools
        if any(term in hierarchy_str for term in ['electronics', 'tool', 'machine']):
            return "Product & Commercial"
        
        # Furniture
        if 'furniture' in hierarchy_str:
            return "Architecture & Interiors"
        
        # Default objects
        return "Still Life"
    
    # Visual attributes
    if branch == "ATTRIBUTE_VISUAL":
        return "Abstract & Texture"
    
    # Concepts
    if branch == "CONCEPT_ABSTRACT":
        return "Conceptual"
    
    # Activities (not covered above)
    if branch == "ACTIVITY_ACTION":
        # Work activities
        if 'work' in hierarchy_str or 'labor' in hierarchy_str:
            return "Documentary"
        
        # Daily activities
        if 'daily activity' in hierarchy_str:
            return "Lifestyle"
        
        # Travel
        if 'travel' in hierarchy_str:
            return "Travel"
        
        # Default activity
        return "Lifestyle"
    
    # Default fallback
    return "Other"


def build_facets_tree(deep_hierarchy: Dict) -> List[Dict]:
    """
    Build FACETS tree directly from hierarchy paths.
    
    Structure: FACETS/{Branch}/{Hierarchy...}/{tag}
    Example: FACETS/Activity/Sport/Ball Sport/basketball game
    """
    facets = {}
    
    for branch_data in deep_hierarchy['branches']:
        branch_name = branch_data['branch']
        
        # Initialize branch structure
        if branch_name not in facets:
            facets[branch_name] = {
                'branch': branch_name,
                'total_tags': 0,
                'hierarchy_tree': {}
            }
        
        # Process each tag
        for tag_entry in branch_data['tags']:
            hierarchy = tag_entry['hierarchy']
            
            # Build nested structure from hierarchy
            current_level = facets[branch_name]['hierarchy_tree']
            
            # Navigate/create hierarchy path (excluding the tag itself at position 0)
            for i in range(1, len(hierarchy)):
                level_name = hierarchy[i]
                if level_name not in current_level:
                    current_level[level_name] = {
                        'subcategories': {},
                        'tags': []
                    }
                current_level = current_level[level_name]['subcategories']
            
            # Add tag at the leaf level
            # Find the parent category (last hierarchy level before tag)
            parent_level = facets[branch_name]['hierarchy_tree']
            for i in range(1, len(hierarchy)):
                level_name = hierarchy[i]
                if i == len(hierarchy) - 1:
                    # This is the leaf category, add tag here
                    parent_level[level_name]['tags'].append({
                        'id': tag_entry['id'],
                        'tag': tag_entry['tag'],
                        'threshold': tag_entry['threshold'],
                        'hierarchy': tag_entry['hierarchy']
                    })
                else:
                    parent_level = parent_level[level_name]['subcategories']
            
            facets[branch_name]['total_tags'] += 1
    
    # Convert to list format
    return [convert_tree_to_list(branch_name, data) 
            for branch_name, data in sorted(facets.items())]


def convert_tree_to_list(branch_name: str, branch_data: Dict) -> Dict:
    """Convert nested tree structure to list format."""
    
    def flatten_tree(tree_dict, path=[]):
        """Recursively flatten tree into categories."""
        categories = []
        
        for name, content in sorted(tree_dict.items()):
            category = {
                'name': name,
                'path': path + [name],
                'tags': content['tags'],
                'count': len(content['tags']),
                'subcategories': flatten_tree(content['subcategories'], path + [name])
            }
            categories.append(category)
        
        return categories
    
    return {
        'branch': branch_name,
        'total_tags': branch_data['total_tags'],
        'categories': flatten_tree(branch_data['hierarchy_tree'])
    }


def build_genres_tree(deep_hierarchy: Dict) -> List[Dict]:
    """
    Build GENRES tree by routing tags based on hierarchy and branch.
    
    Structure: GENRES/{Genre}/{tag}
    """
    genres = defaultdict(list)
    genre_descriptions = {
        "People & Portrait": "People, portraits, and pets",
        "Wildlife": "Wild animals in natural habitats",
        "Landscape & Nature": "Natural scenery, mountains, forests, water bodies",
        "Architecture & Interiors": "Buildings, structures, rooms, and interior spaces",
        "Street & Documentary": "Urban scenes, street life, documentary photography",
        "Travel": "Travel destinations, landmarks, transportation hubs",
        "Sports & Action": "Sports, athletics, and action activities",
        "Food & Drink": "Food, beverages, and culinary subjects",
        "Transportation": "Vehicles, aircraft, watercraft",
        "Product & Commercial": "Commercial products, electronics, tools",
        "Still Life": "Objects, arrangements, everyday items",
        "Events": "Ceremonies, celebrations, social gatherings",
        "Creative & Artistic": "Art creation, musical performance, dance",
        "Lifestyle": "Daily activities, work, leisure",
        "Documentary": "Documentary subjects, work scenes",
        "Conceptual": "Abstract concepts, ideas, symbols",
        "Abstract & Texture": "Visual patterns, textures, colors",
        "Digital Art & Illustration": "Anime, cartoon, illustration styles",
        "Other": "Uncategorized items"
    }
    
    for branch_data in deep_hierarchy['branches']:
        branch_name = branch_data['branch']
        
        for tag_entry in branch_data['tags']:
            genre = classify_genre(
                tag_entry['tag'], 
                tag_entry['hierarchy'], 
                branch_name
            )
            
            if genre:  # Skip tags with no genre (e.g., techniques)
                genres[genre].append({
                    'id': tag_entry['id'],
                    'tag': tag_entry['tag'],
                    'threshold': tag_entry['threshold'],
                    'branch': branch_name,
                    'hierarchy': tag_entry['hierarchy']
                })
    
    # Convert to list format
    return [
        {
            'genre': genre_name,
            'description': genre_descriptions.get(genre_name, ""),
            'count': len(tags),
            'tags': sorted(tags, key=lambda x: x['tag'])
        }
        for genre_name, tags in sorted(genres.items())
    ]


def main():
    """Build dual-tree ontology from deep hierarchy."""
    print("Loading ontology_deep_hierarchy.json...")
    deep_hierarchy = load_deep_hierarchy()
    
    print(f"\nBuilding FACETS tree from {deep_hierarchy['total_tags']} tags...")
    facets = build_facets_tree(deep_hierarchy)
    
    print("Building GENRES tree with routing rules...")
    genres = build_genres_tree(deep_hierarchy)
    
    # Create output structure
    output = {
        'model': deep_hierarchy['model'],
        'source': deep_hierarchy['source'],
        'total_tags': deep_hierarchy['total_tags'],
        'description': 'Dual-tree ontology built from deep hierarchies',
        'facets': facets,
        'genres': genres
    }
    
    # Save to file
    output_file = 'ontology_final.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("DUAL-TREE ONTOLOGY SUMMARY")
    print('='*70)
    print(f"\nTotal tags: {output['total_tags']}")
    
    print(f"\nFACETS tree: {len(facets)} branches")
    for facet in facets:
        print(f"  {facet['branch']}: {facet['total_tags']} tags")
    
    print(f"\nGENRES tree: {len(genres)} genres")
    for genre in genres:
        print(f"  {genre['genre']}: {genre['count']} tags")
    
    # Calculate coverage
    total_genre_tags = sum(g['count'] for g in genres)
    genre_coverage = (total_genre_tags / output['total_tags']) * 100
    
    print(f"\nCoverage:")
    print(f"  FACETS: {output['total_tags']}/{output['total_tags']} (100%)")
    print(f"  GENRES: {total_genre_tags}/{output['total_tags']} ({genre_coverage:.1f}%)")
    
    print(f"\nDual-tree ontology saved to {output_file}")


if __name__ == "__main__":
    main()
