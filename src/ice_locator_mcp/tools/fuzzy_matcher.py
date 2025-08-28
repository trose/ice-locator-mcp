"""
Advanced fuzzy matching engine for name similarity detection.

This module provides sophisticated fuzzy matching capabilities including
phonetic matching, edit distance calculations, and cultural name variations.
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import structlog


@dataclass
class MatchResult:
    """Result of a fuzzy match operation."""
    original_name: str
    matched_name: str
    similarity_score: float
    match_type: str  # exact, phonetic, edit_distance, cultural
    confidence: float
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence match."""
        return self.confidence >= 0.8


class PhoneticMatcher:
    """Phonetic matching algorithms for name similarity."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
    def soundex(self, name: str) -> str:
        """Generate Soundex code for a name."""
        name = self._normalize_name(name)
        if not name:
            return "0000"
        
        # Keep first letter, convert to uppercase
        soundex = name[0].upper()
        
        # Define Soundex mapping
        mapping = {
            'BFPV': '1',
            'CGJKQSXZ': '2', 
            'DT': '3',
            'L': '4',
            'MN': '5',
            'R': '6'
        }
        
        # Process remaining characters
        for char in name[1:]:
            char = char.upper()
            for group, code in mapping.items():
                if char in group:
                    if soundex[-1] != code:  # Avoid consecutive duplicates
                        soundex += code
                    break
        
        # Pad or truncate to 4 characters
        soundex = soundex.ljust(4, '0')[:4]
        return soundex
    
    def metaphone(self, name: str) -> str:
        """Generate Metaphone code for a name (simplified version)."""
        name = self._normalize_name(name).upper()
        if not name:
            return ""
        
        # Simplified Metaphone rules
        metaphone = ""
        i = 0
        
        while i < len(name):
            char = name[i]
            
            # Vowels at beginning
            if i == 0 and char in 'AEIOU':
                metaphone += char
            
            # Consonant mappings
            elif char == 'B':
                metaphone += 'B'
            elif char == 'C':
                if i + 1 < len(name) and name[i + 1] in 'EIY':
                    metaphone += 'S'
                else:
                    metaphone += 'K'
            elif char == 'D':
                metaphone += 'T'
            elif char == 'F':
                metaphone += 'F'
            elif char == 'G':
                if i + 1 < len(name) and name[i + 1] in 'EIY':
                    metaphone += 'J'
                else:
                    metaphone += 'K'
            elif char == 'H':
                if i == 0 or name[i-1] not in 'AEIOU':
                    metaphone += 'H'
            elif char == 'J':
                metaphone += 'J'
            elif char == 'K':
                metaphone += 'K'
            elif char == 'L':
                metaphone += 'L'
            elif char == 'M':
                metaphone += 'M'
            elif char == 'N':
                metaphone += 'N'
            elif char == 'P':
                if i + 1 < len(name) and name[i + 1] == 'H':
                    metaphone += 'F'
                    i += 1
                else:
                    metaphone += 'P'
            elif char == 'Q':
                metaphone += 'K'
            elif char == 'R':
                metaphone += 'R'
            elif char == 'S':
                if i + 1 < len(name) and name[i + 1] == 'H':
                    metaphone += 'X'
                    i += 1
                else:
                    metaphone += 'S'
            elif char == 'T':
                if i + 1 < len(name) and name[i + 1] == 'H':
                    metaphone += '0'
                    i += 1
                else:
                    metaphone += 'T'
            elif char == 'V':
                metaphone += 'F'
            elif char == 'W':
                metaphone += 'W'
            elif char == 'X':
                metaphone += 'KS'
            elif char == 'Y':
                metaphone += 'Y'
            elif char == 'Z':
                metaphone += 'S'
            
            i += 1
        
        return metaphone
    
    def phonetic_similarity(self, name1: str, name2: str) -> float:
        """Calculate phonetic similarity between two names."""
        soundex1 = self.soundex(name1)
        soundex2 = self.soundex(name2)
        
        metaphone1 = self.metaphone(name1)
        metaphone2 = self.metaphone(name2)
        
        # Soundex exact match gets high score
        if soundex1 == soundex2:
            soundex_score = 1.0
        else:
            soundex_score = 0.0
        
        # Metaphone similarity
        if metaphone1 == metaphone2:
            metaphone_score = 1.0
        elif metaphone1 and metaphone2:
            # Calculate character overlap
            common = sum(1 for a, b in zip(metaphone1, metaphone2) if a == b)
            max_len = max(len(metaphone1), len(metaphone2))
            metaphone_score = common / max_len if max_len > 0 else 0.0
        else:
            metaphone_score = 0.0
        
        # Weighted combination
        return soundex_score * 0.6 + metaphone_score * 0.4
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for phonetic processing."""
        # Remove accents and special characters
        name = unicodedata.normalize('NFD', name)
        name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
        
        # Remove non-alphabetic characters
        name = re.sub(r'[^a-zA-Z]', '', name)
        
        return name.upper()


