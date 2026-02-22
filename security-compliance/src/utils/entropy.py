"""
Entropy Calculator for Secret Detection

Calculates Shannon entropy to identify high-entropy strings that may be secrets.
"""

import math
import string
from typing import Dict


class EntropyCalculator:
    """
    Shannon entropy calculator.
    
    Entropy measures the randomness of a string. High-entropy strings
    (like API keys, tokens) have more randomness than regular text.
    """
    
    @classmethod
    def calculate(cls, data: str) -> float:
        """
        Calculate Shannon entropy of a string.
        
        Args:
            data: Input string
            
        Returns:
            Entropy value (0-8 for typical character sets)
        """
        if not data:
            return 0.0
        
        if len(data) == 1:
            return 0.0
        
        # Count character frequencies
        freq: Dict[str, int] = {}
        for char in data:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        
        for count in freq.values():
            if count > 0:
                probability = count / length
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @classmethod
    def is_high_entropy(
        cls,
        data: str,
        threshold: float = 4.5,
        min_length: int = 20
    ) -> bool:
        """
        Check if a string has high entropy (potential secret).
        
        Args:
            data: Input string
            threshold: Entropy threshold (default 4.5)
            min_length: Minimum string length to consider
            
        Returns:
            True if high entropy, False otherwise
        """
        if len(data) < min_length:
            return False
        
        entropy = cls.calculate(data)
        return entropy >= threshold
    
    @classmethod
    def get_entropy_rating(cls, entropy: float) -> str:
        """
        Get human-readable entropy rating.
        
        Args:
            entropy: Entropy value
            
        Returns:
            Rating string
        """
        if entropy < 2.0:
            return "very_low"
        elif entropy < 3.5:
            return "low"
        elif entropy < 4.5:
            return "medium"
        elif entropy < 5.5:
            return "high"
        else:
            return "very_high"


def calculate_entropy_for_secrets(data: str) -> float:
    """
    Calculate entropy optimized for secret detection.
    
    This is a convenience function that uses default parameters
    suitable for detecting API keys and tokens.
    
    Args:
        data: Input string
        
    Returns:
        Entropy value
    """
    return EntropyCalculator.calculate(data)
