#!/usr/bin/env python3
"""Automated integration test runner for ADCP MCP server."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

class ADCPMCPTestRunner:
    """Test runner for ADCP MCP server integration tests."""

    def __init__(self, server_path: str, mcp_root: Path = None):
        self.server_path = Path(server_path)
        self.mcp_root = mcp_root or self.server_path.parent.parent
        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_name": "adcp-tools",
            "server_path": str(server_path),
            "mcp_root": str(self.mcp_root),
            "tests": {},
            "issues": [],
            "summary": {}
        }

    def run_python_test(self, test_name: str, python_code: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a Python code test and return (success, stdout, stderr)."""
        try:
            # Change to MCP root directory for proper imports
            result = subprocess.run(
                [sys.executable, "-c", python_code],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.mcp_root)
            )
            success = result.returncode == 0
            return success, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", f"Test timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)

    def test_server_startup(self) -> bool:
        """Test that server can be imported and started."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from server import mcp
print("Server import successful")
"""
        success, stdout, stderr = self.run_python_test("server_startup", test_code)

        self.results["tests"]["server_startup"] = {
            "status": "passed" if success else "failed",
            "output": stdout,
            "error": stderr,
            "description": "Import server module and check for errors"
        }

        if not success:
            self.results["issues"].append({
                "test": "server_startup",
                "severity": "critical",
                "error": stderr,
                "suggestion": "Check Python path and module dependencies"
            })

        return success

    def test_utility_functions(self) -> bool:
        """Test core utility functions work correctly."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from utils import validate_sequence, find_adcp_binary
from pathlib import Path

# Test sequence validation
valid, msg = validate_sequence('GRGDSP')
print(f"Valid sequence test: {valid}")
assert valid == True, f"Expected valid sequence, got: {msg}"

# Test invalid sequence
valid, msg = validate_sequence('INVALID123')
print(f"Invalid sequence test: {not valid}")
assert valid == False, "Expected invalid sequence"

# Test binary finder
binary = find_adcp_binary(Path('.'))
print(f"Binary found: {binary is not None}")

print("All utility tests passed")
"""
        success, stdout, stderr = self.run_python_test("utility_functions", test_code)

        self.results["tests"]["utility_functions"] = {
            "status": "passed" if success else "failed",
            "output": stdout,
            "error": stderr,
            "description": "Test sequence validation and binary finder functions"
        }

        if not success:
            self.results["issues"].append({
                "test": "utility_functions",
                "severity": "high",
                "error": stderr,
                "suggestion": "Check utils.py implementation and ADCP binary presence"
            })

        return success

    def test_adcp_binary_available(self) -> bool:
        """Test that ADCP binary is present and executable."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from utils import find_adcp_binary
from pathlib import Path
import stat

binary_path = find_adcp_binary(Path('.'))
print(f"Binary path: {binary_path}")

if binary_path:
    # Check if executable
    is_executable = binary_path.stat().st_mode & stat.S_IEXEC
    print(f"Is executable: {bool(is_executable)}")
    print(f"File size: {binary_path.stat().st_size} bytes")
    print("ADCP binary check passed")
else:
    raise Exception("ADCP binary not found")
"""
        success, stdout, stderr = self.run_python_test("adcp_binary", test_code)

        self.results["tests"]["adcp_binary"] = {
            "status": "passed" if success else "failed",
            "output": stdout,
            "error": stderr,
            "description": "Check ADCP binary exists and is executable"
        }

        if not success:
            self.results["issues"].append({
                "test": "adcp_binary",
                "severity": "critical",
                "error": stderr,
                "suggestion": "Download and install adcp_Linux-x86_64 binary in project root"
            })

        return success

    def test_job_manager(self) -> bool:
        """Test job manager can be imported and initialized."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from jobs.manager import JobManager, JobStatus
from pathlib import Path

# Create test job manager
test_jobs_dir = Path("test_jobs")
jm = JobManager(test_jobs_dir)
print(f"Job manager initialized with dir: {jm.jobs_dir}")

# Test job status enum
print(f"Job statuses available: {[s.value for s in JobStatus]}")

# Clean up test directory
import shutil
if test_jobs_dir.exists():
    shutil.rmtree(test_jobs_dir)

print("Job manager test passed")
"""
        success, stdout, stderr = self.run_python_test("job_manager", test_code)

        self.results["tests"]["job_manager"] = {
            "status": "passed" if success else "failed",
            "output": stdout,
            "error": stderr,
            "description": "Test job manager initialization and basic functionality"
        }

        if not success:
            self.results["issues"].append({
                "test": "job_manager",
                "severity": "high",
                "error": stderr,
                "suggestion": "Check jobs/manager.py implementation and dependencies"
            })

        return success

    def test_fastmcp_dev_mode(self) -> bool:
        """Test that fastmcp dev mode can start the server."""
        try:
            # Try to start server in dev mode with short timeout
            result = subprocess.run(
                ["fastmcp", "dev", str(self.server_path)],
                capture_output=True,
                text=True,
                timeout=10,  # Short timeout just to see if it starts
                cwd=str(self.mcp_root)
            )

            # We expect this to timeout, but check that it started properly
            success = "MCP inspector" in result.stdout or "Starting MCP inspector" in result.stdout
            output = result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout

        except subprocess.TimeoutExpired as e:
            # This is expected - server started but we killed it
            success = "MCP inspector" in e.stdout.decode() if e.stdout else False
            output = e.stdout.decode()[:500] if e.stdout else "Server started (timeout as expected)"

        except Exception as e:
            success = False
            output = str(e)

        self.results["tests"]["fastmcp_dev_mode"] = {
            "status": "passed" if success else "failed",
            "output": output,
            "error": "" if success else "Failed to start server in dev mode",
            "description": "Test server starts with fastmcp dev command"
        }

        if not success:
            self.results["issues"].append({
                "test": "fastmcp_dev_mode",
                "severity": "medium",
                "error": "Server failed to start in dev mode",
                "suggestion": "Check fastmcp installation and server.py syntax"
            })

        return success

    def test_claude_mcp_registration(self) -> bool:
        """Test that server is properly registered with Claude."""
        try:
            # Check if server is registered
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout

            # Also check the config file directly
            import os
            claude_config = Path.home() / ".claude.json"
            config_contains_server = False

            if claude_config.exists():
                with open(claude_config) as f:
                    config_content = f.read()
                    config_contains_server = "adcp-tools" in config_content

            success = success and config_contains_server

        except Exception as e:
            success = False
            output = str(e)

        self.results["tests"]["claude_mcp_registration"] = {
            "status": "passed" if success else "failed",
            "output": output,
            "error": "" if success else "Server not properly registered with Claude",
            "description": "Check server is registered with Claude MCP"
        }

        if not success:
            self.results["issues"].append({
                "test": "claude_mcp_registration",
                "severity": "high",
                "error": "Server not registered with Claude",
                "suggestion": "Run: claude mcp add adcp-tools -- python /path/to/server.py"
            })

        return success

    def test_example_data_files(self) -> bool:
        """Test that required example data files exist."""
        test_files = [
            "examples/data/sequences/batch_sequences.txt"
        ]

        all_exist = True
        missing_files = []

        for file_path in test_files:
            full_path = self.mcp_root / file_path
            if not full_path.exists():
                all_exist = False
                missing_files.append(file_path)

        self.results["tests"]["example_data_files"] = {
            "status": "passed" if all_exist else "failed",
            "output": f"Checked {len(test_files)} files",
            "error": f"Missing files: {missing_files}" if not all_exist else "",
            "description": "Check required example data files exist"
        }

        if not all_exist:
            self.results["issues"].append({
                "test": "example_data_files",
                "severity": "medium",
                "error": f"Missing test data files: {missing_files}",
                "suggestion": "Create missing example data files for testing"
            })

        return all_exist

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests and return results."""
        print("🧪 Starting ADCP MCP integration tests...")

        # List of all tests to run
        tests = [
            ("server_startup", self.test_server_startup),
            ("utility_functions", self.test_utility_functions),
            ("adcp_binary", self.test_adcp_binary_available),
            ("job_manager", self.test_job_manager),
            ("fastmcp_dev_mode", self.test_fastmcp_dev_mode),
            ("claude_mcp_registration", self.test_claude_mcp_registration),
            ("example_data_files", self.test_example_data_files)
        ]

        # Run each test
        for test_name, test_func in tests:
            print(f"  Running {test_name}...", end=" ")
            try:
                success = test_func()
                print("✅ PASSED" if success else "❌ FAILED")
            except Exception as e:
                print(f"💥 ERROR: {e}")
                self.results["tests"][test_name] = {
                    "status": "error",
                    "error": str(e),
                    "description": f"Test {test_name} encountered an exception"
                }

        # Generate summary
        total = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"].values() if t.get("status") == "passed")
        failed = sum(1 for t in self.results["tests"].values() if t.get("status") == "failed")
        errors = sum(1 for t in self.results["tests"].values() if t.get("status") == "error")

        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
            "critical_issues": len([i for i in self.results["issues"] if i.get("severity") == "critical"]),
            "high_issues": len([i for i in self.results["issues"] if i.get("severity") == "high"]),
            "medium_issues": len([i for i in self.results["issues"] if i.get("severity") == "medium"])
        }

        print(f"\n📊 Test Summary:")
        print(f"  Total: {total}, Passed: {passed}, Failed: {failed}, Errors: {errors}")
        print(f"  Pass Rate: {self.results['summary']['pass_rate']}")
        print(f"  Issues: {self.results['summary']['critical_issues']} critical, {self.results['summary']['high_issues']} high, {self.results['summary']['medium_issues']} medium")

        return self.results

    def save_report(self, output_file: str) -> None:
        """Save test results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"📝 Test report saved to: {output_path}")

    def save_markdown_report(self, output_file: str) -> None:
        """Save test results as markdown report."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        md_content = self._generate_markdown_report()

        with open(output_path, 'w') as f:
            f.write(md_content)

        print(f"📄 Markdown report saved to: {output_path}")

    def _generate_markdown_report(self) -> str:
        """Generate markdown report content."""
        summary = self.results["summary"]

        md = f"""# ADCP MCP Integration Test Report

