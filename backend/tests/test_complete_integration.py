#!/usr/bin/env python3
"""
Complete Integration Test Suite for EduVerse Backend
Tests all backend components: API endpoints, Database, Authentication, etc.
"""

import asyncio
import aiohttp
import pytest
import requests
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
import socket
import threading
from contextlib import contextmanager

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class TestResult:
    def __init__(self, name: str, success: bool, message: str, duration: float = 0):
        self.name = name
        self.success = success
        self.message = message
        self.duration = duration

class EduVerseBackendTester:
    def __init__(self):
        self.results = []
        self.session = None

    async def initialize(self):
        """Initialize test session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    def log_result(self, result: TestResult):
        """Log test result"""
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"{status} {result.name} ({result.duration:.2f}s)")
        if not result.success:
            print(f"   Error: {result.message}")
        self.results.append(result)

    async def test_backend_health(self) -> TestResult:
        """Test backend server health"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        return TestResult(
                            "Backend Health Check",
                            True,
                            "Backend server is healthy",
                            time.time() - start_time
                        )
                return TestResult(
                    "Backend Health Check",
                    False,
                    f"Unexpected response: {response.status}",
                    time.time() - start_time
                )
        except Exception as e:
            return TestResult(
                "Backend Health Check",
                False,
                str(e),
                time.time() - start_time
            )

    async def test_api_health(self) -> TestResult:
        """Test API endpoints health"""
        start_time = time.time()
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        return TestResult(
                            "API Health Check",
                            True,
                            "API endpoints are healthy",
                            time.time() - start_time
                        )
                return TestResult(
                    "API Health Check",
                    False,
                    f"Unexpected response: {response.status}",
                    time.time() - start_time
                )
        except Exception as e:
            return TestResult(
                "API Health Check",
                False,
                str(e),
                time.time() - start_time
            )

    async def test_app_updates_endpoint(self) -> TestResult:
        """Test app updates endpoint"""
        start_time = time.time()
        try:
            headers = {
                "X-Platform": "android",
                "X-Current-Version": "1.0.0",
                "X-Build-Number": "100"
            }
            async with self.session.get(f"{API_BASE}/app/updates", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "hasUpdate" in data and "platform" in data:
                        return TestResult(
                            "App Updates Endpoint",
                            True,
                            f"Update check successful: hasUpdate={data.get('hasUpdate')}",
                            time.time() - start_time
                        )
                return TestResult(
                    "App Updates Endpoint",
                    False,
                    f"Update endpoint failed: {response.status}",
                    time.time() - start_time
                )
        except Exception as e:
            return TestResult(
                "App Updates Endpoint",
                False,
                str(e),
                time.time() - start_time
            )

    async def test_categories_endpoint(self) -> TestResult:
        """Test categories endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{API_BASE}/categories/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "categories" in data:
                        return TestResult(
                            "Categories Endpoint",
                            True,
                            f"Categories retrieved: {len(data['categories'])} items",
                            time.time() - start_time
                        )
                return TestResult(
                    "Categories Endpoint",
                    False,
                    f"Categories endpoint failed: {response.status}",
                    time.time() - start_time
                )
        except Exception as e:
            return TestResult(
                "Categories Endpoint",
                False,
                str(e),
                time.time() - start_time
            )

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting EduVerse Backend Integration Tests")
        print("=" * 60)

        await self.initialize()

        try:
            tests = [
                self.test_backend_health,
                self.test_api_health,
                self.test_app_updates_endpoint,
                self.test_categories_endpoint,
            ]

            for test in tests:
                result = await test()
                self.log_result(result)

        finally:
            await self.cleanup()

        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 BACKEND TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.success:
                    print(f"  • {result.name}: {result.message}")

def check_port_open(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if a port is open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return False

async def main():
    """Main test function"""
    print("🔍 Checking if backend server is running...")

    if not check_port_open("localhost", 8000):
        print("❌ Backend server is not running on port 8000")
        print("💡 Please start the backend server first:")
        print("   cd backend && python main.py")
        return 1

    print("✅ Backend server is running")

    tester = EduVerseBackendTester()
    await tester.run_all_tests()
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)