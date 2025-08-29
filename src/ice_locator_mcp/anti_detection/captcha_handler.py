"""
CAPTCHA Detection and Handling System for ICE Locator MCP Server.

This module provides comprehensive CAPTCHA detection, analysis, and handling
capabilities including automated solving strategies and fallback mechanisms.
"""

import asyncio
import base64
import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import structlog
from bs4 import BeautifulSoup


class CaptchaType(Enum):
    """Types of CAPTCHA challenges."""
    UNKNOWN = "unknown"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    IMAGE_CAPTCHA = "image_captcha"
    TEXT_CAPTCHA = "text_captcha"
    CLOUDFLARE = "cloudflare"
    FUNCAPTCHA = "funcaptcha"


class CaptchaStatus(Enum):
    """Status of CAPTCHA handling."""
    DETECTED = "detected"
    SOLVING = "solving"
    SOLVED = "solved"
    FAILED = "failed"
    BYPASSED = "bypassed"
    UNSUPPORTED = "unsupported"


@dataclass
class CaptchaChallenge:
    """Represents a CAPTCHA challenge."""
    captcha_type: CaptchaType
    challenge_data: Dict[str, Any]
    detection_confidence: float
    timestamp: float
    page_url: str
    session_id: str
    
    # Challenge-specific data
    site_key: Optional[str] = None
    challenge_id: Optional[str] = None
    image_data: Optional[bytes] = None
    question: Optional[str] = None
    
    # Solving information
    solution: Optional[str] = None
    solve_time: Optional[float] = None
    status: CaptchaStatus = CaptchaStatus.DETECTED


@dataclass
class SolvingStrategy:
    """Strategy for solving a specific CAPTCHA type."""
    captcha_type: CaptchaType
    priority: int
    enabled: bool
    success_rate: float
    average_solve_time: float
    cost_per_solve: float = 0.0


