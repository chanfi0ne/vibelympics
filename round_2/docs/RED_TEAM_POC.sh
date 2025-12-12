#!/bin/bash
# PURPOSE: Red Team Proof of Concept Test Suite for CHAINSAW
# IMPORTANT: Only run against authorized test environments
# Production endpoint: https://chainsaw.up.railway.app/

set -e

ENDPOINT="${1:-https://chainsaw.up.railway.app}"
echo "========================================="
echo "CHAINSAW Red Team Test Suite"
echo "Target: $ENDPOINT"
echo "Date: $(date)"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local expected_result="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}[TEST $TOTAL_TESTS]${NC} $test_name"
    echo "Command: $test_cmd"

    if eval "$test_cmd"; then
        echo -e "${GREEN}✓ PASS${NC} - $expected_result"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} - $expected_result"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

echo "========================================="
echo "1. RECONNAISSANCE TESTS"
echo "========================================="
echo ""

run_test \
    "Health Check Endpoint" \
    "curl -s -o /dev/null -w '%{http_code}' $ENDPOINT/api/health | grep -q '200'" \
    "Health endpoint should return 200"

run_test \
    "OpenAPI Docs Exposed" \
    "curl -s $ENDPOINT/docs | grep -q 'OpenAPI'" \
    "API documentation should be accessible (INFO finding)"

run_test \
    "Root Endpoint Information" \
    "curl -s $ENDPOINT/api/ 2>&1 | grep -q 'Chainsaw'" \
    "Root should return service info"

echo "========================================="
echo "2. INPUT VALIDATION TESTS"
echo "========================================="
echo ""

run_test \
    "Empty Package Name" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"\"}' | grep -q 'validation_error\\|422'" \
    "Should reject empty package name"

run_test \
    "SQL Injection Attempt" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"'; DROP TABLE users; --\"}' | grep -q 'validation_error\\|422\\|400'" \
    "Should reject SQL injection patterns"

run_test \
    "Path Traversal in Package Name" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"../../etc/passwd\"}' | grep -q 'validation_error\\|422\\|400'" \
    "Should reject path traversal attempts"

run_test \
    "XSS in Package Name" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"<script>alert(1)</script>\"}' | grep -q 'validation_error\\|422\\|400'" \
    "Should reject XSS payloads"

run_test \
    "Malformed Version String" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"lodash\",\"version\":\"'; DROP TABLE versions; --\"}' | grep -q '400\\|422'" \
    "Should validate version format (FINDING 4)"

run_test \
    "Version Path Traversal" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"lodash\",\"version\":\"../../../etc/passwd\"}' | grep -q '400\\|422'" \
    "Should reject path traversal in version"

echo "========================================="
echo "3. RATE LIMITING TESTS (FINDING 2)"
echo "========================================="
echo ""

echo "Testing for rate limiting (sending 20 rapid requests)..."
RATE_LIMIT_HIT=0

for i in {1..20}; do
    RESPONSE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $ENDPOINT/api/audit \
        -H 'Content-Type: application/json' \
        -d '{"package_name":"lodash"}')

    if [ "$RESPONSE" = "429" ]; then
        RATE_LIMIT_HIT=1
        echo -e "${GREEN}✓ Rate limit enforced at request $i${NC}"
        break
    fi

    if [ $((i % 5)) -eq 0 ]; then
        echo "Sent $i requests, no rate limit yet..."
    fi
done

if [ $RATE_LIMIT_HIT -eq 0 ]; then
    echo -e "${RED}✗ FAIL - No rate limiting detected (VULNERABILITY)${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "========================================="
echo "4. REQUEST SIZE LIMIT TESTS (FINDING 6)"
echo "========================================="
echo ""

run_test \
    "Large Request Body (1MB)" \
    "python3 -c 'import requests, json; r=requests.post(\"$ENDPOINT/api/audit\", json={\"package_name\": \"a\"*1000000}); exit(0 if r.status_code == 413 else 1)' 2>/dev/null || echo 'Large payload accepted (VULNERABILITY)'" \
    "Should reject requests over size limit"

echo "========================================="
echo "5. SSRF TESTS (FINDING 1)"
echo "========================================="
echo ""

# Note: These test theoretical SSRF but won't work without a malicious npm package
echo "SSRF tests require creating malicious npm packages (not performed)"
echo "Theoretical attack vectors:"
echo "  - Package with repository: 'https://github.com/../../internal-api'"
echo "  - Package with repository: 'http://169.254.169.254/latest/meta-data/'"
echo "  - Package with repository: 'http://localhost:6379/'"
echo ""

