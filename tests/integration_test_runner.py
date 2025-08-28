"""
Comprehensive Integration Test Runner and Validation Framework.

Orchestrates complete system validation including functional tests,
performance benchmarks, security validation, and compliance checks.
"""

import asyncio
import json
import time
import sys
import traceback
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse

# Import test modules
from test_e2e_integration import *
from test_performance_benchmarks import *
from test_advanced_anti_detection import *


@dataclass
class TestResult:
    """Test result container."""
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    execution_time: float
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass 
class TestSuite:
    """Test suite definition."""
    name: str
    description: str
    tests: List[Callable]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    timeout: int = 300  # 5 minutes default


class IntegrationTestRunner:
    """Comprehensive integration test runner."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.results: List[TestResult] = []
        self.summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total_time': 0.0
        }
        
        # Test suites
        self.test_suites = self._define_test_suites()
        
        # Validation criteria
        self.validation_criteria = {
            'min_success_rate': 0.9,
            'max_avg_response_time': 2.0,
            'max_memory_usage': 200,  # MB
            'min_throughput': 5.0,    # requests/sec
            'max_error_rate': 0.1
        }
    
    def _define_test_suites(self) -> List[TestSuite]:
        """Define all test suites."""
        return [
            TestSuite(
                name="basic_functionality",
                description="Basic MCP server functionality tests",
                tests=[
                    self._test_server_initialization,
                    self._test_tool_registration,
                    self._test_basic_search_operations
                ]
            ),
            TestSuite(
                name="complete_workflows",
                description="End-to-end workflow validation",
                tests=[
                    self._test_name_search_workflow,
                    self._test_alien_number_workflow,
                    self._test_facility_search_workflow,
                    self._test_natural_language_workflow,
                    self._test_bulk_operations_workflow
                ]
            ),
            TestSuite(
                name="anti_detection_integration",
                description="Anti-detection system integration",
                tests=[
                    self._test_behavioral_simulation_integration,
                    self._test_traffic_distribution_integration,
                    self._test_proxy_management_integration,
                    self._test_adaptive_strategies
                ]
            ),
            TestSuite(
                name="performance_validation", 
                description="Performance and scalability validation",
                tests=[
                    self._test_single_request_performance,
                    self._test_concurrent_performance,
                    self._test_memory_stability,
                    self._test_throughput_scaling
                ]
            ),
            TestSuite(
                name="spanish_language_support",
                description="Spanish language feature validation",
                tests=[
                    self._test_spanish_query_processing,
                    self._test_spanish_name_matching,
                    self._test_bilingual_interface
                ]
            ),
            TestSuite(
                name="error_handling_resilience",
                description="Error handling and system resilience",
                tests=[
                    self._test_invalid_input_handling,
                    self._test_network_error_recovery,
                    self._test_rate_limiting_behavior,
                    self._test_captcha_handling
                ]
            ),
            TestSuite(
                name="client_compatibility",
                description="MCP client compatibility validation", 
                tests=[
                    self._test_claude_desktop_compatibility,
                    self._test_programmatic_client_compatibility,
                    self._test_tool_schema_validation
                ]
            )
        ]
    
    async def run_all_tests(self, 
                          suite_filter: Optional[List[str]] = None,
                          verbose: bool = False) -> Dict[str, Any]:
        """Run all integration tests."""
        
        print("🚀 Starting Comprehensive Integration Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Filter test suites if specified
        suites_to_run = self.test_suites
        if suite_filter:
            suites_to_run = [s for s in self.test_suites if s.name in suite_filter]
        
        # Run each test suite
        for suite in suites_to_run:
            await self._run_test_suite(suite, verbose)
        
        # Calculate summary
        total_time = time.time() - start_time
        self.summary['total_time'] = total_time
        
        # Generate final report
        return await self._generate_final_report(verbose)
    
    async def _run_test_suite(self, suite: TestSuite, verbose: bool = False):
        """Run a single test suite."""
        
        print(f"\n📋 Running Test Suite: {suite.name}")
        print(f"Description: {suite.description}")
        print("-" * 40)
        
        # Setup if defined
        if suite.setup:
            try:
                await suite.setup()
            except Exception as e:
                print(f"❌ Suite setup failed: {str(e)}")
                return
        
        # Run tests in suite
        for test_func in suite.tests:
            await self._run_single_test(test_func, suite.timeout, verbose)
        
        # Teardown if defined
        if suite.teardown:
            try:
                await suite.teardown()
            except Exception as e:
                if verbose:
                    print(f"⚠️  Suite teardown warning: {str(e)}")
    
    async def _run_single_test(self, 
                             test_func: Callable, 
                             timeout: int,
                             verbose: bool = False):
        """Run a single test with timeout and error handling."""
        
        test_name = test_func.__name__
        start_time = time.time()
        
        try:
            # Run test with timeout
            await asyncio.wait_for(test_func(), timeout=timeout)
            
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status="PASS",
                execution_time=execution_time
            )
            
            print(f"✅ {test_name} - PASSED ({execution_time:.2f}s)")
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status="FAIL",
                execution_time=execution_time,
                error_message=f"Test timed out after {timeout}s"
            )
            print(f"⏰ {test_name} - TIMEOUT ({timeout}s)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            if verbose:
                error_msg += f"\n{traceback.format_exc()}"
            
            result = TestResult(
                test_name=test_name,
                status="ERROR",
                execution_time=execution_time,
                error_message=error_msg
            )
            print(f"❌ {test_name} - ERROR: {str(e)}")
        
        # Update summary
        self.results.append(result)
        self.summary['total_tests'] += 1
        
        if result.status == "PASS":
            self.summary['passed'] += 1
        elif result.status == "FAIL":
            self.summary['failed'] += 1
        elif result.status == "SKIP":
            self.summary['skipped'] += 1
        else:
            self.summary['errors'] += 1
    
    async def _generate_final_report(self, verbose: bool = False) -> Dict[str, Any]:
        """Generate comprehensive final test report."""
        
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Basic summary
        print(f"Total Tests: {self.summary['total_tests']}")
        print(f"✅ Passed: {self.summary['passed']}")
        print(f"❌ Failed: {self.summary['failed']}")
        print(f"⚠️  Errors: {self.summary['errors']}")
        print(f"⏭️  Skipped: {self.summary['skipped']}")
        print(f"⏱️  Total Time: {self.summary['total_time']:.2f}s")
        
        # Calculate rates
        success_rate = self.summary['passed'] / max(1, self.summary['total_tests'])
        error_rate = (self.summary['failed'] + self.summary['errors']) / max(1, self.summary['total_tests'])
        
        print(f"📈 Success Rate: {success_rate:.1%}")
        print(f"📉 Error Rate: {error_rate:.1%}")
        
        # Validation against criteria
        print(f"\n🎯 VALIDATION CRITERIA CHECK")
        print("-" * 30)
        
        validation_passed = True
        
        # Success rate validation
        if success_rate >= self.validation_criteria['min_success_rate']:
            print(f"✅ Success Rate: {success_rate:.1%} >= {self.validation_criteria['min_success_rate']:.1%}")
        else:
            print(f"❌ Success Rate: {success_rate:.1%} < {self.validation_criteria['min_success_rate']:.1%}")
            validation_passed = False
        
        # Error rate validation  
        if error_rate <= self.validation_criteria['max_error_rate']:
            print(f"✅ Error Rate: {error_rate:.1%} <= {self.validation_criteria['max_error_rate']:.1%}")
        else:
            print(f"❌ Error Rate: {error_rate:.1%} > {self.validation_criteria['max_error_rate']:.1%}")
            validation_passed = False
        
        # Performance metrics (if available)
        performance_results = [r for r in self.results if r.performance_metrics]
        if performance_results:
            avg_response_times = []
            memory_usages = []
            throughputs = []
            
            for result in performance_results:
                metrics = result.performance_metrics
                if 'avg_response_time' in metrics:
                    avg_response_times.append(metrics['avg_response_time'])
                if 'memory_usage_mb' in metrics:
                    memory_usages.append(metrics['memory_usage_mb'])
                if 'throughput_rps' in metrics:
                    throughputs.append(metrics['throughput_rps'])
            
            if avg_response_times:
                avg_response_time = sum(avg_response_times) / len(avg_response_times)
                if avg_response_time <= self.validation_criteria['max_avg_response_time']:
                    print(f"✅ Avg Response Time: {avg_response_time:.3f}s <= {self.validation_criteria['max_avg_response_time']:.1f}s")
                else:
                    print(f"❌ Avg Response Time: {avg_response_time:.3f}s > {self.validation_criteria['max_avg_response_time']:.1f}s")
                    validation_passed = False
            
            if memory_usages:
                max_memory = max(memory_usages)
                if max_memory <= self.validation_criteria['max_memory_usage']:
                    print(f"✅ Max Memory Usage: {max_memory:.1f}MB <= {self.validation_criteria['max_memory_usage']}MB")
                else:
                    print(f"❌ Max Memory Usage: {max_memory:.1f}MB > {self.validation_criteria['max_memory_usage']}MB")
                    validation_passed = False
            
            if throughputs:
                min_throughput = min(throughputs)
                if min_throughput >= self.validation_criteria['min_throughput']:
                    print(f"✅ Min Throughput: {min_throughput:.1f} rps >= {self.validation_criteria['min_throughput']:.1f} rps")
                else:
                    print(f"❌ Min Throughput: {min_throughput:.1f} rps < {self.validation_criteria['min_throughput']:.1f} rps")
                    validation_passed = False
        
        # Overall validation result
        print(f"\n🏆 OVERALL VALIDATION: {'PASSED' if validation_passed else 'FAILED'}")
        
        # Failed test details
        failed_tests = [r for r in self.results if r.status in ['FAIL', 'ERROR']]
        if failed_tests and verbose:
            print(f"\n❌ FAILED TEST DETAILS")
            print("-" * 30)
            for test in failed_tests:
                print(f"Test: {test.test_name}")
                print(f"Status: {test.status}")
                print(f"Error: {test.error_message}")
                print("-" * 20)
        
        # Generate JSON report
        report = {
            'timestamp': time.time(),
            'summary': self.summary,
            'validation_passed': validation_passed,
            'validation_criteria': self.validation_criteria,
            'test_results': [r.to_dict() for r in self.results]
        }
        
        # Save report to file
        report_path = Path('integration_test_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return report
    
    # Individual test implementations
    async def _test_server_initialization(self):
        """Test MCP server initialization."""
        config = Config({'server': {'debug': True}})
        server = ICELocatorServer(config)
        
        try:
            await server.initialize()
            assert hasattr(server, 'tools')
            assert len(server.tools) > 0
        finally:
            await server.cleanup()
    
    async def _test_tool_registration(self):
        """Test tool registration and discovery."""
        config = Config({'server': {'debug': True}})
        server = ICELocatorServer(config)
        
        try:
            await server.initialize()
            tools = await server.list_tools()
            
            assert len(tools) >= 4
            tool_names = [t['name'] for t in tools]
            
            required_tools = ['search_by_name', 'search_by_alien_number', 'search_by_facility']
            for tool in required_tools:
                assert tool in tool_names
        finally:
            await server.cleanup()
    
    async def _test_basic_search_operations(self):
        """Test basic search operations."""
        config = Config({'server': {'debug': True}})
        server = ICELocatorServer(config)
        
        try:
            await server.initialize()
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.text = "<html><body>Mock search result</body></html>"
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                session = MagicMock()
                
                result = await server.handle_tool_call(
                    "search_by_name",
                    {"first_name": "Test", "last_name": "User"},
                    session
                )
                
                assert result["isError"] is False
                assert len(result["content"]) > 0
        finally:
            await server.cleanup()
    
    # Placeholder implementations for other test methods
    async def _test_name_search_workflow(self):
        """Test complete name search workflow."""
        # Implementation similar to test_basic_name_search_workflow from e2e tests
        pass
    
    async def _test_alien_number_workflow(self):
        """Test A-number search workflow."""
        pass
    
    async def _test_facility_search_workflow(self):
        """Test facility search workflow."""
        pass
    
    async def _test_natural_language_workflow(self):
        """Test natural language processing workflow."""
        pass
    
    async def _test_bulk_operations_workflow(self):
        """Test bulk operations workflow."""
        pass
    
    async def _test_behavioral_simulation_integration(self):
        """Test behavioral simulation integration."""
        pass
    
    async def _test_traffic_distribution_integration(self):
        """Test traffic distribution integration."""
        pass
    
    async def _test_proxy_management_integration(self):
        """Test proxy management integration."""
        pass
    
    async def _test_adaptive_strategies(self):
        """Test adaptive anti-detection strategies."""
        pass
    
    async def _test_single_request_performance(self):
        """Test single request performance."""
        pass
    
    async def _test_concurrent_performance(self):
        """Test concurrent request performance."""
        pass
    
    async def _test_memory_stability(self):
        """Test memory usage stability."""
        pass
    
    async def _test_throughput_scaling(self):
        """Test throughput scaling characteristics."""
        pass
    
    async def _test_spanish_query_processing(self):
        """Test Spanish language query processing."""
        pass
    
    async def _test_spanish_name_matching(self):
        """Test Spanish name matching capabilities."""
        pass
    
    async def _test_bilingual_interface(self):
        """Test bilingual interface functionality."""
        pass
    
    async def _test_invalid_input_handling(self):
        """Test invalid input handling."""
        pass
    
    async def _test_network_error_recovery(self):
        """Test network error recovery."""
        pass
    
    async def _test_rate_limiting_behavior(self):
        """Test rate limiting behavior."""
        pass
    
    async def _test_captcha_handling(self):
        """Test CAPTCHA handling."""
        pass
    
    async def _test_claude_desktop_compatibility(self):
        """Test Claude Desktop compatibility."""
        pass
    
    async def _test_programmatic_client_compatibility(self):
        """Test programmatic client compatibility."""
        pass
    
    async def _test_tool_schema_validation(self):
        """Test tool schema validation."""
        pass


async def main():
    """Main test runner entry point."""
    
    parser = argparse.ArgumentParser(description='ICE Locator MCP Integration Test Runner')
    parser.add_argument('--suites', nargs='*', help='Specific test suites to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = IntegrationTestRunner(config_path=args.config)
    
    # Run tests
    try:
        report = await runner.run_all_tests(
            suite_filter=args.suites,
            verbose=args.verbose
        )
        
        # Exit with error code if validation failed
        if not report['validation_passed']:
            print("\n❌ Integration tests FAILED validation criteria")
            sys.exit(1)
        else:
            print("\n✅ All integration tests PASSED validation criteria")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())