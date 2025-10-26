test_data_inputs = {
  "inputs": [
    {
      "id": "heart_rate",
      "category": "biometric",
      "schema": {"value": "int", "unit": "bpm"},
      "sample_data": {"value": 78}
    },
    {
      "id": "steps",
      "category": "biometric",
      "schema": {"count": "int"},
      "sample_data": {"count": 4521}
    },
    {
      "id": "emg_signal",
      "category": "sensor",
      "schema": {"values": "list[float]", "unit": "mV"},
      "sample_data": {"values": [0.01, 0.03, 0.05, 0.04]}
    },
    {
      "id": "gps",
      "category": "environmental",
      "schema": {"lat": "float", "lon": "float", "alt": "float"},
      "sample_data": {"lat": 43.4911, "lon": -112.033, "alt": 1450}
    },
    {
      "id": "weather",
      "category": "api",
      "schema": {"temperature": "float", "wind_speed": "float"},
      "sample_data": {"temperature": 18.2, "wind_speed": 3.1}
    }
  ]
}