class ClusterLabel:
    PRODUCTIVO_A = "PRODUCTIVO_A"
    PRODUCTIVO_B = "PRODUCTIVO_B"
    PRODUCTIVO_C = "PRODUCTIVO_C"
    REPRO_OPTIMO = "REPRO_OPTIMO"
    REPRO_PROBLEMA = "REPRO_PROBLEMA"
    PENDING = "PENDING"

    VALID_LABELS = [
        PRODUCTIVO_A,
        PRODUCTIVO_B,
        PRODUCTIVO_C,
        REPRO_OPTIMO,
        REPRO_PROBLEMA,
        PENDING
    ]

    def __init__(self, value: str):
        if value not in self.VALID_LABELS:
            raise ValueError(f"ClusterLabel inválido: {value}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, ClusterLabel):
            return False
        return self._value == other._value

    def __str__(self):
        return self._value