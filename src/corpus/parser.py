# inb4: just_for_lulz

import mwparserfromhell
from typing import Optional


class WikitextParser:
    """
    Parses MediaWiki wikitext into structured data.
    
    Extracts:
    - clean_text: Plain text with markup removed
    - links: Internal wiki links
    - categories: Article categories
    - templates: Template names and parameters
    """
    
    def parse(self, raw_wikitext: str) -> dict:
        """
        Parses raw wikitext into structured format.
        
        Args:
            raw_wikitext: Raw MediaWiki markup
        
        Returns:
            Dictionary with keys: clean_text, links, categories, templates
        """
        if not raw_wikitext:
            return {
                "clean_text": "",
                "links": [],
                "categories": [],
                "templates": []
            }
        
        try:
            wikicode = mwparserfromhell.parse(raw_wikitext)
        except Exception:
            # Fallback: return raw text if parsing fails
            return {
                "clean_text": raw_wikitext.strip(),
                "links": [],
                "categories": [],
                "templates": []
            }
        
        # Extract links
        links = []
        for link in wikicode.filter_wikilinks():
            target = str(link.title).strip()
            anchor = str(link.text).strip() if link.text else target
            links.append({
                "target": target,
                "anchor": anchor
            })
        
        # Extract categories
        categories = []
        for link in wikicode.filter_wikilinks():
            target = str(link.title).strip()
            if target.startswith("Категория:") or target.startswith("Category:"):
                category_name = target.split(":", 1)[1]
                categories.append(category_name)
        
        # Extract templates (all, including nested)
        templates = []
        for template in wikicode.filter_templates():
            template_name = str(template.name).strip()
            params = {}
            for param in template.params:
                param_name = str(param.name).strip()
                param_value = str(param.value).strip()
                params[param_name] = param_value
            templates.append({
                "name": template_name,
                "params": params
            })
        
        # Remove categories and templates from text
        for link in wikicode.filter_wikilinks():
            target = str(link.title).strip()
            if target.startswith("Категория:") or target.startswith("Category:"):
                wikicode.remove(link)
        
        for template in wikicode.filter_templates(recursive=False):
            wikicode.remove(template)
        
        # Strip remaining markup
        clean_text = wikicode.strip_code()
        
        return {
            "clean_text": clean_text.strip(),
            "links": links,
            "categories": categories,
            "templates": templates
        }