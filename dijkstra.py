"""I've got this code from https://gist.github.com/kachayev/5990802"""

from collections import defaultdict
from heapq import *


def dijkstra(edges, f, t):
    g = defaultdict(list)
    for l, r, c in edges:
        g[l].append((c, r))

    q, seen = [(0, f, ())], set()
    while q:
        (cost, v1, path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t:
                return cost, path

            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost+c, v2, path))

    return float("inf")

if __name__ == '__main__':
    edges = [
        (1, 2, 7),
        (2, 1, 7),
        (1, 3, 9),
        (3, 1, 9),
        (1, 6, 14),
        (6, 1, 14),
        (2, 3, 10),
        (3, 2, 10),
        (2, 4, 15),
        (4, 2, 15),
        (3, 4, 11),
        (4, 3, 11),
        (3, 6, 2),
        (6, 3, 2),
        (4, 5, 6),
        (5, 4, 6),
        (5, 6, 9),
        (6, 5, 9)
    ]

    print(dijkstra(edges, 1, 5))
