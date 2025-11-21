from uuid import UUID

class AnimalId:
    def __init__(self, value: UUID):
        if not isinstance(value, UUID):
            raise ValueError("AnimalId debe ser un UUID válido")
        self._value = value

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, AnimalId):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __str__(self):
        return str(self._value)