class UnionFind:
    """
    Union-Find (Disjoint Set Union) data structure.
    It maintains a collection of disjoint sets and supports:
    1. Finding which set an element belongs to.
    2. Merging two sets together.
    """

    def __init__(self, elements):
        """
        Initially, every element is in its own set.
        """

        # parent[x] stores the parent of x.
        # Initially, every element is its own parent.
        self.parent = {}
        # rank[x] helps us keep the tree shallow.
        self.rank = {}

        for element in elements:
            self.parent[element] = element
            self.rank[element] = 0

    def find(self, element):
        """
        Find the representative (root) of the set
        containing 'element'.

        Path compression is used to make future searches faster.
        """

        # If element is not its own parent, move upward.
        if self.parent[element] != element:
            self.parent[element] = self.find(self.parent[element])

        return self.parent[element]

    def union(self, element1, element2):
        """
        Merge the sets containing element1 and element2.

        Union by rank is used to keep the tree shallow.
        """

        root1 = self.find(element1)
        root2 = self.find(element2)

        # They are already in the same set.
        if root1 == root2:
            return

        # Attach the smaller-rank tree under the larger-rank tree.
        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2

        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1

        else:
            # Same rank: choose root1 as the new root.
            self.parent[root2] = root1

            # Increase the rank of the new root.
            self.rank[root1] += 1

    def get_clusters(self):
        """
        Return all elements grouped into their disjoint sets.

        Example result:

        {
            1: [1, 3],
            2: [2, 4, 5]
        }
        """

        clusters = {}

        for element in self.parent:
            root = self.find(element)

            if root not in clusters:
                clusters[root] = []

            clusters[root].append(element)

        return clusters
