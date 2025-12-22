#!/usr/bin/env python3
"""
Polyglot Extraction Demo - Multi-language support showcase.

[20251221_FEATURE] Demonstrates Java, JavaScript, and TypeScript extraction
capabilities in addition to Python.

This example shows how Code Scalpel can surgically extract code from any
supported language using the same unified API.
"""

from code_scalpel.polyglot_extractor import PolyglotExtractor


def demo_java_extraction():
    """Demo 1: Extract Java methods and classes."""
    print("=" * 70)
    print("DEMO 1: Java Extraction")
    print("=" * 70)

    java_code = """
public class Calculator {
    /**
     * Calculate tax on a given amount.
     * @param amount The base amount
     * @param rate The tax rate
     * @return The tax amount
     */
    public double calculateTax(double amount, double rate) {
        return amount * rate;
    }

    public double add(double a, double b) {
        return a + b;
    }

    public double multiply(double a, double b) {
        return a * b;
    }
}
"""

    extractor = PolyglotExtractor(java_code, language="java")

    print(f"✓ Detected language: {extractor.language}")
    print(
        f"✓ Found {len(extractor.list_functions())} methods: {extractor.list_functions()}"
    )
    print(f"✓ Found {len(extractor.list_classes())} class: {extractor.list_classes()}")

    # Extract specific method
    result = extractor.get_function("calculateTax")
    print("\n✓ Extracted method 'calculateTax':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print(f"  Code length: {len(result.code)} chars")
    print("\n" + result.code)


def demo_javascript_extraction():
    """Demo 2: Extract JavaScript functions and classes."""
    print("\n" + "=" * 70)
    print("DEMO 2: JavaScript Extraction")
    print("=" * 70)

    js_code = """
// Payment processing functions
function processPayment(amount, cardNumber) {
    const tax = calculateTax(amount);
    const total = amount + tax;
    return {
        subtotal: amount,
        tax: tax,
        total: total
    };
}

async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    return await response.json();
}

// Arrow function
const validateCard = (cardNumber) => {
    return cardNumber.length === 16;
};

class PaymentProcessor {
    constructor(apiKey) {
        this.apiKey = apiKey;
    }

    charge(amount) {
        console.log(`Charging ${amount}`);
        return true;
    }
}
"""

    extractor = PolyglotExtractor(js_code, language="javascript")

    print(f"✓ Detected language: {extractor.language}")
    print(
        f"✓ Found {len(extractor.list_functions())} functions: {extractor.list_functions()}"
    )
    print(f"✓ Found {len(extractor.list_classes())} class: {extractor.list_classes()}")

    # Extract async function
    result = extractor.get_function("fetchUserData")
    print("\n✓ Extracted async function 'fetchUserData':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print(f"  Success: {result.success}")
    print("\n" + result.code)

    # Extract arrow function
    result = extractor.get_function("validateCard")
    print("\n✓ Extracted arrow function 'validateCard':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print("\n" + result.code)


def demo_typescript_extraction():
    """Demo 3: Extract TypeScript functions with type annotations."""
    print("\n" + "=" * 70)
    print("DEMO 3: TypeScript Extraction")
    print("=" * 70)

    ts_code = """
interface User {
    id: number;
    name: string;
    email: string;
}

interface PaymentResult {
    success: boolean;
    transactionId: string;
    amount: number;
}

function calculateTax(amount: number, rate: number = 0.1): number {
    return amount * rate;
}

async function processPayment(
    user: User,
    amount: number
): Promise<PaymentResult> {
    const tax = calculateTax(amount);
    const total = amount + tax;
    
    // Process payment logic here
    return {
        success: true,
        transactionId: generateId(),
        amount: total
    };
}

const formatCurrency = (amount: number): string => {
    return `$${amount.toFixed(2)}`;
};

class PaymentService {
    private apiKey: string;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }

    async charge(amount: number): Promise<boolean> {
        console.log(`Charging ${amount}`);
        return true;
    }
}
"""

    extractor = PolyglotExtractor(ts_code, language="typescript")

    print(f"✓ Detected language: {extractor.language}")
    print(
        f"✓ Found {len(extractor.list_functions())} functions: {extractor.list_functions()}"
    )
    print(f"✓ Found {len(extractor.list_classes())} class: {extractor.list_classes()}")

    # Extract typed async function
    result = extractor.get_function("processPayment")
    print("\n✓ Extracted TypeScript async function 'processPayment':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print(f"  Code length: {len(result.code)} chars")
    print("\n" + result.code)

    # Extract class
    result = extractor.get_class("PaymentService")
    print("\n✓ Extracted TypeScript class 'PaymentService':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print(f"  Code length: {len(result.code)} chars")


def demo_python_extraction():
    """Demo 4: Python extraction (for comparison)."""
    print("\n" + "=" * 70)
    print("DEMO 4: Python Extraction (Baseline)")
    print("=" * 70)

    python_code = """
def calculate_tax(amount: float, rate: float = 0.1) -> float:
    '''
    Calculate tax on a given amount.
    
    Args:
        amount: The base amount
        rate: The tax rate (default: 0.1)
    
    Returns:
        The tax amount
    '''
    return amount * rate

async def process_payment(user_id: int, amount: float) -> dict:
    '''Process a payment asynchronously.'''
    tax = calculate_tax(amount)
    total = amount + tax
    
    return {
        'subtotal': amount,
        'tax': tax,
        'total': total
    }

class PaymentProcessor:
    '''Payment processing service.'''
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def charge(self, amount: float) -> bool:
        '''Charge a payment.'''
        print(f'Charging {amount}')
        return True
"""

    extractor = PolyglotExtractor(python_code, language="python")

    print(f"✓ Detected language: {extractor.language}")
    print(
        f"✓ Found {len(extractor.list_functions())} functions: {extractor.list_functions()}"
    )
    print(f"✓ Found {len(extractor.list_classes())} class: {extractor.list_classes()}")

    # Extract function
    result = extractor.get_function("calculate_tax")
    print("\n✓ Extracted Python function 'calculate_tax':")
    print(f"  Lines: {result.line_start}-{result.line_end}")
    print(
        f"  Docstring: {result.docstring[:50]}..."
        if result.docstring
        else "  Docstring: None"
    )
    print(
        f"  Signature: {result.signature}" if result.signature else "  Signature: None"
    )
    print("\n" + result.code[:200] + "...")


def demo_auto_detection():
    """Demo 5: Auto-detect language from file extension or content."""
    print("\n" + "=" * 70)
    print("DEMO 5: Automatic Language Detection")
    print("=" * 70)

    # Example 1: Detect from content (Java)
    java_snippet = "public class Test { public void run() {} }"
    extractor = PolyglotExtractor(java_snippet)
    print(f"✓ Auto-detected Java from content: {extractor.language}")

    # Example 2: Detect from content (TypeScript)
    ts_snippet = "const add = (a: number, b: number): number => a + b;"
    extractor = PolyglotExtractor(ts_snippet)
    print(f"✓ Auto-detected TypeScript from content: {extractor.language}")

    # Example 3: Detect from content (Python)
    py_snippet = "def hello():\n    print('hello')"
    extractor = PolyglotExtractor(py_snippet)
    print(f"✓ Auto-detected Python from content: {extractor.language}")

    # Example 4: Detect from file extension
    print("\n✓ Language detection from file extensions:")
    extensions = {
        "app.py": "python",
        "utils.js": "javascript",
        "service.ts": "typescript",
        "Calculator.java": "java",
    }
    for filename, expected in extensions.items():
        # Simulate file path detection
        extractor = PolyglotExtractor("# dummy", file_path=filename)
        detected = extractor.language
        status = "✓" if detected == expected else "✗"
        print(f"  {status} {filename:20s} → {detected}")


def demo_error_handling():
    """Demo 6: Error handling for non-existent symbols."""
    print("\n" + "=" * 70)
    print("DEMO 6: Error Handling")
    print("=" * 70)

    js_code = "function hello() { return 'world'; }"
    extractor = PolyglotExtractor(js_code, language="javascript")

    # Try to extract non-existent function
    result = extractor.get_function("goodbye")
    print("✓ Attempted to extract non-existent function:")
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    # List available functions
    available = extractor.list_functions()
    print(f"\n✓ Available functions: {available}")


def demo_unified_api():
    """Demo 7: Show unified API works across all languages."""
    print("\n" + "=" * 70)
    print("DEMO 7: Unified API Across Languages")
    print("=" * 70)

    # Same API, different languages
    examples = [
        ("python", "def test(): pass", "test"),
        ("java", "public class Test { void run() {} }", "run"),
        ("javascript", "function hello() {}", "hello"),
        ("typescript", "const add = (a: number) => a", "add"),
    ]

    print("✓ Using identical API for all languages:")
    for lang, code, func_name in examples:
        extractor = PolyglotExtractor(code, language=lang)
        result = extractor.get_function(func_name)
        status = "✓" if result.success else "✗"
        print(
            f"  {status} {lang:12s} - extracted '{func_name}' (lines {result.line_start}-{result.line_end})"
        )


def main():
    """Run all polyglot extraction demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + " POLYGLOT EXTRACTION DEMO - Multi-Language Support ".center(68) + "║")
    print("║" + " Code Scalpel v3.1.0 ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    demo_java_extraction()
    demo_javascript_extraction()
    demo_typescript_extraction()
    demo_python_extraction()
    demo_auto_detection()
    demo_error_handling()
    demo_unified_api()

    print("\n" + "=" * 70)
    print("✓ All demos completed successfully!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  • Same API works for Python, Java, JavaScript, and TypeScript")
    print("  • Auto-detection from file extensions or code content")
    print("  • Surgical extraction preserves exact code structure")
    print("  • Error handling with helpful messages")
    print("  • Line number tracking across all languages")
    print("\nNext Steps:")
    print("  • Try with your own code files")
    print("  • Integrate with your AI workflow")
    print("  • Explore cross-file dependency analysis")
    print()


if __name__ == "__main__":
    main()
