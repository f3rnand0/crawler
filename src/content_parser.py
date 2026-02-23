#!/usr/bin/env python3
"""
Grammar Content Parser

Intelligently parses HTML content from grammar lessons to extract structured
sections: rules, examples, tables, exceptions, glossary terms.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup, Tag


class GrammarContentParser:
    """Parse HTML grammar content into structured sections."""
    
    def __init__(self):
        self.soup = None
    
    def parse_html(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML content into structured sections.
        
        Args:
            html: Raw HTML content from grammar lesson
            
        Returns:
            Dictionary with structured content sections
        """
        if not html or not html.strip():
            return self._empty_structure()
        
        self.soup = BeautifulSoup(html, 'html.parser')
        
        # Remove images and figure tags (as requested)
        for img in self.soup.find_all('img'):
            img.decompose()
        for figure in self.soup.find_all('figure'):
            figure.decompose()
        
        return {
            "overview": self._extract_overview(),
            "rules": self._extract_rules(),
            "examples": self._extract_examples(),
            "tables": self._extract_tables(),
            "exceptions": self._extract_exceptions(),
            "glossary": self._extract_glossary(),
            "raw_html": html  # Keep original for reference
        }
    
    def _empty_structure(self) -> Dict[str, Any]:
        """Return empty structure dictionary."""
        return {
            "overview": "",
            "rules": [],
            "examples": [],
            "tables": [],
            "exceptions": [],
            "glossary": [],
            "raw_html": ""
        }
    
    def _extract_overview(self) -> str:
        """
        Extract overview/introduction from content.
        Usually the first paragraph or first few sentences.
        """
        if not self.soup:
            return ""
        
        paragraphs = self.soup.find_all('p')
        if not paragraphs:
            return ""
        
        # Get first non-empty paragraph as overview
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 20:  # Reasonable length for overview
                return text
        
        return ""
    
    def _extract_rules(self) -> List[str]:
        """
        Extract grammar rules from content.
        Rules are typically in paragraphs that explain grammatical concepts.
        """
        rules = []
        if not self.soup:
            return rules
        
        paragraphs = self.soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text().strip()
            if not text:
                continue
            
            # Heuristic: Rules often contain explanations without being examples
            # Avoid paragraphs that are just examples or glossary
            if self._is_likely_rule_paragraph(p):
                # Clean up the text
                cleaned = self._clean_text(text)
                if cleaned:
                    rules.append(cleaned)
        
        return rules
    
    def _extract_examples(self) -> List[Dict[str, str]]:
        """
        Extract examples from content.
        Examples are typically in <em> tags (italicized German text).
        """
        examples = []
        if not self.soup:
            return examples
        
        # Find all <em> tags that likely contain German examples
        em_tags = self.soup.find_all('em')
        
        for em in em_tags:
            german_text = em.get_text().strip()
            if not german_text or len(german_text) < 3:
                continue
            
            # Try to find context/translation
            context = self._find_example_context(em)
            
            example = {
                "german": german_text,
                "context": context,
                "translation": self._infer_translation(german_text, context)
            }
            examples.append(example)
        
        return examples
    
    def _extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extract tables from content and convert to markdown.
        """
        tables = []
        if not self.soup:
            return tables
        
        for table in self.soup.find_all('table'):
            table_data = self._parse_table_to_markdown(table)
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def _extract_exceptions(self) -> List[str]:
        """
        Extract exceptions and special cases from content.
        Often signaled by words like "excepto", "sin embargo", "pero", etc.
        """
        exceptions = []
        if not self.soup:
            return exceptions
        
        # Look for paragraphs containing exception indicators
        exception_indicators = [
            "excepto", "sin embargo", "pero", "aunque", 
            "no obstante", "salvo", "excepción", "excepciones"
        ]
        
        for p in self.soup.find_all('p'):
            text = p.get_text().lower().strip()
            if any(indicator in text for indicator in exception_indicators):
                cleaned = self._clean_text(p.get_text().strip())
                if cleaned:
                    exceptions.append(cleaned)
        
        return exceptions
    
    def _extract_glossary(self) -> List[Dict[str, str]]:
        """
        Extract glossary terms ("Términos gramaticales").
        """
        glossary = []
        if not self.soup:
            return glossary
        
        # Look for "Términos gramaticales" section
        # Often in a table or special section
        for elem in self.soup.find_all(['table', 'p', 'div']):
            text = elem.get_text().lower()
            if 'términos gramaticales' in text:
                # Extract terms from this element
                terms = self._extract_terms_from_glossary(elem)
                glossary.extend(terms)
                break
        
        return glossary
    
    def _is_likely_rule_paragraph(self, paragraph: Tag) -> bool:
        """
        Determine if a paragraph is likely a grammar rule.
        """
        text = paragraph.get_text().lower().strip()
        
        # Rules typically don't start with example markers
        if text.startswith(('_', '**', '«', '"', "'")):
            return False
        
        # Rules often contain grammatical explanation words
        rule_indicators = [
            'se usa', 'se emplea', 'se puede', 'debe', 'deben',
            'es necesario', 'hay que', 'tiene que', 'tienen que',
            'gramatical', 'sintaxis', 'conjugación', 'declinación'
        ]
        
        if any(indicator in text for indicator in rule_indicators):
            return True
        
        # Check if it's likely an example (contains italicized text)
        if paragraph.find('em'):
            return False
        
        # Reasonable length for a rule
        return 30 <= len(text) <= 500
    
    def _find_example_context(self, em_tag: Tag) -> str:
        """
        Find context for an example (surrounding text).
        """
        # Look for parent paragraph
        parent_p = em_tag.find_parent('p')
        if parent_p:
            full_text = parent_p.get_text().strip()
            german_text = em_tag.get_text().strip()
            
            # Remove the German text to get context
            context = full_text.replace(german_text, '').strip()
            if context:
                return self._clean_text(context)
        
        return ""
    
    def _infer_translation(self, german_text: str, context: str) -> str:
        """
        Infer translation from context.
        In a real implementation, this might use a translation API.
        For now, return empty string.
        """
        return ""  # Placeholder - could be enhanced later
    
    def _parse_table_to_markdown(self, table: Tag) -> Dict[str, Any]:
        """
        Convert HTML table to markdown format.
        """
        try:
            rows = table.find_all('tr')
            if not rows:
                return {"headers": [], "rows": [], "markdown": "", "row_count": 0, "col_count": 0}
            
            # Extract headers
            headers = []
            header_cells = rows[0].find_all(['th', 'td'])
            for cell in header_cells:
                headers.append(cell.get_text().strip())
            
            # Extract data rows
            data = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if cells:
                    row_data = [cell.get_text().strip() for cell in cells]
                    data.append(row_data)
            
            # Build markdown table
            markdown_lines = []
            if headers:
                # Header row
                markdown_lines.append('| ' + ' | '.join(headers) + ' |')
                # Separator row
                markdown_lines.append('|' + '---|' * len(headers))
            
            for row in data:
                markdown_lines.append('| ' + ' | '.join(row) + ' |')
            
            markdown_table = '\n'.join(markdown_lines)
            
            return {
                "headers": headers,
                "rows": data,
                "markdown": markdown_table,
                "row_count": len(data),
                "col_count": len(headers) if headers else (len(data[0]) if data else 0)
            }
            
        except Exception as e:
            # Fallback: return table as plain text
            return {
                "headers": [],
                "rows": [],
                "markdown": table.get_text().strip(),
                "error": str(e)
            }
    
    def _extract_terms_from_glossary(self, element: Tag) -> List[Dict[str, str]]:
        """
        Extract terms and definitions from glossary section.
        """
        terms = []
        
        # Simple heuristic: look for bold terms followed by definitions
        for bold in element.find_all(['strong', 'b']):
            term = bold.get_text().strip()
            if not term:
                continue
            
            # Get definition (text after bold)
            definition = ""
            next_sibling = bold.next_sibling
            while next_sibling:
                if isinstance(next_sibling, str):
                    definition += next_sibling.strip()
                else:
                    # Check if it's a Tag with a name attribute
                    try:
                        if next_sibling.name not in ['strong', 'b', 'em']:
                            definition += next_sibling.get_text().strip()
                        else:
                            break
                    except AttributeError:
                        # Not a Tag, just add its text
                        definition += str(next_sibling).strip()
                next_sibling = next_sibling.next_sibling
            
            if term and definition:
                terms.append({
                    "term": term,
                    "definition": definition.strip(': ,.;')
                })
        
        return terms
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing."""
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing punctuation
        text = text.strip(' :;.,-')
        return text
    
    def html_to_structured_markdown(self, html: str) -> str:
        """
        Convert HTML directly to structured markdown with sections.
        This is a convenience method that uses the parser.
        """
        structured = self.parse_html(html)
        return self._format_as_markdown(structured)
    
    def _format_as_markdown(self, structured: Dict[str, Any]) -> str:
        """
        Format structured content as markdown with sections.
        """
        lines = []
        
        # Overview
        if structured["overview"]:
            lines.append("## 📖 Overview")
            lines.append(structured["overview"])
            lines.append("")
        
        # Rules
        if structured["rules"]:
            lines.append("## 📝 Rules & Explanation")
            for rule in structured["rules"]:
                lines.append(f"- {rule}")
            lines.append("")
        
        # Examples
        if structured["examples"]:
            lines.append("## 🎯 Examples")
            for example in structured["examples"]:
                lines.append(f"**German**: {example['german']}")
                if example['translation']:
                    lines.append(f"**Translation**: {example['translation']}")
                if example['context']:
                    lines.append(f"**Context**: {example['context']}")
                lines.append("")
            lines.append("")
        
        # Tables
        if structured["tables"]:
            lines.append("## 📊 Tables")
            for table in structured["tables"]:
                lines.append(table.get("markdown", ""))
                lines.append("")
        
        # Exceptions
        if structured["exceptions"]:
            lines.append("## ⚠️ Exceptions & Notes")
            for exception in structured["exceptions"]:
                lines.append(f"- {exception}")
            lines.append("")
        
        # Glossary
        if structured["glossary"]:
            lines.append("## 📚 Glossary")
            for term in structured["glossary"]:
                lines.append(f"**{term['term']}**: {term['definition']}")
            lines.append("")
        
        return "\n".join(lines)


# Convenience function for module-level usage
def parse_html_content(html: str) -> Dict[str, Any]:
    """Parse HTML content into structured sections."""
    parser = GrammarContentParser()
    return parser.parse_html(html)


def html_to_structured_markdown(html: str) -> str:
    """Convert HTML directly to structured markdown."""
    parser = GrammarContentParser()
    return parser.html_to_structured_markdown(html)