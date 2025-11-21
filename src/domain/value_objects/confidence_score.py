class ConfidenceScore:
    MINIMUM_SCORE = 0.0
    MAXIMUM_SCORE = 1.0

    def __init__(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Confianza debe ser un número")
        if value < self.MINIMUM_SCORE or value > self.MAXIMUM_SCORE:
            raise ValueError(f"Confianza debe estar entre {self.MINIMUM_SCORE} y {self.MAXIMUM_SCORE}")
        self._value = float(value)

    @property
    def value(self) -> float:
        return self._value

    def is_high(self) -> bool:
        return self._value >= 0.8

    def is_medium(self) -> bool:
        return 0.5 <= self._value < 0.8

    def is_low(self) -> bool:
        return self._value < 0.5

    def __eq__(self, other):
        if not isinstance(other, ConfidenceScore):
            return False
        return abs(self._value - other._value) < 0.001

    def __str__(self):
        return f"{self._value:.3f}"