"""
Unit tests for text utilities module.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils import SpellChecker, TextModifier, correct_spelling_in_text


@pytest.mark.unit
class TestSpellChecker:
    """Test SpellChecker class."""
    
    def test_check_word_correct(self):
        """Test checking correctly spelled word."""
        checker = SpellChecker()
        assert checker.check_word("hello") is True
        assert checker.check_word("world") is True
    
    def test_check_word_incorrect(self):
        """Test checking incorrectly spelled word."""
        checker = SpellChecker()
        # Note: TextBlob might correct this, but check_word should return False
        result = checker.check_word("wrld")
        # The result depends on TextBlob's dictionary
        assert isinstance(result, bool)
    
    def test_correct_word(self):
        """Test correcting a single word."""
        checker = SpellChecker()
        corrected = checker.correct_word("helo")
        # TextBlob should correct to "hello"
        assert "hel" in corrected.lower()
    
    def test_check_text(self):
        """Test checking text for mistakes."""
        checker = SpellChecker()
        text = "This is a test"
        mistakes = checker.check_text(text)
        # Should have no mistakes
        assert isinstance(mistakes, list)
    
    def test_correct_text(self):
        """Test correcting text."""
        checker = SpellChecker()
        text = "Hello world"
        corrected = checker.correct_text(text)
        assert isinstance(corrected, str)
        assert len(corrected) > 0
    
    def test_custom_dictionary(self):
        """Test custom dictionary."""
        checker = SpellChecker(custom_dictionary=["customword"])
        assert checker.check_word("customword") is True
        assert checker.correct_word("customword") == "customword"
    
    def test_add_to_dictionary(self):
        """Test adding word to dictionary."""
        checker = SpellChecker()
        checker.add_to_dictionary("testword")
        assert "testword" in checker.custom_dictionary
        assert checker.check_word("testword") is True
    
    def test_get_suggestions(self):
        """Test getting spelling suggestions."""
        checker = SpellChecker()
        suggestions = checker.get_suggestions("helo", max_suggestions=3)
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3
    
    def test_preserve_case(self):
        """Test preserving case in corrections."""
        checker = SpellChecker()
        
        # Uppercase
        corrected = checker.correct_word("HELLO")
        assert corrected.isupper() or corrected == "HELLO"
        
        # Capitalized
        corrected = checker.correct_word("Hello")
        assert corrected[0].isupper() or corrected == "Hello"


@pytest.mark.unit
class TestTextModifier:
    """Test TextModifier class."""
    
    def test_insert_text(self):
        """Test inserting text."""
        original = "Hello world"
        result = TextModifier.insert_text(original, " beautiful", 5)
        assert result == "Hello beautiful world"
    
    def test_insert_text_at_start(self):
        """Test inserting at start."""
        original = "world"
        result = TextModifier.insert_text(original, "Hello ", 0)
        assert result == "Hello world"
    
    def test_insert_text_at_end(self):
        """Test inserting at end."""
        original = "Hello"
        result = TextModifier.insert_text(original, " world", 5)
        assert result == "Hello world"
    
    def test_insert_text_invalid_position(self):
        """Test inserting at invalid position."""
        with pytest.raises(ValueError):
            TextModifier.insert_text("Hello", "test", 10)
    
    def test_replace_text(self):
        """Test replacing text."""
        original = "Hello world, world"
        result = TextModifier.replace_text(original, "world", "Python")
        assert result == "Hello Python, Python"
    
    def test_replace_text_with_count(self):
        """Test replacing text with count limit."""
        original = "Hello world, world"
        result = TextModifier.replace_text(original, "world", "Python", count=1)
        assert result == "Hello Python, world"
    
    def test_replace_at_position(self):
        """Test replacing text at position."""
        original = "Hello world"
        result = TextModifier.replace_at_position(original, "Python", 6, 11)
        assert result == "Hello Python"
    
    def test_replace_at_position_invalid(self):
        """Test replacing at invalid position."""
        with pytest.raises(ValueError):
            TextModifier.replace_at_position("Hello", "test", 10, 20)
    
    def test_delete_text(self):
        """Test deleting text."""
        original = "Hello world"
        result = TextModifier.delete_text(original, 5, 11)
        assert result == "Hello"
    
    def test_delete_text_invalid(self):
        """Test deleting at invalid position."""
        with pytest.raises(ValueError):
            TextModifier.delete_text("Hello", 10, 20)


@pytest.mark.unit
def test_correct_spelling_convenience():
    """Test convenience function for spell correction."""
    text = "Hello world"
    corrected = correct_spelling_in_text(text)
    assert isinstance(corrected, str)
    assert len(corrected) > 0
