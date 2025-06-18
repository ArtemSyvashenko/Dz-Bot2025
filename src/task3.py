from collections import OrderedDict
import time

class Memoize:
    def __init__(self, func, max_size=100, strategy="lru"):
        self.func = func
        self.max_size = max_size
        self.strategy = strategy
        self.cache = OrderedDict()
        self.freq = {}

    def __call__(self, *args):
        if args in self.cache:
            if self.strategy == "lru":
                self.cache.move_to_end(args)
            elif self.strategy == "lfu":
                self.freq[args] += 1
            return self.cache[args]

        result = self.func(*args)
        if len(self.cache) >= self.max_size:
            self.evict()
        self.cache[args] = result
        if self.strategy == "lfu":
            self.freq[args] = 1
        return result

    def evict(self):
        if self.strategy == "lru":
            self.cache.popitem(last=False)
        elif self.strategy == "lfu":
            least_used = min(self.freq.items(), key=lambda x: x[1])[0]
            self.cache.pop(least_used)
            self.freq.pop(least_used)
        else:
            self.cache.popitem(last=False)