class CaptchaDetector:
    """Detects various types of CAPTCHA challenges in web pages."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.detection_patterns = self._load_detection_patterns()
        
    def detect_captcha(self, html_content: str, page_url: str) -> Optional[CaptchaChallenge]:
        """Detect CAPTCHA challenge in HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for different CAPTCHA types
        for captcha_type, patterns in self.detection_patterns.items():
            challenge = self._check_captcha_type(soup, captcha_type, patterns, page_url)
            if challenge:
                self.logger.info(
                    "CAPTCHA detected",
                    captcha_type=captcha_type.value,
                    confidence=challenge.detection_confidence,
                    page_url=page_url
                )
                return challenge
        
        return None
    
    def _check_captcha_type(self, soup: BeautifulSoup, captcha_type: CaptchaType, 
                           patterns: Dict[str, Any], page_url: str) -> Optional[CaptchaChallenge]:
        """Check for specific CAPTCHA type."""
        
        confidence = 0.0
        challenge_data = {}
        
        # Element-based detection
        for selector, weight in patterns.get('selectors', {}).items():
            elements = soup.select(selector)
            if elements:
                confidence += weight
                challenge_data[f'elements_{selector}'] = len(elements)
        
        # Text-based detection
        page_text = soup.get_text().lower()
        for keyword, weight in patterns.get('keywords', {}).items():
            if keyword.lower() in page_text:
                confidence += weight
                challenge_data[f'keyword_{keyword}'] = True
        
        # Script-based detection
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or ''
            for pattern, weight in patterns.get('script_patterns', {}).items():
                if pattern.lower() in script_content.lower():
                    confidence += weight
                    challenge_data[f'script_{pattern}'] = True
        
        # URL-based detection
        for pattern, weight in patterns.get('url_patterns', {}).items():
            if pattern.lower() in page_url.lower():
                confidence += weight
                challenge_data[f'url_{pattern}'] = True
        
        # Minimum confidence threshold
        if confidence >= patterns.get('min_confidence', 0.5):
            # Extract specific challenge data
            specific_data = self._extract_challenge_data(soup, captcha_type)
            challenge_data.update(specific_data)
            
            return CaptchaChallenge(
                captcha_type=captcha_type,
                challenge_data=challenge_data,
                detection_confidence=min(confidence, 1.0),
                timestamp=time.time(),
                page_url=page_url,
                session_id="",  # Will be set by caller
                **specific_data
            )
        
        return None
    
    def _extract_challenge_data(self, soup: BeautifulSoup, captcha_type: CaptchaType) -> Dict[str, Any]:
        """Extract challenge-specific data."""
        data = {}
        
        if captcha_type == CaptchaType.RECAPTCHA_V2:
            # Extract site key
            recaptcha_div = soup.find('div', class_='g-recaptcha')
            if recaptcha_div:
                data['site_key'] = recaptcha_div.get('data-sitekey')
        
        elif captcha_type == CaptchaType.RECAPTCHA_V3:
            # Extract site key from script
            scripts = soup.find_all('script')
            for script in scripts:
                content = script.string or ''
                if 'grecaptcha.execute' in content:
                    # Try to extract site key
                    import re
                    match = re.search(r'grecaptcha\.execute\(["\']([^"\']+)["\']', content)
                    if match:
                        data['site_key'] = match.group(1)
        
        elif captcha_type == CaptchaType.HCAPTCHA:
            # Extract hCaptcha site key
            hcaptcha_div = soup.find('div', class_='h-captcha')
            if hcaptcha_div:
                data['site_key'] = hcaptcha_div.get('data-sitekey')
        
        elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
            # Extract image CAPTCHA
            img_elements = soup.find_all('img')
            for img in img_elements:
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                if 'captcha' in src.lower() or 'captcha' in alt:
                    data['image_url'] = src
                    break
        
        elif captcha_type == CaptchaType.TEXT_CAPTCHA:
            # Extract text challenge
            challenge_text = self._find_challenge_question(soup)
            if challenge_text:
                data['question'] = challenge_text
        
        return data
    
    def _find_challenge_question(self, soup: BeautifulSoup) -> Optional[str]:
        """Find text-based challenge question."""
        # Common patterns for challenge questions
        question_patterns = [
            ('label', {'for': 'captcha'}),
            ('div', {'class': 'captcha-question'}),
            ('span', {'class': 'challenge-text'}),
        ]
        
        for tag, attrs in question_patterns:
            element = soup.find(tag, attrs)
            if element:
                return element.get_text().strip()
        
        # Look for text near CAPTCHA inputs
        captcha_inputs = soup.find_all('input', {'name': re.compile(r'captcha', re.I)})
        for input_elem in captcha_inputs:
            # Look for preceding label or text
            prev_elements = input_elem.find_previous_siblings()
            for elem in prev_elements[:3]:  # Check up to 3 previous elements
                text = elem.get_text().strip()
                if text and '?' in text:
                    return text
        
        return None
    
    def _load_detection_patterns(self) -> Dict[CaptchaType, Dict[str, Any]]:
        """Load CAPTCHA detection patterns."""
        return {
            CaptchaType.RECAPTCHA_V2: {
                'selectors': {
                    '.g-recaptcha': 0.8,
                    '[data-sitekey]': 0.6,
                    '#recaptcha': 0.5
                },
                'keywords': {
                    'recaptcha': 0.3,
                    'i\'m not a robot': 0.7
                },
                'script_patterns': {
                    'www.google.com/recaptcha': 0.8,
                    'grecaptcha.render': 0.6
                },
                'min_confidence': 0.5
            },
            CaptchaType.RECAPTCHA_V3: {
                'script_patterns': {
                    'grecaptcha.execute': 0.9,
                    'recaptcha/releases/v3': 0.8
                },
                'keywords': {
                    'recaptcha': 0.2
                },
                'min_confidence': 0.6
            },
            CaptchaType.HCAPTCHA: {
                'selectors': {
                    '.h-captcha': 0.9,
                    '[data-sitekey]': 0.4
                },
                'script_patterns': {
                    'hcaptcha.com': 0.8,
                    'hcaptcha.render': 0.7
                },
                'keywords': {
                    'hcaptcha': 0.5
                },
                'min_confidence': 0.5
            },
            CaptchaType.IMAGE_CAPTCHA: {
                'selectors': {
                    'img[src*="captcha"]': 0.8,
                    'img[alt*="captcha"]': 0.7,
                    '.captcha-image': 0.9
                },
                'keywords': {
                    'enter the code': 0.5,
                    'verification code': 0.5,
                    'security code': 0.4
                },
                'min_confidence': 0.4
            },
            CaptchaType.TEXT_CAPTCHA: {
                'keywords': {
                    'what is': 0.4,
                    'solve': 0.3,
                    'math problem': 0.6,
                    'arithmetic': 0.5
                },
                'selectors': {
                    '.math-captcha': 0.8,
                    '.text-challenge': 0.7
                },
                'min_confidence': 0.3
            },
            CaptchaType.CLOUDFLARE: {
                'keywords': {
                    'checking your browser': 0.9,
                    'cloudflare': 0.7,
                    'ddos protection': 0.8
                },
                'script_patterns': {
                    'cloudflare.com': 0.8,
                    'cf-ray': 0.6
                },
                'min_confidence': 0.7
            },
            CaptchaType.FUNCAPTCHA: {
                'script_patterns': {
                    'funcaptcha': 0.9,
                    'arkoselabs': 0.8
                },
                'selectors': {
                    '#funcaptcha': 0.8,
                    '.funcaptcha': 0.7
                },
                'min_confidence': 0.6
            }
        }


