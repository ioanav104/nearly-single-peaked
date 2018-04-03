import numpy
import sys
from preflibtools import io

def wd(s, a, b, c, v):
    return{ # replacement of a switch using dictionaries
        0: v[b] < v[a] and v[c] < v[a],
        1: v[a] < v[b] and v[c] < v[b],
        2: v[a] < v[c] and v[b] < v[c]
    }[s]


def gen_alpha_configs(rank_maps, num_cand, num_votes):
    C = range(1, num_cand+1)
    V = []
    alpha = set()
    for a in C:
        for b in C:
            if a==b:
                continue
            for c in C:
                if a==c or b==c:
                    continue
                for d in C:
                    if a==d or b==d or c==d:
                        continue
                    for i in range(0, num_votes):
                        v = rank_maps[i]
                        if v[a] < v[b] and v[d] < v[b] and v[b] < v[c]:
                            for j in range(0, num_votes):
                                w = rank_maps[j]
                                if w[c] < w[b] and w[d] < w[b] and w[b] < w[a]:
                                    alpha.add(frozenset([i, j]))

    return alpha


def hittingSet(T, num_votes, w):
    contain = dict()
    sol = []
    total = 0
    MAXW = sum(w)
    for v in range(num_votes):
        contain[v] = set()
    for s in T:
        for e in s:
            contain[e].add(s)
    while len(T) > 0:
        s = T.pop()
        k = 0
        minw = MAXW
        for a in s:
            if w[a] < minw:
                minw = w[a]
                k = a
        for c in contain[k]:
                T.discard(c)
        sol.append(k)
        total = total + w[k]
    return (sol, total)


def deleted(rank_maps, num_cand, w):
    C = range(1, num_cand+1)
    num_votes = len(rank_maps)
    Vr = range(0, num_votes)
    V = [[], [], []]
    maxV = []
    maxMinL = 0
    for c1 in C:
        for c2 in C:
            if c1 == c2:
                continue
            for c3 in C:
                if c1 == c3 or c2 == c3:
                    continue
                V = [[], [], []]
                for v in Vr:
                    for s in range(3):
                        if wd(s, c1, c2, c3, rank_maps[v]):
                            V[s].append(v)
                minL = min(list(map (len, V)))
                if minL > maxMinL:
                    maxV = V
                    maxMinL = minL
        
    Vnew = [[],[],[]]
    minWeight = sum(w)
    solution  = []
    A = gen_alpha_configs(rank_maps, num_cand, num_votes)
    for s in range(3):
        Vnew = [[],[],[]]
        T = set(A)
        for v in maxV[s]:
            T.add(frozenset([v]))
        Vp = []
        # Calculate Vp(V[-s]) as V/V[s]
        for i in range (3):
            if i != s:
                Vp = Vp + maxV[i]
        
        for c1 in C:
            for c2 in C:
                if c1 == c2:
                    continue
                for c3 in C:
                    if c1 == c3 or c2 == c3:
                        continue
                    for i in range(3):
                        Vnew[i] = list(filter(lambda x: wd(i, c1, c2, c3, rank_maps[x]), Vp))
                    Vnew.sort(key=lambda x: len(x))   
                    for v0 in Vnew[0]:
                        for v1 in Vnew[1]:
                                T.add(frozenset([v0, v1]))
        
        localSol, localWeight = hittingSet(T, num_votes, w)
        if localWeight < minWeight:
            minWeight = localWeight
            solution = localSol
    return solution, minWeight

def main():
    input_file = open(sys.argv[1], 'r')
    cand_map, rank_maps, rank_map_counts, num_voters = io.read_election_file(input_file)
    num_cand = len(cand_map)
    num_votes = len(rank_map_counts)
    delVotes, delW = deleted(rank_maps, num_cand, rank_map_counts)
    solution = list(filter(lambda x: not(x in delVotes), range(num_votes)))
    print('By choosing votes ' + str(solution) + ',%.2f pc of voters are included'%((num_voters-delW)/num_voters*100))
if __name__ == "__main__":
    main()
