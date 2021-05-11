def raft():
    goats, courses = [int(x) for x in input().split()]
    if courses <= 1 or courses >= 1000 or goats <= 1 or goats >= 1000:
        return

    goats_weight = list(map(int, input().split()))

    if len(goats_weight) != goats:
        return

    goats_weight.sort(reverse=True)
    min_raft_size = goats_weight[0]
    max_raft_size = sum(goats_weight)
    best_raft_size = max_raft_size

    trips = []

    for i in range(courses):
        trips.append([])

    for temp_raft_size in range(min_raft_size, max_raft_size):
        temp_goats_weight = goats_weight.copy()

        for i in range(courses):
            for goat in temp_goats_weight:
                if sum(trips[i]) + goat > temp_raft_size:
                    pass

                else:
                    trips[i].append(goat)

            for n, k in enumerate(temp_goats_weight):
                if k in trips[i]:
                    temp_goats_weight[n] = 0
                    trips[i][trips[i].index(k)] = 0

        if sum(temp_goats_weight) == 0:
            best_raft_size = temp_raft_size
            break

        for i in range(courses):
            trips[i] = []

    print(best_raft_size)


if __name__ == '__main__':
    raft()
