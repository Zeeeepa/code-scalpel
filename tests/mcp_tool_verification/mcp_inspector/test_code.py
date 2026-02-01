def process_item(x):
    """Process numeric data."""
    return x * 2

def process_item(y):
    """Process item data."""
    return y + 1

def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def calculate_product(x, y):
    """Calculate product of two numbers."""
    return x * y

class DataProcessor:
    """Process various data types."""

    def __init__(self, name):
        self.name = name

    def execute(self, data):
        """Execute processing."""
        return process_item(data)

def main():
    """Main entry point."""
    result = process_item(5)
    return result