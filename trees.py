class PriorityQueue(object):
    def __init__(self, compare=lambda a, b: a < b):
        self.heap = []
        self.set = set()
        self.compare = compare

    def __len__(self):
        return len(self.heap)
    def __repr__(self):
        return str(self.heap)
    def __contains__(self, item):
        return item in self.set

    def push(self, item):
        self.heap.append(item)
        self.set.add(item)

        self.__bubble(len(self) - 1)

    def update(self, item):
        index = self.heap.index(item)
        self.__bubble(index)

    def pop(self):
        set = self.set
        heap = self.heap
        compare = self.compare

        size = len(self) - 1

        if not size:
            first = heap.pop()
        else:
            first = heap.pop(0)
            last = heap.pop()

            heap.insert(0, last)
            self.__drip(0)

        set.remove(first)
        return first

    def peek(self):
        return self.heap[0]
    def empty(self):
        return len(self) == 0

    def __bubble(self, index):
        heap = self.heap
        compare = self.compare

        child = index
        parent = (child - 1) / 2

        while child and compare(heap[child], heap[parent]):
            heap[child], heap[parent] = heap[parent], heap[child]
            child, parent = parent, (parent - 1)/2

    def __drip(self, index):
        heap = self.heap
        compare = self.compare

        get_parent_child = lambda parent: (parent, 2 * parent + 1)
        parent, child = get_parent_child(index)

        size = len(self) - 1

        while child < size:
            if (child < size - 1) and compare(heap[child + 1], heap[child]):
                child += 1

            if compare(heap[child], heap[parent]):
                heap[child], heap[parent] = heap[parent], heap[child]
                parent, child = get_parent_child(child)
            else:
                break

class IndexedPQ(PriorityQueue):
    def __init__(self, weights, compare=lambda a, b: a < b):
        PriorityQueue.__init__(self, self.__compare)
        self.weights = weights
        self.naive_compare = compare

    def __compare(self, a, b):
        weights = self.weights
        compare = self.naive_compare
        return compare(weights[a], weights[b])

if __name__ == "__main__":

    from random import shuffle

    def test_range():
        queue = PriorityQueue()

        values = range(1000)
        values.reverse()

        # Fill the queue...
        for value in values:
            queue.push(value)

        # ...then empty it.
        # Note that pop() removes from the end of lists.
        while queue:
            assert queue.pop() == values.pop()

    def test_months():
        values = range(12)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        weights = dict(zip(months, values))
        queue = IndexedPQ(weights)

        months.reverse()
        for month in months:
            queue.push(month)

        while queue:
            assert queue.pop() == months.pop()

    test_range()
    test_months()

    print "All tests passed."
