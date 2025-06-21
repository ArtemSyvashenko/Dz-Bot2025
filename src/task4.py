# --- Queue implementation ---

from collections import deque

class BiPriorityQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, item, priority):
        self.queue.append({'item': item, 'priority': priority})

    def dequeue(self, mode='highest'):
        if not self.queue:
            return None

        if mode == 'highest':
            return self._pop_by_priority(max)
        elif mode == 'lowest':
            return self._pop_by_priority(min)
        elif mode == 'oldest':
            return self.queue.popleft()['item']
        elif mode == 'newest':
            return self.queue.pop()['item']

    def peek(self, mode='highest'):
        if not self.queue:
            return None

        if mode == 'highest':
            return self._find_by_priority(max)
        elif mode == 'lowest':
            return self._find_by_priority(min)
        elif mode == 'oldest':
            return self.queue[0]['item']
        elif mode == 'newest':
            return self.queue[-1]['item']

    def _find_by_priority(self, func):
        best = func(self.queue, key=lambda x: x['priority'])
        return best['item']

    def _pop_by_priority(self, func):
        index = 0
        best_priority = self.queue[0]['priority']
        for i, obj in enumerate(self.queue):
            if func(obj['priority'], best_priority) == obj['priority']:
                best_priority = obj['priority']
                index = i
        return self.queue.pop(index)['item']