class EditDistanceMatcher:
    """Edit distance algorithms for name similarity."""
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def similarity_ratio(self, s1: str, s2: str) -> float:
        """Calculate similarity ratio based on edit distance."""
        s1 = s1.lower().strip()
        s2 = s2.lower().strip()
        
        if s1 == s2:
            return 1.0
        
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        distance = self.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
    
    def jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler similarity."""
        s1 = s1.lower().strip()
        s2 = s2.lower().strip()
        
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Maximum allowed distance
        match_distance = max(len1, len2) // 2 - 1
        match_distance = max(0, match_distance)
        
        # Arrays to track matches
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Count transpositions
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        jaro = (matches / len1 + matches / len2 + 
                (matches - transpositions/2) / matches) / 3
        
        # Calculate Jaro-Winkler similarity
        if jaro < 0.7:
            return jaro
        
        # Find common prefix (up to 4 characters)
        prefix = 0
        for i in range(min(len1, len2, 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break
        
        return jaro + (0.1 * prefix * (1 - jaro))


class CulturalNameMatcher:
    """Matcher for cultural name variations and equivalents."""
    
    def __init__(self):
        self.name_equivalents = self._load_name_equivalents()
        self.cultural_patterns = self._load_cultural_patterns()
        
    def find_cultural_matches(self, name: str) -> List[str]:
        """Find cultural variations of a name."""
        name_lower = name.lower().strip()
        matches = []
        
        # Direct equivalents
        if name_lower in self.name_equivalents:
            matches.extend(self.name_equivalents[name_lower])
        
        # Reverse lookup
        for canonical, variants in self.name_equivalents.items():
            if name_lower in [v.lower() for v in variants]:
                matches.append(canonical)
                matches.extend([v for v in variants if v.lower() != name_lower])
        
        # Cultural patterns (diminutives, etc.)
        for pattern_type, patterns in self.cultural_patterns.items():
            for pattern, replacements in patterns.items():
                if name_lower.endswith(pattern):
                    base = name_lower[:-len(pattern)]
                    for replacement in replacements:
                        matches.append(base + replacement)
        
        return list(set(matches))
    
    def cultural_similarity(self, name1: str, name2: str) -> float:
        """Calculate cultural similarity between names."""
        name1_variants = set([name1.lower()] + [v.lower() for v in self.find_cultural_matches(name1)])
        name2_variants = set([name2.lower()] + [v.lower() for v in self.find_cultural_matches(name2)])
        
        # Check for overlap
        if name1_variants & name2_variants:
            return 1.0
        
        return 0.0
    
    def _load_name_equivalents(self) -> Dict[str, List[str]]:
        """Load name equivalents database."""
        return {
            'jose': ['josé', 'joseph', 'joe', 'pepe'],
            'maria': ['maría', 'mary', 'marie'],
            'juan': ['john', 'johnny'],
            'carlos': ['charles', 'charlie'],
            'luis': ['louis', 'louie'],
            'miguel': ['michael', 'mike'],
            'antonio': ['anthony', 'tony'],
            'francisco': ['francis', 'frank', 'paco', 'pancho'],
            'ana': ['anna', 'anne'],
            'carmen': ['carla'],
            'teresa': ['theresa', 'terry'],
            'patricia': ['patty', 'pat'],
            'alejandro': ['alexander', 'alex'],
            'fernando': ['ferdinand', 'fred'],
            'roberto': ['robert', 'bob'],
            'eduardo': ['edward', 'ed'],
            'rafael': ['raphael', 'ralph'],
            'manuel': ['emmanuel', 'manny'],
            'jesus': ['jesse'],
            'david': ['dave'],
            'daniel': ['dan', 'danny'],
            'jorge': ['george'],
            'ricardo': ['richard', 'rick'],
            'alberto': ['albert'],
            'raul': ['ralph'],
            'enrique': ['henry', 'hank'],
            'guadalupe': ['lupe'],
            'esperanza': ['hope'],
            'dolores': ['lola'],
            'concepcion': ['concha', 'connie'],
            'rosario': ['rosa', 'rose']
        }
    
    def _load_cultural_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load cultural name patterns."""
        return {
            'spanish_diminutives': {
                'ito': ['illo', 'ico'],
                'ita': ['illa', 'ica'],
                'cito': ['cillo', 'cico'],
                'cita': ['cilla', 'cica']
            },
            'english_diminutives': {
                'y': ['ie'],
                'ie': ['y']
            }
        }


