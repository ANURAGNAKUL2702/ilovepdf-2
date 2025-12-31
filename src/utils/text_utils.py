"""
Spell checking utilities for PDF editing system.

This module provides spell checking and correction functionality.
"""
from textblob import TextBlob
from typing import List, Dict, Tuple, Optional
import re


class SpellChecker:
    """Spell checker and corrector for text."""
    
    def __init__(self, custom_dictionary: Optional[List[str]] = None):
        """
        Initialize spell checker.
        
        Args:
            custom_dictionary: Optional list of custom words to add to dictionary
        """
        self.custom_dictionary = set(custom_dictionary or [])
        
    def check_word(self, word: str) -> bool:
        """
        Check if a word is spelled correctly.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is correct, False otherwise
        """
        # Skip custom dictionary words
        if word.lower() in self.custom_dictionary:
            return True
            
        # Skip numbers and special characters
        if not word.isalpha():
            return True
            
        blob = TextBlob(word)
        corrected = str(blob.correct())
        return word.lower() == corrected.lower()
    
    def correct_word(self, word: str) -> str:
        """
        Correct a single word.
        
        Args:
            word: Word to correct
            
        Returns:
            Corrected word
        """
        # Don't correct custom dictionary words
        if word.lower() in self.custom_dictionary:
            return word
            
        # Don't correct numbers and special characters
        if not word.isalpha():
            return word
            
        blob = TextBlob(word)
        corrected = str(blob.correct())
        
        # Preserve original case if possible
        if word.isupper():
            return corrected.upper()
        elif len(word) > 0 and word[0].isupper():
            return corrected.capitalize()
        else:
            return corrected
    
    def check_text(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Check text for spelling mistakes.
        
        Args:
            text: Text to check
            
        Returns:
            List of tuples (misspelled_word, start_position, end_position)
        """
        mistakes = []
        
        # Split text into words while preserving positions
        words = re.finditer(r'\b\w+\b', text)
        
        for match in words:
            word = match.group()
            if not self.check_word(word):
                mistakes.append((word, match.start(), match.end()))
                
        return mistakes
    
    def correct_text(self, text: str) -> str:
        """
        Correct spelling mistakes in text.
        
        Args:
            text: Text to correct
            
        Returns:
            Corrected text
        """
        def replace_word(match):
            word = match.group()
            return self.correct_word(word)
            
        corrected = re.sub(r'\b\w+\b', replace_word, text)
        return corrected
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Word to get suggestions for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested corrections
        """
        if not word.isalpha():
            return []
            
        # Use correct() to get the main suggestion, and return it in a list
        blob = TextBlob(word)
        corrected = str(blob.correct())
        
        # Return the correction as a suggestion if different from original
        if corrected.lower() != word.lower():
            return [corrected]
        return []
    
    def add_to_dictionary(self, word: str):
        """
        Add a word to the custom dictionary.
        
        Args:
            word: Word to add
        """
        self.custom_dictionary.add(word.lower())
    
    def remove_from_dictionary(self, word: str):
        """
        Remove a word from the custom dictionary.
        
        Args:
            word: Word to remove
        """
        self.custom_dictionary.discard(word.lower())


class TextModifier:
    """Utilities for text modification operations."""
    
    @staticmethod
    def insert_text(original: str, text_to_insert: str, position: int) -> str:
        """
        Insert text at a specific position.
        
        Args:
            original: Original text
            text_to_insert: Text to insert
            position: Position to insert at
            
        Returns:
            Modified text
        """
        if position < 0 or position > len(original):
            raise ValueError(f"Position {position} out of range for text of length {len(original)}")
            
        return original[:position] + text_to_insert + original[position:]
    
    @staticmethod
    def replace_text(original: str, old_text: str, new_text: str, 
                     count: int = -1) -> str:
        """
        Replace occurrences of text.
        
        Args:
            original: Original text
            old_text: Text to replace
            new_text: Replacement text
            count: Number of replacements (-1 for all)
            
        Returns:
            Modified text
        """
        if count == -1:
            return original.replace(old_text, new_text)
        else:
            return original.replace(old_text, new_text, count)
    
    @staticmethod
    def replace_at_position(original: str, new_text: str, 
                           start: int, end: int) -> str:
        """
        Replace text at a specific position range.
        
        Args:
            original: Original text
            new_text: Replacement text
            start: Start position
            end: End position
            
        Returns:
            Modified text
        """
        if start < 0 or end > len(original) or start > end:
            raise ValueError(f"Invalid position range [{start}, {end}] for text of length {len(original)}")
            
        return original[:start] + new_text + original[end:]
    
    @staticmethod
    def delete_text(original: str, start: int, end: int) -> str:
        """
        Delete text at a specific position range.
        
        Args:
            original: Original text
            start: Start position
            end: End position
            
        Returns:
            Modified text
        """
        if start < 0 or end > len(original) or start > end:
            raise ValueError(f"Invalid position range [{start}, {end}] for text of length {len(original)}")
            
        return original[:start] + original[end:]


def correct_spelling_in_text(text: str, custom_dictionary: Optional[List[str]] = None) -> str:
    """
    Convenience function to correct spelling in text.
    
    Args:
        text: Text to correct
        custom_dictionary: Optional custom dictionary
        
    Returns:
        Corrected text
    """
    checker = SpellChecker(custom_dictionary)
    return checker.correct_text(text)
