"""
🧩题目：冗余连接（Redundant Connection）
题目描述：
树是一个连通且无环的无向图。给出一个包含 n 个节点的图（从 1 到 n 编号），它原本是一棵树，但多加了一条边，导致图中产生了一个环。

请你找出这条冗余的边并将其移除，使图重新变成一棵树。如果有多个答案，返回输入中最后出现的那一条边。


输入: edges = [[1,2],[1,3],[2,3]]
输出: [2,3]

输入: edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]
输出: [1,4]

"""
def findRedundantConnection(edges):
    # 初始化每个节点的父节点为自己
    parent = [i for i in range(len(edges) + 1)]

    def find(x):
        # 路径压缩
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x == root_y:
            return False  # 如果已经连通，则为冗余边
        parent[root_y] = root_x  # 合并两个集合
        return True

    for u, v in edges:
        if not union(u, v):
            return [u, v]




