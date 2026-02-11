#!/usr/bin/env python3
"""
Build dual-tree ontology from ontology_deep_hierarchy.json:
1. FACETS tree: Canonical hierarchical structure (facet-based truth)
2. GENRES tree: Photography-centric routed view (user-friendly browsing)
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any


def build_facets_tree(ontology_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build FACETS tree directly from hierarchy paths.
    Structure: FACETS/{Branch}/{Hierarchy...}/{tag}
    
    Each tag's hierarchy is materialized as a path in the tree.
    Example: "award ceremony" -> ["award ceremony", "Ceremony", "Social Event", "Activity"]
    becomes: FACETS/ACTIVITY_ACTION/Activity/Social Event/Ceremony/award ceremony
    """
    facets = {}
    
    for branch_data in ontology_data["branches"]:
        branch_name = branch_data["branch"]
        branch_tree = {}
        
        for tag_data in branch_data["tags"]:
            hierarchy = tag_data["hierarchy"]  # [leaf, ..., root]
            
            # Reverse hierarchy to go from root to leaf
            path = list(reversed(hierarchy))
            
            # Build nested structure
            current = branch_tree
            for i, level in enumerate(path):
                if i == len(path) - 1:
                    # Leaf node (actual tag)
                    if level not in current:
                        current[level] = {
                            "_meta": {
                                "id": tag_data["id"],
                                "threshold": tag_data["threshold"],
                                "depth": tag_data["depth"]
                            }
                        }
                else:
                    # Intermediate node
                    if level not in current:
                        current[level] = {}
                    current = current[level]
        
        facets[branch_name] = branch_tree
    
    return facets