class AdvancedFuzzyMatcher:
    """Advanced fuzzy matching engine combining multiple algorithms."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.phonetic_matcher = PhoneticMatcher()
        self.edit_distance_matcher = EditDistanceMatcher()
        self.cultural_matcher = CulturalNameMatcher()
        
    def match_names(self, target_name: str, candidate_names: List[str], 
                   threshold: float = 0.7) -> List[MatchResult]:
        """Find fuzzy matches for a target name against candidates."""
        results = []
        
        for candidate in candidate_names:
            match_result = self._calculate_match(target_name, candidate)
            if match_result.confidence >= threshold:
                results.append(match_result)
        
        # Sort by confidence score (highest first)
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def find_best_match(self, target_name: str, candidate_names: List[str]) -> Optional[MatchResult]:
        """Find the best fuzzy match for a target name."""
        matches = self.match_names(target_name, candidate_names, threshold=0.0)
        return matches[0] if matches else None
    
    def _calculate_match(self, name1: str, name2: str) -> MatchResult:
        """Calculate comprehensive match between two names."""
        # Exact match
        if name1.lower().strip() == name2.lower().strip():
            return MatchResult(
                original_name=name1,
                matched_name=name2,
                similarity_score=1.0,
                match_type="exact",
                confidence=1.0
            )
        
        # Calculate different similarity metrics
        phonetic_sim = self.phonetic_matcher.phonetic_similarity(name1, name2)
        edit_sim = self.edit_distance_matcher.similarity_ratio(name1, name2)
        jaro_sim = self.edit_distance_matcher.jaro_winkler_similarity(name1, name2)
        cultural_sim = self.cultural_matcher.cultural_similarity(name1, name2)
        
        # Determine primary match type
        if cultural_sim > 0.9:
            match_type = "cultural"
            primary_score = cultural_sim
        elif phonetic_sim > 0.8:
            match_type = "phonetic" 
            primary_score = phonetic_sim
        else:
            match_type = "edit_distance"
            primary_score = max(edit_sim, jaro_sim)
        
        # Calculate weighted confidence score
        confidence = (
            phonetic_sim * 0.3 +
            edit_sim * 0.25 +
            jaro_sim * 0.25 +
            cultural_sim * 0.2
        )
        
        # Boost confidence for high individual scores
        if max(phonetic_sim, edit_sim, jaro_sim, cultural_sim) > 0.9:
            confidence = min(1.0, confidence * 1.1)
        
        return MatchResult(
            original_name=name1,
            matched_name=name2,
            similarity_score=primary_score,
            match_type=match_type,
            confidence=confidence
        )
    
    def generate_name_variations(self, name: str, max_variations: int = 10) -> List[str]:
        """Generate potential variations of a name."""
        variations = set()
        
        # Cultural variations
        cultural_vars = self.cultural_matcher.find_cultural_matches(name)
        variations.update(cultural_vars)
        
        # Common spelling variations
        spelling_vars = self._generate_spelling_variations(name)
        variations.update(spelling_vars)
        
        # Remove original name and limit results
        variations.discard(name.lower())
        return list(variations)[:max_variations]
    
    def _generate_spelling_variations(self, name: str) -> List[str]:
        """Generate common spelling variations."""
        variations = []
        name_lower = name.lower()
        
        # Common substitutions
        substitutions = [
            ('ph', 'f'), ('f', 'ph'),
            ('c', 'k'), ('k', 'c'),
            ('z', 's'), ('s', 'z'),
            ('i', 'y'), ('y', 'i'),
            ('ck', 'k'), ('k', 'ck'),
            ('qu', 'kw'), ('kw', 'qu')
        ]
        
        for old, new in substitutions:
            if old in name_lower:
                variation = name_lower.replace(old, new, 1)
                variations.append(variation)
        
        # Double letters
        for i, char in enumerate(name_lower):
            if i > 0 and name_lower[i-1] != char:
                # Add double letter
                variation = name_lower[:i] + char + name_lower[i:]
                variations.append(variation)
                
            if i > 0 and name_lower[i-1] == char:
                # Remove double letter
                variation = name_lower[:i-1] + name_lower[i:]
                variations.append(variation)
        
        return variations