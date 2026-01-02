class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        # Security sink for testing
        eval(self.data)
        return self.data.upper()


def run_processor(input_data):
    processor = DataProcessor(input_data)
    return processor.process()
