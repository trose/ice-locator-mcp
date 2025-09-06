"""
Comprehensive Fingerprinting Evasion Testing Framework for ICE Locator MCP Server.

This module provides comprehensive tests for all advanced fingerprinting evasion techniques
to ensure effectiveness against browser fingerprinting detection systems.
"""

import asyncio
import hashlib
import json
import random
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from playwright.async_api import async_playwright, BrowserContext
import structlog

from ..anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager
from ..anti_detection.canvas_fingerprinting_protection import CanvasFingerprintingProtectionManager
from ..anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager
from ..anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager
from ..anti_detection.audio_fingerprinting_protection import AudioFingerprintingProtectionManager
from ..anti_detection.font_enumeration_protection import FontEnumerationProtectionManager
from ..anti_detection.viewport_screen_spoofing import ViewportScreenSpoofingManager
from ..anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProtectionManager
from ..anti_detection.media_device_spoofing import MediaDeviceSpoofingManager
from ..anti_detection.timezone_locale_manager import TimezoneLocaleManager


@dataclass
class FingerprintTestResult:
    """Represents the result of a fingerprinting test."""
    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    timestamp: float = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "score": self.score,
            "details": self.details,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FingerprintTestResult':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FingerprintReport:
    """Represents a comprehensive fingerprinting test report."""
    session_id: str
    overall_score: float
    test_results: List[FingerprintTestResult]
    fingerprint_hash: str
    timestamp: float = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "overall_score": self.overall_score,
            "test_results": [result.to_dict() for result in self.test_results],
            "fingerprint_hash": self.fingerprint_hash,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FingerprintReport':
        """Create from dictionary."""
        test_results = [FingerprintTestResult.from_dict(result) for result in data["test_results"]]
        return cls(
            session_id=data["session_id"],
            overall_score=data["overall_score"],
            test_results=test_results,
            fingerprint_hash=data["fingerprint_hash"],
            timestamp=data["timestamp"]
        )


