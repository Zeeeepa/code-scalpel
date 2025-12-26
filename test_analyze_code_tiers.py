#!/usr/bin/env python3
"""
Test script for tiered analyze_code functionality - runs each tier in subprocess.

Tests that analyze_code returns different results based on CODE_SCALPEL_TIER:
- COMMUNITY: cognitive_complexity=0, code_smells=[]
- PRO: cognitive_complexity>0, code_smells populated
- ENTERPRISE: All features enabled
"""

import os
import subprocess
import sys

# Test code with complexity and smells
TEST_CODE_CONTENT = '''
def complex_function(a, b, c, d, e, f, g):
    """This function has too many parameters and is too long"""
    result = 0
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = a + b + c + d + e
                    else:
                        result = a + b + c + d
                else:
                    result = a + b + c
            else:
                result = a + b
        else:
            result = a
    else:
        result = 0
    
    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    
    while result > 100:
        result = result // 2
        if result < 50:
            break
    
    return result

class GodClass:
    """This class has way too many methods"""
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
'''


def test_tier(tier_name: str):
    """Run test in subprocess to ensure clean environment."""
    print(f"\n{'='*60}")
    print(f"Testing tier: {tier_name.upper()}")
    print(f"{'='*60}")
    
    # Build test code  - use repr() to safely embed the test code
    test_code = f'''
import sys
import os
os.environ["CODE_SCALPEL_TIER"] = "{tier_name}"
os.environ["SCALPEL_NO_CACHE"] = "1"

TEST_CODE = {repr(TEST_CODE_CONTENT.strip())}

from code_scalpel.mcp.server import _analyze_code_sync

result = _analyze_code_sync(TEST_CODE, "python")

print(f"Success: {{result.success}}")
print(f"Functions found: {{result.function_count}}")
print(f"Classes found: {{result.class_count}}")
print(f"Cyclomatic complexity: {{result.complexity}}")
print(f"Cognitive complexity: {{result.cognitive_complexity}}")
print(f"Code smells: {{len(result.code_smells)}}")

if result.code_smells:
    print("\\nDetected code smells:")
    for smell in result.code_smells:
        print(f"  - {{smell}}")

# Verify expectations
if "{tier_name}" == "community":
    assert result.cognitive_complexity == 0, "COMMUNITY tier should have cognitive_complexity=0"
    assert len(result.code_smells) == 0, "COMMUNITY tier should have no code smells"
    print("\\n✅ COMMUNITY tier: Basic features only (as expected)")
elif "{tier_name}" == "pro":
    assert result.cognitive_complexity > 0, f"PRO tier should compute cognitive_complexity, got {{result.cognitive_complexity}}"
    assert len(result.code_smells) > 0, f"PRO tier should detect code smells, got {{len(result.code_smells)}}"
    print(f"\\n✅ PRO tier: Advanced features enabled (cognitive={{result.cognitive_complexity}}, smells={{len(result.code_smells)}})")
elif "{tier_name}" == "enterprise":
    assert result.cognitive_complexity > 0, f"ENTERPRISE tier should compute cognitive_complexity, got {{result.cognitive_complexity}}"
    assert len(result.code_smells) > 0, f"ENTERPRISE tier should detect code smells, got {{len(result.code_smells)}}"
    print(f"\\n✅ ENTERPRISE tier: All features enabled (cognitive={{result.cognitive_complexity}}, smells={{len(result.code_smells)}})")
'''
    
    # Run in subprocess
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Only print warnings/errors, not DEBUG
        for line in result.stderr.splitlines():
            if "WARNING" in line or "ERROR" in line or "Traceback" in line:
                print(line, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"\n❌ Test failed with exit code {result.returncode}")
        if result.stderr:
            print("\nFull stderr:")
            print(result.stderr)
        return False
    
    return True


def main():
    """Run tests for all tiers."""
    print("Testing analyze_code tier-based features")
    print(f"Python: {sys.version}")
    
    try:
        # Test each tier in subprocess
        success = True
        success &= test_tier("community")
        success &= test_tier("pro")
        success &= test_tier("enterprise")
        
        if success:
            print(f"\n{'='*60}")
            print("✅ All tests passed!")
            print(f"{'='*60}\n")
            return 0
        else:
            return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
