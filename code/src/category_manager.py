import json
import os
from typing import Dict, List, Optional

class CategoryManager:
    def __init__(self, json_file: str = 'categories.json'):
        self.json_file = json_file
        self.categories = self._load_categories()

    def _load_categories(self) -> Dict:
        """Load categories from JSON file or create new if file doesn't exist."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"categories": {}}
        return {"categories": {}}

    def _save_categories(self):
        """Save categories to JSON file."""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, indent=4, ensure_ascii=False)

    def add_category(self, category_name: str) -> bool:
        """Add a new category."""
        if category_name in self.categories["categories"]:
            return False
        
        self.categories["categories"][category_name] = {
            "subcategories": {}
        }
        self._save_categories()
        return True

    def add_subcategory(self, category_name: str, subcategory_name: str) -> bool:
        """Add a new subcategory to an existing category."""
        if category_name not in self.categories["categories"]:
            return False
        
        if subcategory_name in self.categories["categories"][category_name]["subcategories"]:
            return False
        
        self.categories["categories"][category_name]["subcategories"][subcategory_name] = {}
        self._save_categories()
        return True

    def delete_category(self, category_name: str) -> bool:
        """Delete a category and all its subcategories."""
        if category_name not in self.categories["categories"]:
            return False
        
        del self.categories["categories"][category_name]
        self._save_categories()
        return True

    def delete_subcategory(self, category_name: str, subcategory_name: str) -> bool:
        """Delete a subcategory from a category."""
        if category_name not in self.categories["categories"]:
            return False
        
        if subcategory_name not in self.categories["categories"][category_name]["subcategories"]:
            return False
        
        del self.categories["categories"][category_name]["subcategories"][subcategory_name]
        self._save_categories()
        return True

    def get_categories(self) -> Dict:
        """Get all categories and their subcategories."""
        return self.categories["categories"]

    def get_category(self, category_name: str) -> Optional[Dict]:
        """Get a specific category and its subcategories."""
        return self.categories["categories"].get(category_name)

    def get_subcategories(self, category_name: str) -> Optional[Dict]:
        """Get all subcategories of a specific category."""
        if category_name not in self.categories["categories"]:
            return None
        return self.categories["categories"][category_name]["subcategories"] 