class CaptchaSolver:
    """Handles solving different types of CAPTCHA challenges."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.solving_strategies = self._initialize_strategies()
        self.solver_services = self._initialize_solver_services()
        
    def _initialize_solver_services(self):
        """Initialize external CAPTCHA solving services."""
        services = []
        
        # Import external services if available
        try:
            # 2Captcha service
            import os
            twocaptcha_key = os.getenv("TWOCAPTCHA_API_KEY")
            if twocaptcha_key:
                services.append(TwoCaptchaService(twocaptcha_key))
        except ImportError:
            pass
        
        try:
            # Anti-Captcha service
            anticaptcha_key = os.getenv("ANTICAPTCHA_API_KEY")
            if anticaptcha_key:
                services.append(AntiCaptchaService(anticaptcha_key))
        except ImportError:
            pass
        
        try:
            # CapSolver service
            capsolver_key = os.getenv("CAPSOLVER_API_KEY")
            if capsolver_key:
                services.append(CapSolverService(capsolver_key))
        except ImportError:
            pass
        
        return services
    
    async def solve_captcha(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve a CAPTCHA challenge."""
        
        self.logger.info(
            "Attempting to solve CAPTCHA",
            captcha_type=challenge.captcha_type.value,
            confidence=challenge.detection_confidence
        )
        
        challenge.status = CaptchaStatus.SOLVING
        start_time = time.time()
        
        # Try bypass strategies first (cheaper and faster)
        bypass_success = await self._try_bypass_strategies(challenge)
        if bypass_success:
            challenge.status = CaptchaStatus.BYPASSED
            challenge.solve_time = time.time() - start_time
            return True
        
        # Get applicable strategies
        strategies = self._get_strategies_for_type(challenge.captcha_type)
        
        for strategy in strategies:
            if not strategy.enabled:
                continue
                
            try:
                success = await self._apply_strategy(challenge, strategy)
                if success:
                    challenge.status = CaptchaStatus.SOLVED
                    challenge.solve_time = time.time() - start_time
                    
                    self.logger.info(
                        "CAPTCHA solved successfully",
                        captcha_type=challenge.captcha_type.value,
                        strategy=strategy.__class__.__name__,
                        solve_time=challenge.solve_time
                    )
                    return True
                    
            except Exception as e:
                self.logger.warning(
                    "Strategy failed",
                    strategy=strategy.__class__.__name__,
                    error=str(e)
                )
                continue
        
        # All strategies failed
        challenge.status = CaptchaStatus.FAILED
        self.logger.error(
            "Failed to solve CAPTCHA",
            captcha_type=challenge.captcha_type.value,
            strategies_tried=len(strategies)
        )
        return False
    
    async def _try_bypass_strategies(self, challenge: CaptchaChallenge) -> bool:
        """Try bypass strategies before using external solvers."""
        
        # Try waiting for automatic resolution (common for some CAPTCHAs)
        if challenge.captcha_type in [CaptchaType.RECAPTCHA_V3, CaptchaType.CLOUDFLARE]:
            await asyncio.sleep(3)  # Give time for automatic resolution
            return True
        
        # Try browser automation techniques
        if challenge.captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.HCAPTCHA]:
            # Some CAPTCHAs can be bypassed by proper browser fingerprinting
            # This is handled at the browser simulator level
            return False
        
        return False
    
    async def _apply_strategy(self, challenge: CaptchaChallenge, strategy: SolvingStrategy) -> bool:
        """Apply a specific solving strategy."""
        
        if challenge.captcha_type == CaptchaType.RECAPTCHA_V2:
            return await self._solve_recaptcha_v2(challenge)
        elif challenge.captcha_type == CaptchaType.RECAPTCHA_V3:
            return await self._solve_recaptcha_v3(challenge)
        elif challenge.captcha_type == CaptchaType.HCAPTCHA:
            return await self._solve_hcaptcha(challenge)
        elif challenge.captcha_type == CaptchaType.IMAGE_CAPTCHA:
            return await self._solve_image_captcha(challenge)
        elif challenge.captcha_type == CaptchaType.TEXT_CAPTCHA:
            return await self._solve_text_captcha(challenge)
        elif challenge.captcha_type == CaptchaType.CLOUDFLARE:
            return await self._handle_cloudflare(challenge)
        elif challenge.captcha_type == CaptchaType.FUNCAPTCHA:
            return await self._solve_funcaptcha(challenge)
        else:
            return False
    
    async def _solve_recaptcha_v2(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve reCAPTCHA v2."""
        # For reCAPTCHA v2, we typically need external solving services
        # or sophisticated image recognition
        
        if challenge.site_key:
            # Try external solving services
            for service in self.solver_services:
                if service.supports_recaptcha_v2():
                    try:
                        solution = await service.solve_recaptcha_v2(
                            challenge.site_key,
                            challenge.page_url
                        )
                        if solution:
                            challenge.solution = solution
                            return True
                    except Exception as e:
                        self.logger.warning("External service failed", service=service.name, error=str(e))
        
        return False
    
    async def _solve_funcaptcha(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve FunCaptcha."""
        # FunCaptcha typically requires external services
        
        for service in self.solver_services:
            if service.supports_funcaptcha():
                try:
                    solution = await service.solve_funcaptcha(
                        challenge.site_key,
                        challenge.page_url
                    )
                    if solution:
                        challenge.solution = solution
                        return True
                except Exception as e:
                    self.logger.warning("FunCaptcha service failed", error=str(e))
        
        return False
    
    async def _solve_recaptcha_v3(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve reCAPTCHA v3."""
        # reCAPTCHA v3 is score-based and typically requires behavioral analysis
        # For now, we try to wait and see if it automatically passes
        
        await asyncio.sleep(2)  # Give time for score calculation
        return True  # Optimistically assume it passes
    
    async def _solve_hcaptcha(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve hCaptcha."""
        # Similar to reCAPTCHA v2, usually requires external services
        
        for service in self.solver_services:
            if service.supports_hcaptcha():
                try:
                    solution = await service.solve_hcaptcha(
                        challenge.site_key,
                        challenge.page_url
                    )
                    if solution:
                        challenge.solution = solution
                        return True
                except Exception as e:
                    self.logger.warning("hCaptcha service failed", error=str(e))
        
        return False
    
    async def _solve_image_captcha(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve image CAPTCHA."""
        # This would require OCR or image recognition
        # For demonstration, we implement basic patterns
        
        if challenge.image_data:
            # Try basic OCR approaches
            try:
                # This is where you'd integrate with OCR services
                # For now, return False as it requires additional dependencies
                return False
            except Exception as e:
                self.logger.warning("Image CAPTCHA solving failed", error=str(e))
        
        return False
    
    async def _solve_text_captcha(self, challenge: CaptchaChallenge) -> bool:
        """Attempt to solve text-based CAPTCHA."""
        question = challenge.question
        if not question:
            return False
        
        # Simple math problems
        if any(op in question for op in ['+', '-', '*', '/', 'plus', 'minus', 'times']):
            answer = self._solve_math_captcha(question)
            if answer is not None:
                challenge.solution = str(answer)
                return True
        
        # Simple text challenges
        simple_answers = {
            'what color is the sky': 'blue',
            'what is 2+2': '4',
            'what day comes after monday': 'tuesday',
            'what month comes before march': 'february'
        }
        
        question_lower = question.lower().strip()
        for q, a in simple_answers.items():
            if q in question_lower:
                challenge.solution = a
                return True
        
        # Try external services for more complex text CAPTCHAs
        for service in self.solver_services:
            if service.supports_text_captcha():
                try:
                    solution = await service.solve_text_captcha(question)
                    if solution:
                        challenge.solution = solution
                        return True
                except Exception as e:
                    self.logger.warning("Text CAPTCHA service failed", error=str(e))
        
        return False
    
    async def _handle_cloudflare(self, challenge: CaptchaChallenge) -> bool:
        """Handle Cloudflare challenge."""
        # Cloudflare challenges often resolve automatically after waiting
        self.logger.info("Waiting for Cloudflare challenge to resolve")
        
        # Wait with exponential backoff
        for wait_time in [5, 10, 20]:
            await asyncio.sleep(wait_time)
            # In real implementation, you'd check if the challenge is resolved
            # For now, assume it resolves after waiting
            return True
        
        return False
    
    def _solve_math_captcha(self, question: str) -> Optional[int]:
        """Solve simple math CAPTCHA."""
        # Extract numbers and operators
        import re
        
        # Pattern for "X + Y" or "X plus Y"
        patterns = [
            r'(\d+)\s*\+\s*(\d+)',
            r'(\d+)\s*plus\s*(\d+)',
            r'(\d+)\s*-\s*(\d+)', 
            r'(\d+)\s*minus\s*(\d+)',
            r'(\d+)\s*\*\s*(\d+)',
            r'(\d+)\s*times\s*(\d+)',
            r'(\d+)\s*/\s*(\d+)',
            r'(\d+)\s*divided by\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                
                if '+' in pattern or 'plus' in pattern:
                    return a + b
                elif '-' in pattern or 'minus' in pattern:
                    return a - b
                elif '*' in pattern or 'times' in pattern:
                    return a * b
                elif '/' in pattern or 'divided' in pattern:
                    return a // b if b != 0 else None
        
        return None
    
    def _get_strategies_for_type(self, captcha_type: CaptchaType) -> List[SolvingStrategy]:
        """Get applicable strategies for CAPTCHA type."""
        strategies = [s for s in self.solving_strategies if s.captcha_type == captcha_type]
        return sorted(strategies, key=lambda x: x.priority)
    
    def _initialize_strategies(self) -> List[SolvingStrategy]:
        """Initialize solving strategies."""
        return [
            SolvingStrategy(
                captcha_type=CaptchaType.TEXT_CAPTCHA,
                priority=1,
                enabled=True,
                success_rate=0.8,
                average_solve_time=1.0
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.CLOUDFLARE,
                priority=1,
                enabled=True,
                success_rate=0.9,
                average_solve_time=15.0
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.RECAPTCHA_V3,
                priority=2,
                enabled=True,
                success_rate=0.7,
                average_solve_time=3.0
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.IMAGE_CAPTCHA,
                priority=3,
                enabled=False,  # Requires OCR setup
                success_rate=0.5,
                average_solve_time=10.0
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.FUNCAPTCHA,
                priority=4,
                enabled=False,  # Requires external services
                success_rate=0.8,
                average_solve_time=25.0,
                cost_per_solve=0.001
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.RECAPTCHA_V2,
                priority=4,
                enabled=False,  # Requires external services
                success_rate=0.9,
                average_solve_time=30.0,
                cost_per_solve=0.001
            ),
            SolvingStrategy(
                captcha_type=CaptchaType.HCAPTCHA,
                priority=4,
                enabled=False,  # Requires external services
                success_rate=0.85,
                average_solve_time=25.0,
                cost_per_solve=0.001
            )
        ]


# External service classes (simplified implementations)
class TwoCaptchaService:
    """2Captcha service integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "2Captcha"
    
    def supports_recaptcha_v2(self) -> bool:
        return True
    
    def supports_hcaptcha(self) -> bool:
        return True
    
    def supports_funcaptcha(self) -> bool:
        return True
    
    def supports_text_captcha(self) -> bool:
        return True
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with 2Captcha API
        return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with 2Captcha API
        return None
    
    async def solve_funcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with 2Captcha API
        return None
    
    async def solve_text_captcha(self, question: str) -> Optional[str]:
        # Implementation would interact with 2Captcha API
        return None


class AntiCaptchaService:
    """Anti-Captcha service integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "Anti-Captcha"
    
    def supports_recaptcha_v2(self) -> bool:
        return True
    
    def supports_hcaptcha(self) -> bool:
        return True
    
    def supports_funcaptcha(self) -> bool:
        return True
    
    def supports_text_captcha(self) -> bool:
        return True
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with Anti-Captcha API
        return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with Anti-Captcha API
        return None
    
    async def solve_funcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with Anti-Captcha API
        return None
    
    async def solve_text_captcha(self, question: str) -> Optional[str]:
        # Implementation would interact with Anti-Captcha API
        return None


class CapSolverService:
    """CapSolver service integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "CapSolver"
    
    def supports_recaptcha_v2(self) -> bool:
        return True
    
    def supports_hcaptcha(self) -> bool:
        return True
    
    def supports_funcaptcha(self) -> bool:
        return True
    
    def supports_text_captcha(self) -> bool:
        return True
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with CapSolver API
        return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with CapSolver API
        return None
    
    async def solve_funcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Implementation would interact with CapSolver API
        return None
    
    async def solve_text_captcha(self, question: str) -> Optional[str]:
        # Implementation would interact with CapSolver API
        return None


class CaptchaHandler:
    """Main CAPTCHA handling coordinator."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.detector = CaptchaDetector()
        self.solver = CaptchaSolver()
        self.challenge_history: List[CaptchaChallenge] = []
        
    async def handle_response(self, html_content: str, page_url: str, 
                            session_id: str) -> Tuple[bool, Optional[CaptchaChallenge]]:
        """Handle potential CAPTCHA in response."""
        
        # Detect CAPTCHA
        challenge = self.detector.detect_captcha(html_content, page_url)
        
        if not challenge:
            return True, None  # No CAPTCHA detected
        
        challenge.session_id = session_id
        self.challenge_history.append(challenge)
        
        # Attempt to solve
        solved = await self.solver.solve_captcha(challenge)
        
        return solved, challenge
    
    def get_challenge_stats(self) -> Dict[str, Any]:
        """Get statistics about CAPTCHA challenges."""
        if not self.challenge_history:
            return {'total_challenges': 0}
        
        total = len(self.challenge_history)
        solved = sum(1 for c in self.challenge_history if c.status == CaptchaStatus.SOLVED)
        
        by_type = {}
        for challenge in self.challenge_history:
            captcha_type = challenge.captcha_type.value
            if captcha_type not in by_type:
                by_type[captcha_type] = {'total': 0, 'solved': 0}
            by_type[captcha_type]['total'] += 1
            if challenge.status == CaptchaStatus.SOLVED:
                by_type[captcha_type]['solved'] += 1
        
        return {
            'total_challenges': total,
            'solved_challenges': solved,
            'success_rate': solved / total if total > 0 else 0,
            'by_type': by_type,
            'average_solve_time': sum(
                c.solve_time for c in self.challenge_history 
                if c.solve_time is not None
            ) / max(1, sum(1 for c in self.challenge_history if c.solve_time is not None))
        }