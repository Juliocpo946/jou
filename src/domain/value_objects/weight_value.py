class WeightValue:
    MINIMUM_WEIGHT_KG = 5.0
    MAXIMUM_WEIGHT_KG = 1500.0

    def __init__(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Peso debe ser un número")
        if value < self.MINIMUM_WEIGHT_KG or value > self.MAXIMUM_WEIGHT_KG:
            raise ValueError(f"Peso debe estar entre {self.MINIMUM_WEIGHT_KG} y {self.MAXIMUM_WEIGHT_KG} kg")
        self._value = float(value)

    @property
    def value(self) -> float:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, WeightValue):
            return False
        return abs(self._value - other._value) < 0.01

    def __lt__(self, other):
        if not isinstance(other, WeightValue):
            return NotImplemented
        return self._value < other._value

    def __gt__(self, other):
        if not isinstance(other, WeightValue):
            return NotImplemented
        return self._value > other._value

    def __str__(self):
        return f"{self._value:.2f} kg"