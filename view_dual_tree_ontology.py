#!/usr/bin/env python3
"""
Interactive viewer for the dual-tree ontology.
Browse FACETS (canonical hierarchy) and GENRES (photography-centric view).
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_ontology(path: Path = Path("ontology_dual_tree.json")) -> Dict[str, Any]:
    """Load the dual-tree ontology."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_tree(tree: Dict[str, Any], indent: int = 0, max_depth: int = 10):
    """Recursively print tree structure."""
    if indent > max_depth:
        return
    
    for key, value in sorted(tree.items()):
        if key == "_meta":
            continue
        
        if isinstance(value, dict):
            if "_meta" in value:
                # Leaf node (tag)
                meta = value["_meta"]
                print(f"{'  ' * indent}├─ {key} (id: {meta['id']}, threshold: {meta['threshold']})")
            else:
                # Intermediate node
                print(f"{'  ' * indent}├─ {key}/")
                print_tree(value, indent + 1, max_depth)


def count_items(tree: Dict[str, Any]) -> int:
    """Count items in a tree branch."""
    count = 0
    for key, value in tree.items():
        if isinstance(value, dict):
            if "_meta" in value:
                count += 1
            else:
                count += count_items(value)
    return count


def search_tag(ontology: Dict[str, Any], query: str, tree_name: str = "both") -> List[Dict[str, Any]]:
    """Search for tags containing the query string."""
    results = []
    query_lower = query.lower()
    
    def search_recursive(tree: Dict[str, Any], path: List[str], tree_type: str):
        for key, value in tree.items():
            if key == "_meta":
                continue
            
            current_path = path + [key]
            
            if isinstance(value, dict):
                if "_meta" in value:
                    # Leaf node (tag)
                    if query_lower in key.lower():
                        results.append({
                            "tag": key,
                            "path": " → ".join(current_path),
                            "tree": tree_type,
                            "meta": value["_meta"]
                        })
                else:
                    # Intermediate node
                    search_recursive(value, current_path, tree_type)
    
    if tree_name in ["both", "facets"]:
        for branch_name, branch_tree in ontology["FACETS"].items():
            search_recursive(branch_tree, [branch_name], "FACETS")
    
    if tree_name in ["both", "genres"]:
        for genre_name, genre_tree in ontology["GENRES"].items():
            search_recursive(genre_tree, [genre_name], "GENRES")
    
    return results


def list_top_level(ontology: Dict[str, Any], tree_name: str = "facets"):
    """List top-level branches or genres with counts."""
    if tree_name == "facets":
        print("\n=== FACETS (Canonical Hierarchy) ===\n")
        for branch, tree in sorted(ontology["FACETS"].items()):
            count = count_items(tree)
            print(f"{branch}: {count} tags")
    else:
        print("\n=== GENRES (Photography-Centric View) ===\n")
        for genre, tree in sorted(ontology["GENRES"].items()):
            count = count_items(tree)
            print(f"{genre}: {count} tags")


def browse_tree(ontology: Dict[str, Any], tree_name: str, path: List[str]):
    """Browse a specific path in the tree."""
    if tree_name == "facets":
        tree = ontology["FACETS"]
        print(f"\n=== FACETS/{'/'.join(path)} ===\n")
    else:
        tree = ontology["GENRES"]
        print(f"\n=== GENRES/{'/'.join(path)} ===\n")
    
    # Navigate to the specified path
    current = tree
    for segment in path:
        if segment in current:
            current = current[segment]
        else:
            print(f"Error: Path not found: {'/'.join(path)}")
            return
    
    # Print the subtree
    print_tree(current, max_depth=5)


def main():
    import sys
    
    # Load ontology
    ontology = load_ontology()
    
    print(f"\n{'='*60}")
    print("  Dual-Tree Photo Ontology Viewer")
    print(f"  Model: {ontology['model']}")
    print(f"  Total tags: {ontology['statistics']['facets']['total_tags']}")
    print(f"{'='*60}\n")
    
    if len(sys.argv) == 1:
        # No arguments - show help
        print("Usage:")
        print("  python view_dual_tree_ontology.py list [facets|genres]")
        print("  python view_dual_tree_ontology.py browse facets <branch> [path...]")
        print("  python view_dual_tree_ontology.py browse genres <genre> [path...]")
        print("  python view_dual_tree_ontology.py search <query> [facets|genres|both]")
        print()
        print("Examples:")
        print("  python view_dual_tree_ontology.py list facets")
        print("  python view_dual_tree_ontology.py list genres")
        print("  python view_dual_tree_ontology.py browse facets ACTIVITY_ACTION")
        print("  python view_dual_tree_ontology.py browse genres 'Sports & Action'")
        print("  python view_dual_tree_ontology.py search baseball")
        print("  python view_dual_tree_ontology.py search wedding genres")
        print()
        print("Quick overview:")
        list_top_level(ontology, "facets")
        list_top_level(ontology, "genres")
        
    elif sys.argv[1] == "list":
        tree_name = sys.argv[2] if len(sys.argv) > 2 else "facets"
        list_top_level(ontology, tree_name)
    
    elif sys.argv[1] == "browse":
        if len(sys.argv) < 4:
            print("Error: browse requires tree type and path")
            print("Usage: python view_dual_tree_ontology.py browse [facets|genres] <path> [...]")
            return
        
        tree_name = sys.argv[2]
        path = sys.argv[3:]
        browse_tree(ontology, tree_name, path)
    
    elif sys.argv[1] == "search":
        if len(sys.argv) < 3:
            print("Error: search requires a query")
            print("Usage: python view_dual_tree_ontology.py search <query> [facets|genres|both]")
            return
        
        query = sys.argv[2]
        tree_name = sys.argv[3] if len(sys.argv) > 3 else "both"
        
        results = search_tag(ontology, query, tree_name)
        
        print(f"\nSearch results for '{query}' ({len(results)} matches):\n")
        for result in results:
            print(f"[{result['tree']}] {result['path']}")
            print(f"  ID: {result['meta']['id']}, Threshold: {result['meta']['threshold']}")
            if 'source_branch' in result['meta']:
                print(f"  Source: {result['meta']['source_branch']}")
            print()
    
    else:
        print(f"Error: Unknown command '{sys.argv[1]}'")
        print("Run without arguments for help")


if __name__ == "__main__":
    main()
