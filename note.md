# improvements
- if symbol is eleminated from the CNF, remove it from `symbols` set
- can wumpus and pi be in same room
- remove time library
- randomize the dir
- apply dpll on all possible neighbours... to solve random rooms problem
- when we visit rooms randomly, we might have already discarded the room which we shopuld have gone into by visiting its nbr before

- Possible soln: when no more unvisited safe available, run dpll on all the unvisited nbrs and add to safe if safe


# Speed
- random restarts
- manhattan ?
- 