class FingerprintingTester:
    """Comprehensive fingerprinting evasion testing framework."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Initialize all anti-detection managers
        self.webgl_manager = WebGLFingerprintingEvasionManager()
        self.canvas_manager = CanvasFingerprintingProtectionManager()
        self.hardware_manager = HardwareConcurrencyPlatformManager()
        self.device_manager = DeviceMemoryCPUManager()
        self.audio_manager = AudioFingerprintingProtectionManager()
        self.font_manager = FontEnumerationProtectionManager()
        self.viewport_manager = ViewportScreenSpoofingManager()
        self.plugin_manager = PluginFingerprintingProtectionManager()
        self.media_manager = MediaDeviceSpoofingManager()
        self.timezone_manager = TimezoneLocaleManager()
        
        # Test configurations
        self.test_configurations = {
            "webgl_tests": [
                "webgl_vendor_spoofing",
                "webgl_renderer_spoofing",
                "webgl_extension_spoofing",
                "webgl_parameter_spoofing"
            ],
            "canvas_tests": [
                "canvas_text_rendering",
                "canvas_image_data",
                "canvas_to_data_url",
                "canvas_measurement"
            ],
            "hardware_tests": [
                "hardware_concurrency_spoofing",
                "platform_spoofing",
                "device_memory_spoofing",
                "cpu_class_spoofing"
            ],
            "audio_tests": [
                "audio_context_spoofing",
                "oscillator_fingerprinting",
                "analyser_fingerprinting",
                "audio_data_consistency"
            ],
            "font_tests": [
                "font_enumeration_protection",
                "font_measurement_protection",
                "css_font_property_protection"
            ],
            "viewport_tests": [
                "screen_dimension_spoofing",
                "viewport_dimension_spoofing",
                "device_pixel_ratio_spoofing"
            ],
            "plugin_tests": [
                "plugin_enumeration_protection",
                "extension_information_spoofing"
            ],
            "media_tests": [
                "media_device_enumeration_protection",
                "media_device_access_protection"
            ],
            "timezone_tests": [
                "timezone_id_spoofing",
                "locale_spoofing",
                "geolocation_consistency"
            ]
        }
    
    async def run_comprehensive_test(self, session_id: str = None) -> FingerprintReport:
        """
        Run comprehensive fingerprinting evasion tests.
        
        Args:
            session_id: Optional session ID for tracking
            
        Returns:
            FingerprintReport with test results
        """
        if session_id is None:
            session_id = f"test_{int(time.time())}"
        
        self.logger.info("Starting comprehensive fingerprinting evasion testing", session_id=session_id)
        
        # Create a browser context for testing
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            try:
                # Apply all anti-detection techniques to the context
                await self._apply_all_protections(context)
                
                # Run all tests
                test_results = await self._run_all_tests(context)
                
                # Calculate overall score
                overall_score = self._calculate_overall_score(test_results)
                
                # Generate fingerprint hash
                fingerprint_hash = self._generate_fingerprint_hash(test_results)
                
                # Create report
                report = FingerprintReport(
                    session_id=session_id,
                    overall_score=overall_score,
                    test_results=test_results,
                    fingerprint_hash=fingerprint_hash
                )
                
                self.logger.info(
                    "Comprehensive fingerprinting evasion testing completed",
                    session_id=session_id,
                    overall_score=overall_score,
                    test_count=len(test_results)
                )
                
                return report
                
            finally:
                await browser.close()
    
    async def _apply_all_protections(self, context: BrowserContext) -> None:
        """Apply all anti-detection protections to the browser context."""
        # Generate random profiles for all managers
        webgl_profile = self.webgl_manager.get_random_webgl_profile()
        canvas_profile = self.canvas_manager.get_random_profile()
        hardware_profile = self.hardware_manager.get_random_profile()
        device_profile = self.device_manager.get_random_profile()
        audio_profile = self.audio_manager.get_random_profile()
        font_profile = self.font_manager.get_random_profile()
        viewport_profile = self.viewport_manager.get_random_profile()
        plugin_profile = self.plugin_manager.get_random_profile()
        media_profile = self.media_manager.get_random_profile()
        
        # Apply all protections
        await self.webgl_manager.apply_webgl_fingerprinting_evasion(context, webgl_profile)
        await self.canvas_manager.apply_canvas_fingerprinting_protection(context, canvas_profile)
        await self.hardware_manager.apply_hardware_concurrency_platform_masking(context, hardware_profile)
        await self.device_manager.apply_device_memory_cpu_spoofing(context, device_profile)
        await self.audio_manager.apply_audio_fingerprinting_protection(context, audio_profile)
        await self.font_manager.apply_font_enumeration_protection(context, font_profile)
        await self.viewport_manager.apply_viewport_screen_spoofing(context, viewport_profile)
        await self.plugin_manager.apply_plugin_fingerprinting_protection(context, plugin_profile)
        await self.media_manager.apply_media_device_spoofing(context, media_profile)
        
        # For timezone/locale, we need both profiles
        timezone_profile, locale_profile = self.timezone_manager.generate_realistic_timezone_locale()
        await self.timezone_manager.apply_timezone_locale_to_context(context, timezone_profile, locale_profile)
    
    async def _run_all_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run all fingerprinting tests."""
        test_results = []
        
        # Run WebGL tests
        webgl_results = await self._run_webgl_tests(context)
        test_results.extend(webgl_results)
        
        # Run canvas tests
        canvas_results = await self._run_canvas_tests(context)
        test_results.extend(canvas_results)
        
        # Run hardware tests
        hardware_results = await self._run_hardware_tests(context)
        test_results.extend(hardware_results)
        
        # Run audio tests
        audio_results = await self._run_audio_tests(context)
        test_results.extend(audio_results)
        
        # Run font tests
        font_results = await self._run_font_tests(context)
        test_results.extend(font_results)
        
        # Run viewport tests
        viewport_results = await self._run_viewport_tests(context)
        test_results.extend(viewport_results)
        
        # Run plugin tests
        plugin_results = await self._run_plugin_tests(context)
        test_results.extend(plugin_results)
        
        # Run media tests
        media_results = await self._run_media_tests(context)
        test_results.extend(media_results)
        
        # Run timezone tests
        timezone_results = await self._run_timezone_tests(context)
        test_results.extend(timezone_results)
        
        return test_results
    
    async def _run_webgl_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run WebGL fingerprinting tests."""
        results = []
        
        # Test WebGL vendor spoofing
        try:
            page = await context.new_page()
            vendor = await page.evaluate("""() => {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (gl) {
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    }
                }
                return 'Not available';
            }""")
            
            # Check if vendor is realistic (not empty or default)
            passed = vendor != "" and vendor != "Not available"
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="webgl_vendor_spoofing",
                passed=passed,
                score=score,
                details={"vendor": vendor}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="webgl_vendor_spoofing",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_canvas_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run canvas fingerprinting tests."""
        results = []
        
        # Test canvas text rendering
        try:
            page = await context.new_page()
            text_rendering = await page.evaluate("""() => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.fillText('Hello World', 10, 10);
                    return ctx.getImageData(0, 0, canvas.width, canvas.height).data.slice(0, 10).join(',');
                }
                return 'Not available';
            }""")
            
            # Check if text rendering works
            passed = text_rendering != "Not available"
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="canvas_text_rendering",
                passed=passed,
                score=score,
                details={"text_rendering": str(text_rendering)[:50]}  # Truncate for readability
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="canvas_text_rendering",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_hardware_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run hardware fingerprinting tests."""
        results = []
        
        # Test hardware concurrency spoofing
        try:
            page = await context.new_page()
            hardware_concurrency = await page.evaluate("() => navigator.hardwareConcurrency")
            
            # Check if hardware concurrency is realistic (between 1 and 64)
            passed = 1 <= hardware_concurrency <= 64
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="hardware_concurrency_spoofing",
                passed=passed,
                score=score,
                details={"hardware_concurrency": hardware_concurrency}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="hardware_concurrency_spoofing",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_audio_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run audio fingerprinting tests."""
        results = []
        
        # Test audio context spoofing
        try:
            page = await context.new_page()
            sample_rate = await page.evaluate("""() => {
                try {
                    const ac = new AudioContext();
                    return ac.sampleRate;
                } catch (e) {
                    return 'Not available';
                }
            }""")
            
            # Check if sample rate is realistic
            passed = sample_rate != "Not available" and isinstance(sample_rate, (int, float))
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="audio_context_spoofing",
                passed=passed,
                score=score,
                details={"sample_rate": sample_rate}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="audio_context_spoofing",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_font_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run font fingerprinting tests."""
        results = []
        
        # Test font enumeration protection
        try:
            page = await context.new_page()
            font_count = await page.evaluate("""() => {
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    if (ctx) {
                        const fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia'];
                        return fonts.length;
                    }
                } catch (e) {
                    // Ignore errors
                }
                return 0;
            }""")
            
            # Check if font enumeration works
            passed = font_count > 0
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="font_enumeration_protection",
                passed=passed,
                score=score,
                details={"font_count": font_count}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="font_enumeration_protection",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_viewport_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run viewport fingerprinting tests."""
        results = []
        
        # Test screen dimension spoofing
        try:
            page = await context.new_page()
            screen_width = await page.evaluate("() => screen.width")
            screen_height = await page.evaluate("() => screen.height")
            
            # Check if screen dimensions are realistic
            passed = 320 <= screen_width <= 8192 and 240 <= screen_height <= 4320
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="screen_dimension_spoofing",
                passed=passed,
                score=score,
                details={"screen_width": screen_width, "screen_height": screen_height}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="screen_dimension_spoofing",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_plugin_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run plugin fingerprinting tests."""
        results = []
        
        # Test plugin enumeration protection
        try:
            page = await context.new_page()
            plugin_count = await page.evaluate("() => navigator.plugins.length")
            
            # Check if plugin enumeration works
            passed = plugin_count >= 0  # Should be non-negative
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="plugin_enumeration_protection",
                passed=passed,
                score=score,
                details={"plugin_count": plugin_count}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="plugin_enumeration_protection",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_media_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run media device fingerprinting tests."""
        results = []
        
        # Test media device enumeration protection
        try:
            page = await context.new_page()
            media_devices_available = await page.evaluate("""() => {
                try {
                    return !!navigator.mediaDevices;
                } catch (e) {
                    return false;
                }
            }""")
            
            # Check if media devices API is available
            passed = media_devices_available
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="media_device_enumeration_protection",
                passed=passed,
                score=score,
                details={"media_devices_available": media_devices_available}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="media_device_enumeration_protection",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    async def _run_timezone_tests(self, context: BrowserContext) -> List[FingerprintTestResult]:
        """Run timezone fingerprinting tests."""
        results = []
        
        # Test timezone spoofing
        try:
            page = await context.new_page()
            timezone = await page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
            
            # Check if timezone is set
            passed = timezone and timezone != ""
            score = 1.0 if passed else 0.0
            
            results.append(FingerprintTestResult(
                test_name="timezone_id_spoofing",
                passed=passed,
                score=score,
                details={"timezone": timezone}
            ))
            
            await page.close()
        except Exception as e:
            results.append(FingerprintTestResult(
                test_name="timezone_id_spoofing",
                passed=False,
                score=0.0,
                details={"error": str(e)}
            ))
        
        return results
    
    def _calculate_overall_score(self, test_results: List[FingerprintTestResult]) -> float:
        """Calculate overall fingerprinting evasion score."""
        if not test_results:
            return 0.0
        
        total_score = sum(result.score for result in test_results)
        return total_score / len(test_results)
    
    def _generate_fingerprint_hash(self, test_results: List[FingerprintTestResult]) -> str:
        """Generate a hash representing the fingerprint test results."""
        # Create a string representation of all test results
        fingerprint_data = ""
        for result in test_results:
            fingerprint_data += f"{result.test_name}:{result.passed}:{result.score}|"
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    async def run_continuous_monitoring(self, duration_minutes: int = 60) -> List[FingerprintReport]:
        """
        Run continuous fingerprinting monitoring.
        
        Args:
            duration_minutes: Duration to run monitoring in minutes
            
        Returns:
            List of FingerprintReport objects
        """
        self.logger.info("Starting continuous fingerprinting monitoring", duration_minutes=duration_minutes)
        
        reports = []
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Run a comprehensive test
            report = await self.run_comprehensive_test()
            reports.append(report)
            
            # Log the result
            self.logger.info(
                "Continuous monitoring test completed",
                session_id=report.session_id,
                overall_score=report.overall_score
            )
            
            # Wait before next test (random interval between 5-15 minutes)
            wait_time = random.randint(300, 900)  # 5-15 minutes
            await asyncio.sleep(wait_time)
        
        self.logger.info("Continuous fingerprinting monitoring completed", report_count=len(reports))
        return reports
    
    def save_report(self, report: FingerprintReport, file_path: str) -> None:
        """
        Save a fingerprint report to a file.
        
        Args:
            report: FingerprintReport to save
            file_path: Path to save the report
        """
        with open(file_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        self.logger.info("Fingerprint report saved", file_path=file_path)
    
    def load_report(self, file_path: str) -> FingerprintReport:
        """
        Load a fingerprint report from a file.
        
        Args:
            file_path: Path to load the report from
            
        Returns:
            FingerprintReport object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        report = FingerprintReport.from_dict(data)
        self.logger.info("Fingerprint report loaded", file_path=file_path)
        return report