def build_genres_tree(ontology_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build GENRES tree with photography-centric routing.
    Structure: GENRES/{Genre}/{optional_subgenre}/{tag}
    
    Routing rules:
    - ATTRIBUTE_STYLE -> GENRES/Digital Art & Illustration/...
    - TECHNICAL_PHOTO -> GENRES/Technique/...
    - ... -> Sport -> Activity -> GENRES/Sports & Action/...
    - ... -> Social Event -> Activity -> GENRES/Events/...
    - ... -> Wildlife -> ... -> GENRES/Wildlife & Nature/...
    - ... -> Architecture -> ... -> GENRES/Architecture & Built Environment/...
    - ... -> Food -> ... -> GENRES/Food & Culinary/...
    - SUBJECT_PEOPLE -> GENRES/People & Portrait/...
    """
    genres = defaultdict(lambda: defaultdict(dict))
    
    for branch_data in ontology_data["branches"]:
        branch_name = branch_data["branch"]
        
        for tag_data in branch_data["tags"]:
            tag = tag_data["tag"]
            hierarchy = tag_data["hierarchy"]  # [leaf, ..., root]
            
            genre = None
            subgenre = None
            
            # Routing logic
            if branch_name == "ATTRIBUTE_STYLE":
                genre = "Digital Art & Illustration"
                # Use second-to-last hierarchy level as subgenre if depth > 1
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "TECHNICAL_PHOTO":
                genre = "Technique"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif "Sport" in hierarchy:
                genre = "Sports & Action"
                # Find sport type
                sport_idx = hierarchy.index("Sport")
                if sport_idx > 0:
                    subgenre = hierarchy[sport_idx - 1]
            
            elif "Social Event" in hierarchy:
                genre = "Events"
                # Find event type (level below Social Event)
                event_idx = hierarchy.index("Social Event")
                if event_idx > 0:
                    subgenre = hierarchy[event_idx - 1]
            
            elif "Wildlife" in hierarchy or "Animal" in hierarchy:
                genre = "Wildlife & Nature"
                # Use first level as subgenre
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif "Architecture" in hierarchy or "Building" in hierarchy:
                genre = "Architecture & Built Environment"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "SUBJECT_FOOD":
                genre = "Food & Culinary"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "SUBJECT_PEOPLE":
                genre = "People & Portrait"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif "Landscape" in hierarchy or "Natural Landscape" in hierarchy:
                genre = "Landscape & Scenic"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "SCENE_LOCATION":
                genre = "Places & Travel"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "SUBJECT_OBJECT":
                genre = "Objects & Still Life"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "CONCEPT_ABSTRACT":
                genre = "Concept & Abstract"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            elif branch_name == "ACTIVITY_ACTION":
                # Default to Activities for uncategorized actions
                genre = "Activities & Lifestyle"
                if len(hierarchy) > 1:
                    subgenre = hierarchy[-2]
            
            # Add tag to genre tree
            if genre:
                tag_meta = {
                    "id": tag_data["id"],
                    "threshold": tag_data["threshold"],
                    "depth": tag_data["depth"],
                    "source_branch": branch_name,
                    "hierarchy": hierarchy
                }
                
                if subgenre:
                    if subgenre not in genres[genre]:
                        genres[genre][subgenre] = {}
                    genres[genre][subgenre][tag] = {"_meta": tag_meta}
                else:
                    genres[genre][tag] = {"_meta": tag_meta}
    
    # Convert defaultdict to regular dict
    return {genre: dict(subgenres) for genre, subgenres in genres.items()}


def generate_stats(facets: Dict[str, Any], genres: Dict[str, Any]) -> Dict[str, Any]:
    """Generate statistics about the dual tree structure."""
    
    def count_tags(tree: Dict[str, Any]) -> int:
        """Recursively count leaf tags in tree."""
        count = 0
        for key, value in tree.items():
            if isinstance(value, dict):
                if "_meta" in value:
                    count += 1
                else:
                    count += count_tags(value)
        return count
    
    facets_stats = {
        "total_branches": len(facets),
        "tags_per_branch": {
            branch: count_tags(subtree) 
            for branch, subtree in facets.items()
        },
        "total_tags": sum(count_tags(subtree) for subtree in facets.values())
    }
    
    genres_stats = {
        "total_genres": len(genres),
        "tags_per_genre": {
            genre: count_tags(subtree)
            for genre, subtree in genres.items()
        },
        "total_tags": sum(count_tags(subtree) for subtree in genres.values())
    }
    
    return {
        "facets": facets_stats,
        "genres": genres_stats
    }


def main():
    # Load deep hierarchy ontology
    input_path = Path("ontology_deep_hierarchy.json")
    
    with open(input_path, "r", encoding="utf-8") as f:
        ontology_data = json.load(f)
    
    print(f"Loaded ontology with {ontology_data['total_tags']} tags from {len(ontology_data['branches'])} branches")
    
    # Build FACETS tree
    print("\nBuilding FACETS tree (canonical hierarchy)...")
    facets = build_facets_tree(ontology_data)
    
    # Build GENRES tree
    print("Building GENRES tree (photography-centric routing)...")
    genres = build_genres_tree(ontology_data)
    
    # Generate statistics
    stats = generate_stats(facets, genres)
    
    # Create dual-tree structure
    dual_tree = {
        "model": ontology_data["model"],
        "source": ontology_data["source"],
        "description": "Dual-tree ontology: FACETS (canonical hierarchy) and GENRES (photography-centric view)",
        "format_version": "1.0",
        "statistics": stats,
        "FACETS": facets,
        "GENRES": genres
    }
    
    # Write output
    output_path = Path("ontology_dual_tree.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dual_tree, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Dual-tree ontology written to {output_path}")
    print("\nStatistics:")
    print(f"  FACETS: {stats['facets']['total_tags']} tags across {stats['facets']['total_branches']} branches")
    print(f"  GENRES: {stats['genres']['total_tags']} tags across {stats['genres']['total_genres']} genres")
    print("\nFACETS branches:")
    for branch, count in stats['facets']['tags_per_branch'].items():
        print(f"  {branch}: {count} tags")
    print("\nGENRES:")
    for genre, count in sorted(stats['genres']['tags_per_genre'].items(), key=lambda x: -x[1]):
        print(f"  {genre}: {count} tags")


if __name__ == "__main__":
    main()