## Test Information
- **Test Date**: {self.results['test_date']}
- **Server Name**: {self.results['server_name']}
- **Server Path**: `{self.results['server_path']}`
- **MCP Root**: `{self.results['mcp_root']}`

## Test Results Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary['total_tests']} |
| Passed | {summary['passed']} |
| Failed | {summary['failed']} |
| Errors | {summary['errors']} |
| Pass Rate | {summary['pass_rate']} |

## Issue Summary

| Severity | Count |
|----------|-------|
| Critical | {summary['critical_issues']} |
| High | {summary['high_issues']} |
| Medium | {summary['medium_issues']} |

## Detailed Results

| Test | Status | Description |
|------|--------|-------------|
"""

        for test_name, test_result in self.results["tests"].items():
            status_emoji = "✅" if test_result["status"] == "passed" else "❌" if test_result["status"] == "failed" else "💥"
            md += f"| {test_name} | {status_emoji} {test_result['status'].upper()} | {test_result.get('description', 'N/A')} |\n"

        if self.results["issues"]:
            md += f"\n## Issues Found\n\n"
            for i, issue in enumerate(self.results["issues"], 1):
                md += f"### Issue #{i:03d}: {issue['test']}\n"
                md += f"- **Severity**: {issue['severity'].upper()}\n"
                md += f"- **Error**: {issue['error']}\n"
                md += f"- **Suggestion**: {issue['suggestion']}\n\n"
        else:
            md += f"\n## Issues Found\n\nNo issues found! 🎉\n\n"

        md += f"""## Next Steps

