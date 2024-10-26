from typing import Tuple, Any
import hashlib
import time


class PredictionCache:

    def __init__(self, ttl: int):
        self.ttl = ttl
        self.cache = {}

    def _generate_key(self, features: Tuple) -> str:
        features_str = str(features)
        return hashlib.md5(features_str.encode()).hexdigest()

    def get(self, features: Tuple) -> Tuple[bool, Any]:
        key = self._generate_key(features)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp <= self.ttl:
                return True, result
            del self.cache[key]
        return False, None

    def set(self, features: Tuple, result: Any):
        key = self._generate_key(features)
        self.cache[key] = (result, time.time())
