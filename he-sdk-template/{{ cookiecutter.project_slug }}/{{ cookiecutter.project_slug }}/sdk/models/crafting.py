from .cost import Cost
from .reward import Reward


class CraftRule(object):
    def __init__(self, name: str):
        self._name = name
        self._reward = Reward()
        self._cost = Cost()

    @property
    def name(self) -> str:
        return self._name

    @property
    def reward(self) -> Reward:
        return self._reward

    @property
    def cost(self) -> Cost:
        return self._cost

    def require(self, item, amount: int = 1):
        return self._cost.add(item, amount)

    def produce(self, item, amount: int = 1):
        return self._reward.add(item, amount)

    def to_dict(self):
        return dict(
            Name=self._name,
            Reward=self._reward.to_dict(),
            Cost=self._cost.to_dict()
        )
