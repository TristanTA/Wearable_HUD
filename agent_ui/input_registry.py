class InputRegistry:
    def __init__(self, input_id: str, category: str, schema: dict, sample_data: dict):
        self.input_id: str = input_id or "NA"
        self.category: str = category or "NA"
        self.schema: dict = schema or {}
        self.sample_data: dict = sample_data or {}

    def get(self):
        return {
            "Input ID": self.input_id,
            "Category": self.category,
            "Schema": self.schema,
            "Sample Data": self.sample_data
        }
    

class RegistryManager:
    def __init__(self, input_data: dict):
        self.registry = []
        for entry in input_data.get("inputs", []):
            self.registry.append(
                InputRegistry(
                    input_id=entry.get("id"),
                    category=entry.get("category"),
                    schema=entry.get("schema"),
                    sample_data=entry.get("sample_data")
                )
            )

    def list_inputs(self):
        return [inp.input_id for inp in self.registry]

    def get_input(self, input_id: str) -> dict:
        for inp in self.registry:
            if inp.input_id == input_id:
                return inp.get()
        return {"error": f"Input '{input_id}' not found."}