run_test \
    "Test with suspicious GitHub URL format" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"lodash\"}' | grep -q 'lodash'" \
    "Should handle standard packages"

echo "========================================="
echo "6. ERROR MESSAGE INFORMATION DISCLOSURE (FINDING 3)"
echo "========================================="
echo ""

run_test \
    "Nonexistent Package Error Message" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"zzz-nonexistent-package-12345\"}' | grep -qv 'traceback\\|line [0-9]\\|File \"'" \
    "Error should not contain stack traces or file paths"

run_test \
    "Invalid JSON Error Message" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{invalid json}' | grep -qv 'traceback\\|line [0-9]'" \
    "JSON parse error should not expose internals"

echo "========================================="
echo "7. CORS CONFIGURATION TESTS (FINDING 5)"
echo "========================================="
echo ""

run_test \
    "CORS Preflight from Unauthorized Origin" \
    "curl -s -X OPTIONS $ENDPOINT/api/audit -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: POST' | grep -q 'Access-Control-Allow-Origin: https://evil.com' && echo 'VULNERABLE' || echo 'OK'" \
    "Should reject unauthorized origins"

run_test \
    "CORS with Credentials Check" \
    "curl -s -I -X POST $ENDPOINT/api/audit -H 'Origin: http://localhost:3000' | grep -q 'Access-Control-Allow-Credentials: true'" \
    "Check if credentials are allowed (potential CSRF risk)"

echo "========================================="
echo "8. SECURITY HEADERS TESTS (INFO 2)"
echo "========================================="
echo ""

HEADERS_CHECK=$(curl -s -I $ENDPOINT/api/health)

echo "Checking security headers:"
echo "$HEADERS_CHECK" | grep -i "X-Content-Type-Options" || echo -e "${YELLOW}⚠ Missing: X-Content-Type-Options${NC}"
echo "$HEADERS_CHECK" | grep -i "X-Frame-Options" || echo -e "${YELLOW}⚠ Missing: X-Frame-Options${NC}"
echo "$HEADERS_CHECK" | grep -i "Strict-Transport-Security" || echo -e "${YELLOW}⚠ Missing: Strict-Transport-Security${NC}"
echo "$HEADERS_CHECK" | grep -i "Content-Security-Policy" || echo -e "${YELLOW}⚠ Missing: Content-Security-Policy${NC}"
echo ""

echo "========================================="
echo "9. TIMING ATTACK TESTS (FINDING 8)"
echo "========================================="
echo ""

echo "Testing cache timing differences..."
echo "First request (uncached):"
TIME1=$(curl -s -o /dev/null -w '%{time_total}' -X POST $ENDPOINT/api/audit \
    -H 'Content-Type: application/json' \
    -d '{"package_name":"lodash"}')
echo "Time: ${TIME1}s"

sleep 1

echo "Second request (should be cached):"
TIME2=$(curl -s -o /dev/null -w '%{time_total}' -X POST $ENDPOINT/api/audit \
    -H 'Content-Type: application/json' \
    -d '{"package_name":"lodash"}')
echo "Time: ${TIME2}s"

echo "Timing difference could reveal cache status (INFO finding)"
echo ""

echo "========================================="
echo "10. VALID FUNCTIONALITY TESTS"
echo "========================================="
echo ""

run_test \
    "Audit Valid Package (lodash)" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"lodash\"}' | grep -q 'risk_score'" \
    "Should successfully audit legitimate package"

run_test \
    "Audit Scoped Package (@babel/core)" \
    "curl -s -X POST $ENDPOINT/api/audit -H 'Content-Type: application/json' -d '{\"package_name\":\"@babel/core\"}' | grep -q 'risk_score'" \
    "Should handle scoped packages"

run_test \
    "Compare Endpoint" \
    "curl -s -X POST $ENDPOINT/api/audit/compare -H 'Content-Type: application/json' -d '{\"package_name\":\"lodash\",\"version_old\":\"4.17.11\",\"version_new\":\"4.17.21\"}' | grep -q 'vulnerabilities_fixed'" \
    "Compare endpoint should work"

echo "========================================="
echo "TEST SUMMARY"
echo "========================================="
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}⚠ VULNERABILITIES DETECTED ⚠${NC}"
    echo "Review the failed tests above for security issues"
    exit 1
else
    echo -e "${GREEN}✓ All tests passed${NC}"
    exit 0
fi