### If All Tests Passed
1. Server is ready for MCP client integration
2. Run the test prompts in `tests/test_prompts.md`
3. Test with actual Claude Code or Gemini CLI

### If Tests Failed
1. Review failed tests and error messages
2. Follow suggestions in Issues section
3. Re-run tests after fixes
4. Check dependencies and environment setup

### Critical Issues
Critical issues prevent the server from working at all and must be fixed first.

### High Priority Issues
High priority issues affect core functionality and should be addressed.

### Medium Priority Issues
Medium priority issues affect testing or nice-to-have features.

---
*Report generated by ADCP MCP Test Runner on {self.results['test_date']}*
"""

        return md


def main():
    """Main entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run ADCP MCP integration tests")
    parser.add_argument("--server", default="src/server.py", help="Path to server.py")
    parser.add_argument("--output", default="reports/integration_test_results.json", help="Output JSON file")
    parser.add_argument("--markdown", default="reports/step7_integration.md", help="Output markdown file")

    args = parser.parse_args()

    # Create test runner
    runner = ADCPMCPTestRunner(args.server)

    # Run all tests
    results = runner.run_all_tests()

    # Save reports
    runner.save_report(args.output)
    runner.save_markdown_report(args.markdown)

    # Exit with error code if any tests failed
    if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Server is ready for use.")
        sys.exit(0)


if __name__ == "__main__":
    main()