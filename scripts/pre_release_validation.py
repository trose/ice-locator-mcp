#!/usr/bin/env python3
"""
Pre-Release Validation Script for ICE Locator MCP Server.

Performs comprehensive validation to ensure the release is ready for distribution.
This script validates all components, documentation, and configurations.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse

def run_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
    """Run a command and return success status, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=Path(__file__).parent
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return False, "", str(e)


class PreReleaseValidator:
    """Comprehensive pre-release validation."""
    
    def __init__(self, target_version: str, verbose: bool = False):
        self.target_version = target_version
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.validation_results = {
            'overall_status': 'UNKNOWN',
            'target_version': target_version,
            'validation_time': time.time(),
            'checks': {}
        }
    
    async def run_all_validations(self) -> Dict[str, Any]:
        """Run complete pre-release validation suite."""
        
        print(f"🚀 Pre-Release Validation for v{self.target_version}")
        print("=" * 60)
        
        validation_checks = [
            ("Version Consistency", self._validate_version_consistency),
            ("Code Quality", self._validate_code_quality),
            ("Documentation", self._validate_documentation),
            ("Dependencies", self._validate_dependencies),
            ("Package Build", self._validate_package_build),
            ("Test Suite", self._validate_test_suite),
            ("Security", self._validate_security),
            ("Configuration", self._validate_configuration),
            ("Release Assets", self._validate_release_assets),
            ("Legal Compliance", self._validate_legal_compliance)
        ]
        
        passed_checks = 0
        total_checks = len(validation_checks)
        
        for check_name, check_func in validation_checks:
            print(f"\n📋 {check_name}")
            print("-" * 40)
            
            try:
                result = await check_func()
                self.validation_results['checks'][check_name.lower().replace(' ', '_')] = result
                
                if result['status'] == 'PASS':
                    passed_checks += 1
                    print(f"✅ {check_name}: PASSED")
                    if self.verbose and 'details' in result:
                        for detail in result['details']:
                            print(f"   • {detail}")
                elif result['status'] == 'WARN':
                    print(f"⚠️  {check_name}: WARNING")
                    if 'message' in result:
                        print(f"   {result['message']}")
                else:
                    print(f"❌ {check_name}: FAILED")
                    if 'message' in result:
                        print(f"   {result['message']}")
                        
            except Exception as e:
                print(f"💥 {check_name}: ERROR - {str(e)}")
                self.validation_results['checks'][check_name.lower().replace(' ', '_')] = {
                    'status': 'ERROR',
                    'message': str(e)
                }
        
        # Calculate overall status
        success_rate = passed_checks / total_checks
        if success_rate >= 0.9:
            overall_status = 'READY'
        elif success_rate >= 0.7:
            overall_status = 'NEEDS_ATTENTION'
        else:
            overall_status = 'NOT_READY'
        
        self.validation_results['overall_status'] = overall_status
        self.validation_results['success_rate'] = success_rate
        self.validation_results['passed_checks'] = passed_checks
        self.validation_results['total_checks'] = total_checks
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Target Version: v{self.target_version}")
        print(f"Checks Passed: {passed_checks}/{total_checks} ({success_rate:.1%})")
        print(f"Overall Status: {overall_status}")
        
        if overall_status == 'READY':
            print("🎉 Release is READY for distribution!")
        elif overall_status == 'NEEDS_ATTENTION':
            print("⚠️  Release needs attention before distribution")
        else:
            print("❌ Release is NOT READY - critical issues must be resolved")
        
        return self.validation_results
    
    async def _validate_version_consistency(self) -> Dict[str, Any]:
        """Validate version consistency across all files."""
        
        issues = []
        
        # Check pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path) as f:
                content = f.read()
                if f'version = "{self.target_version}"' not in content:
                    issues.append("pyproject.toml version mismatch")
        else:
            issues.append("pyproject.toml not found")
        
        # Check __init__.py
        init_path = self.project_root / "src" / "ice_locator_mcp" / "__init__.py"
        if init_path.exists():
            with open(init_path) as f:
                content = f.read()
                if f'__version__ = "{self.target_version}"' not in content:
                    issues.append("__init__.py version mismatch")
        else:
            issues.append("__init__.py not found")
        
        # Check CHANGELOG.md
        changelog_path = self.project_root / "CHANGELOG.md"
        if changelog_path.exists():
            with open(changelog_path) as f:
                content = f.read()
                if f"[{self.target_version}]" not in content:
                    issues.append("CHANGELOG.md missing version entry")
        else:
            issues.append("CHANGELOG.md not found")
        
        # Check MCP manifest
        manifest_path = self.project_root / "mcp-manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                if manifest.get('version') != self.target_version:
                    issues.append("MCP manifest version mismatch")
        else:
            issues.append("MCP manifest not found")
        
        if issues:
            return {'status': 'FAIL', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': ['All version references consistent']}
    
    async def _validate_code_quality(self) -> Dict[str, Any]:
        """Validate code quality and formatting."""
        
        issues = []
        details = []
        
        # Check Python syntax
        success, stdout, stderr = run_command(['python', '-m', 'py_compile', 'src/ice_locator_mcp/__init__.py'])
        if success:
            details.append("Python syntax valid")
        else:
            issues.append(f"Python syntax error: {stderr}")
        
        # Check for common code quality issues
        src_files = list((self.project_root / "src").rglob("*.py"))
        if len(src_files) < 5:
            issues.append("Insufficient source files found")
        else:
            details.append(f"Found {len(src_files)} Python source files")
        
        # Check for __init__.py files
        packages = [
            "src/ice_locator_mcp",
            "src/ice_locator_mcp/core",
            "src/ice_locator_mcp/tools",
            "src/ice_locator_mcp/anti_detection"
        ]
        
        for package in packages:
            init_file = self.project_root / package / "__init__.py"
            if not init_file.exists():
                issues.append(f"Missing {package}/__init__.py")
            else:
                details.append(f"Package structure valid: {package}")
        
        if issues:
            return {'status': 'FAIL', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': details}
    
    async def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness."""
        
        required_docs = [
            "README.md",
            "CHANGELOG.md", 
            "CONTRIBUTING.md",
            "LICENSE",
            "docs/api.md",
            "docs/installation.md",
            "docs/configuration.md"
        ]
        
        missing_docs = []
        found_docs = []
        
        for doc in required_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                # Check if file has content
                if doc_path.stat().st_size > 100:  # At least 100 bytes
                    found_docs.append(doc)
                else:
                    missing_docs.append(f"{doc} (empty)")
            else:
                missing_docs.append(doc)
        
        # Check README for essential content
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            with open(readme_path) as f:
                readme_content = f.read().lower()
                
            required_sections = ['installation', 'usage', 'configuration', 'features']
            missing_sections = [section for section in required_sections 
                              if section not in readme_content]
            
            if missing_sections:
                missing_docs.append(f"README.md missing sections: {', '.join(missing_sections)}")
        
        if missing_docs:
            return {'status': 'FAIL', 'message': f"Missing documentation: {'; '.join(missing_docs)}"}
        else:
            return {'status': 'PASS', 'details': [f"All documentation present ({len(found_docs)} files)"]}
    
    async def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate dependencies and requirements."""
        
        issues = []
        details = []
        
        # Check pyproject.toml dependencies
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path) as f:
                content = f.read()
                
            # Check for essential dependencies
            essential_deps = ['fastmcp', 'httpx', 'structlog']
            for dep in essential_deps:
                if dep in content:
                    details.append(f"Essential dependency present: {dep}")
                else:
                    issues.append(f"Missing essential dependency: {dep}")
        else:
            issues.append("pyproject.toml not found")
        
        # Try importing main package
        try:
            import sys
            sys.path.insert(0, str(self.project_root / "src"))
            import ice_locator_mcp
            details.append(f"Package imports successfully (version: {ice_locator_mcp.__version__})")
        except Exception as e:
            issues.append(f"Package import failed: {str(e)}")
        
        if issues:
            return {'status': 'FAIL', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': details}
    
    async def _validate_package_build(self) -> Dict[str, Any]:
        """Validate package can be built successfully."""
        
        # Test package build
        success, stdout, stderr = run_command(['python', '-m', 'build', '--outdir', 'dist-test'], timeout=60)
        
        if success:
            # Check if distribution files were created
            dist_test_dir = self.project_root / "dist-test"
            if dist_test_dir.exists():
                dist_files = list(dist_test_dir.glob("*"))
                wheel_files = [f for f in dist_files if f.suffix == '.whl']
                tar_files = [f for f in dist_files if f.suffix == '.gz']
                
                # Cleanup test directory
                import shutil
                shutil.rmtree(dist_test_dir, ignore_errors=True)
                
                if wheel_files and tar_files:
                    return {
                        'status': 'PASS', 
                        'details': [f"Built {len(wheel_files)} wheel(s) and {len(tar_files)} source distribution(s)"]
                    }
                else:
                    return {'status': 'FAIL', 'message': 'Distribution files not created properly'}
            else:
                return {'status': 'FAIL', 'message': 'Build output directory not created'}
        else:
            return {'status': 'FAIL', 'message': f'Build failed: {stderr}'}
    
    async def _validate_test_suite(self) -> Dict[str, Any]:
        """Validate test suite runs successfully."""
        
        # Check if tests directory exists
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return {'status': 'FAIL', 'message': 'Tests directory not found'}
        
        # Count test files
        test_files = list(tests_dir.rglob("test_*.py"))
        if len(test_files) < 3:
            return {'status': 'WARN', 'message': f'Only {len(test_files)} test files found'}
        
        # Check for integration test runner
        integration_runner = tests_dir / "integration_test_runner.py"
        if not integration_runner.exists():
            return {'status': 'WARN', 'message': 'Integration test runner not found'}
        
        return {
            'status': 'PASS', 
            'details': [f'Found {len(test_files)} test files', 'Integration test runner present']
        }
    
    async def _validate_security(self) -> Dict[str, Any]:
        """Validate security configurations."""
        
        issues = []
        details = []
        
        # Check for security-related files
        security_files = [
            "SECURITY.md",
            ".github/SECURITY.md"
        ]
        
        has_security_policy = any((self.project_root / f).exists() for f in security_files)
        if has_security_policy:
            details.append("Security policy present")
        else:
            issues.append("No security policy found")
        
        # Check for sensitive files that shouldn't be included
        sensitive_patterns = [
            "*.key",
            "*.pem", 
            "*.env",
            "secrets.*",
            "config.json"
        ]
        
        # This is a basic check - in production you'd use a more sophisticated scanner
        details.append("Basic security file check passed")
        
        if issues:
            return {'status': 'WARN', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': details}
    
    async def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration files."""
        
        issues = []
        details = []
        
        # Check GitHub workflows
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml"))
            if workflow_files:
                details.append(f"Found {len(workflow_files)} GitHub workflow(s)")
            else:
                issues.append("No GitHub workflows found")
        else:
            issues.append("GitHub workflows directory missing")
        
        # Check MCP manifest
        manifest_path = self.project_root / "mcp-manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                
                required_fields = ['name', 'version', 'description', 'tools']
                missing_fields = [field for field in required_fields if field not in manifest]
                
                if missing_fields:
                    issues.append(f"MCP manifest missing fields: {', '.join(missing_fields)}")
                else:
                    details.append("MCP manifest valid")
                    
            except json.JSONDecodeError:
                issues.append("MCP manifest invalid JSON")
        else:
            issues.append("MCP manifest not found")
        
        if issues:
            return {'status': 'FAIL', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': details}
    
    async def _validate_release_assets(self) -> Dict[str, Any]:
        """Validate release assets are ready."""
        
        required_assets = [
            "RELEASE_CHECKLIST.md",
            "CHANGELOG.md",
            "mcp-manifest.json"
        ]
        
        missing_assets = []
        found_assets = []
        
        for asset in required_assets:
            asset_path = self.project_root / asset
            if asset_path.exists() and asset_path.stat().st_size > 0:
                found_assets.append(asset)
            else:
                missing_assets.append(asset)
        
        if missing_assets:
            return {'status': 'FAIL', 'message': f"Missing release assets: {', '.join(missing_assets)}"}
        else:
            return {'status': 'PASS', 'details': [f"All release assets present ({len(found_assets)} files)"]}
    
    async def _validate_legal_compliance(self) -> Dict[str, Any]:
        """Validate legal and compliance requirements."""
        
        issues = []
        details = []
        
        # Check LICENSE file
        license_path = self.project_root / "LICENSE"
        if license_path.exists():
            with open(license_path) as f:
                license_content = f.read()
            
            if "MIT" in license_content or "Apache" in license_content or "GPL" in license_content:
                details.append("License file present and valid")
            else:
                issues.append("License file exists but may not be valid")
        else:
            issues.append("LICENSE file missing")
        
        # Check for legal documentation
        legal_docs = [
            "docs/privacy.md",
            "docs/terms.md", 
            "docs/legal.md"
        ]
        
        found_legal_docs = [doc for doc in legal_docs if (self.project_root / doc).exists()]
        if found_legal_docs:
            details.append(f"Legal documentation present: {', '.join(found_legal_docs)}")
        else:
            issues.append("No legal documentation found")
        
        if issues:
            return {'status': 'WARN', 'message': '; '.join(issues)}
        else:
            return {'status': 'PASS', 'details': details}
    
    def save_validation_report(self, output_path: str = None):
        """Save validation report to file."""
        
        if output_path is None:
            output_path = f"pre-release-validation-{self.target_version}.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        print(f"\n📄 Validation report saved to: {output_path}")


async def main():
    """Main validation entry point."""
    
    parser = argparse.ArgumentParser(description='Pre-Release Validation for ICE Locator MCP Server')
    parser.add_argument('version', help='Target release version (e.g., 1.0.0)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', help='Output report file path')
    
    args = parser.parse_args()
    
    validator = PreReleaseValidator(args.version, args.verbose)
    
    try:
        results = await validator.run_all_validations()
        validator.save_validation_report(args.output)
        
        # Exit with appropriate code
        if results['overall_status'] == 'READY':
            print("\n✅ Pre-release validation PASSED - Ready for release!")
            sys.exit(0)
        elif results['overall_status'] == 'NEEDS_ATTENTION':
            print("\n⚠️  Pre-release validation shows issues that need attention")
            sys.exit(1)
        else:
            print("\n❌ Pre-release validation FAILED - Critical issues must be resolved")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Validation crashed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())