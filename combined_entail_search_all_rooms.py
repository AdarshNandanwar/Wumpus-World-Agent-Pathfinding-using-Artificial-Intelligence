#!/usr/bin/env python3
from Agent import * # See the Agent.py file
import time
import random


#### All your code can go here.

GRID_SIZE = 4
DEBUG = 1
start_time = 0
total_dpll_calls = 0

def find_pure_symbols(clauses, symbols, model):
    for sym in symbols:
        value = None
        is_pure_symbol = True
        for clause in clauses:
            for c in clause.split():
                if sym in c:
                    if value == None:
                        value = c[0] != '!'
                    else:
                        if value != (c[0] != '!'):
                            is_pure_symbol = False
                            break
            if not is_pure_symbol:
                break
        if is_pure_symbol:
            # if sym not in clauses, None value is returned
            return sym, value
    return None, None

def find_unit_clause(clauses, model):
    for clause in clauses:
        if len(clause) == 1:
            return (clause[0] if clause[0][0] != '!' else clause[0][1:]), (clause[0][0] != '!')
    return None, None


def dpll(clauses, symbols, model):

    global total_dpll_calls
    total_dpll_calls += 1

    # most frequent HEURISTIC
    max_sym = [None, 0]
    freq = dict()

    # checking if all clauses are true or if any clause is false
    is_all_true = True
    next_clauses = set()
    for clause in clauses:
        clause = clause.split()
        new_clause = []
        is_not_assigned = False    # True when the clause is False
        is_true = False    
        add_clause = True
        for c in clause:
            sym, sign = (c, True) if c[0] != '!' else (c[1:], False)

            if sym in freq:
                freq[sym] += 1
            else:
                freq[sym] = 1
            if max_sym[1] < freq[sym]:
                max_sym = [sym, freq[sym]]

            add_literal = True
            if sym in model:
                if model.get(sym) == sign:
                    is_true = True
                    # Remove this clause from clauses for pure symbol heuristic
                    add_clause = False
                else:
                    # Remove this literal from clause for unit clause heuristic
                    add_literal = False
            else:
                is_not_assigned = True
            if add_literal:
                new_clause.append(c)
        if not is_true:
            is_all_true = False
        is_false = not is_true and not is_not_assigned
        if is_false:
            # print("one false")
            return False
        if add_clause:
            next_clauses.add(' '.join(new_clause))


    if is_all_true:
        return model

    # finding pure symbols
    pure_symbol, value = find_pure_symbols(next_clauses, symbols, model)
    if pure_symbol != None:
        # print("pure_symbol: {0} = {1}".format(pure_symbol, value))
        next_symbols = symbols.copy()
        next_symbols.remove(pure_symbol)
        next_model = model.copy()
        next_model[pure_symbol] = value
        return dpll(next_clauses, next_symbols, next_model)

    # finding unit clause
    unit_clause, value = find_unit_clause(next_clauses, model)
    if unit_clause != None:
        # print("unit_clause: {0} = {1}".format(unit_clause, value))
        next_symbols = symbols.copy()
        next_symbols.remove(unit_clause)
        next_model = model.copy()
        next_model[unit_clause] = value
        return dpll(next_clauses, next_symbols, next_model)

    next_symbols = symbols.copy()
    first = max_sym[0]
    if first in next_symbols:
        next_symbols.remove(first)
    next_model = model.copy()

    # Random Assignment HEURISTIC
    value = random.randint(0, 1)
    next_model[first] = (value == 1)
    res = dpll(next_clauses, next_symbols, next_model)
    if res: return res
    next_model[first] = not next_model[first]
    res = dpll(next_clauses, next_symbols, next_model)
    if res: return res
    return False

def plan_route(src, dest, allowed_rooms):
    allowed_rooms.add('r'+str(dest[0])+str(dest[1]))
    visited = set()
    queue = []
    queue.append(src) 
    room = 'r'+str(src[0])+str(src[1])
    visited.add(room)
    parent = dict()
    cur = src
    while queue:
        cur = queue.pop(0)
        if cur == dest:
            break
        dir = [0, -1, 0, 1, 0]
        for i in range(GRID_SIZE):
            nbr = [cur[0]+dir[i], cur[1]+dir[i+1]]
            nbr_room = 'r'+str(nbr[0])+str(nbr[1])
            if nbr_room in allowed_rooms and nbr_room not in visited:
                parent[nbr_room] = [cur, i]
                queue.append(nbr)
                visited.add(nbr_room)
    
    if cur != dest:
        # print("No path available")
        return []
    
    dir_map = {
        0: 'Down',
        1: 'Left',
        2: 'Up',
        3: 'Right'
    }
    actions = []
    while cur != src:
        cur_room = 'r'+str(cur[0])+str(cur[1])
        actions.append(dir_map[parent[cur_room][1]])
        cur = parent[cur_room][0]
    actions.reverse()

    return actions


def hybrid_wumpus_agent(ag, kb, symbols, model):

    call_count = 0
    safe = set()
    safe.add('r11')
    safe.add('r'+str(GRID_SIZE)+str(GRID_SIZE))
    visited = set()
    # unvisited = ['r11']

    dpll_call_count = dict()
    for i in range(1, GRID_SIZE+1):
        for j in range(1, GRID_SIZE+1):
            dpll_call_count['r'+str(i)+str(j)] = 0

    rooms = []
    for i in range(1, GRID_SIZE+1):
        for j in range(1, GRID_SIZE+1):
            rooms.append('r'+str(i)+str(j))
    # sort according to manhattan diatance
    rooms.sort(key=lambda x: abs(GRID_SIZE-int(x[1]))+abs(GRID_SIZE-int(x[2])), reverse = True)

    # if DEBUG: print(kb)
    if DEBUG: print("kb: {0} - {1} seconds".format(len(kb), time.time() - start_time))

    while True:
        if DEBUG: print()
        loc = ag.FindCurrentLocation()
        if DEBUG: print(loc)
        if loc == [GRID_SIZE,GRID_SIZE]:
            break
        visited.add('r'+str(loc[0])+str(loc[1]))
        # unvisited.remove('r'+str(loc[0])+str(loc[1]))


        ag_percept = ag.PerceiveCurrentLocation()
        if DEBUG: print("percept: {0}".format(ag_percept))
        # breeze
        kb.add(('' if ag_percept[0] else '!')+'b'+str(loc[0])+str(loc[1]))
        # if DEBUG: print("[{0}, {1}]: {2}".format(i, j, ('' if ag_percept[0] else '!')+'b'+str(loc[0])+str(loc[1])))
        # stench
        kb.add(('' if ag_percept[1] else '!')+'s'+str(loc[0])+str(loc[1]))
        # if DEBUG: print("[{0}, {1}]: {2}".format(i, j, ('' if ag_percept[1] else '!')+'s'+str(loc[0])+str(loc[1])))


        # ADD RULES OF CURRENT LOCATION

        # # add breeze <-> pit and stench <-> wumpus sentences
        # i,j = loc
        # dir = [0, -1, 0, 1, 0]
        # percept = ['b', 's']
        # conclusion = ['p', 'w']
        # for p in range(2):
        #     clauses = []
        #     for k in range(GRID_SIZE):
        #         x = i+dir[k]
        #         y = j+dir[k+1]
        #         if x>=1 and x<=GRID_SIZE and y>=1 and y<=GRID_SIZE:
        #             if len(clauses) == 0:
        #                 clauses.append(['!'+percept[p]+str(i)+str(j)])
        #             clauses[0].append(conclusion[p]+str(x)+str(y))
        #             clauses.append([percept[p]+str(i)+str(j), '!'+conclusion[p]+str(x)+str(y)])
        #     if len(clauses) > 0:
        #         for clause in clauses:
        #             clause.sort()
        #             kb.add(' '.join(clause))
        #         if DEBUG: print("[{0}, {1}]: {2}".format(i, j, clauses))


        # # add breeze -> pit, !breeze -> !pit and stench -> wumpus, !stench -> !wumpus sentences
        # i,j = loc
        # dir = [0, -1, 0, 1, 0]
        # percept = ['b', 's']
        # conclusion = ['p', 'w']
        # for p in range(2):
        #     clauses = []
        #     clause_true = []
        #     for k in range(GRID_SIZE):
        #         x = i+dir[k]
        #         y = j+dir[k+1]
        #         if x>=1 and x<=GRID_SIZE and y>=1 and y<=GRID_SIZE:
        #             if len(clause_true) == 0:
        #                 clause_true.append('!'+percept[p]+str(i)+str(j))
        #             clause_true.append(conclusion[p]+str(x)+str(y))
        #             clauses.append([percept[p]+str(i)+str(j), '!'+conclusion[p]+str(x)+str(y)])
        #     if len(clauses) > 0:
        #         clause_true.sort()
        #         kb.add(' '.join(clause_true))
        #         for clause in clauses:
        #             clause.sort()
        #             kb.add(' '.join(clause))
        #         if DEBUG: print("[{0}, {1}]: {2} {3}".format(i, j, clauses, clause_true))

        # MANUAL ADDITION
        dir = [0, -1, 0, 1, 0]
        i,j = loc
        conclusion = ['p', 'w']
        for p in range(2):
            if ag_percept[p]:
                clause = []
                for k in range(GRID_SIZE):
                    x = i+dir[k]
                    y = j+dir[k+1]
                    if x>=1 and x<=GRID_SIZE and y>=1 and y<=GRID_SIZE and 'r'+str(x)+str(y) not in safe:
                        clause.append(conclusion[p]+str(x)+str(y))
                kb.add(' '.join(clause))
                if DEBUG: print("[{0}, {1}]: {2}".format(i, j, ' '.join(clause)))
            else:
                for k in range(GRID_SIZE):
                    x = i+dir[k]
                    y = j+dir[k+1]
                    if x>=1 and x<=GRID_SIZE and y>=1 and y<=GRID_SIZE and 'r'+str(x)+str(y) not in safe:
                        kb.add('!'+conclusion[p]+str(x)+str(y))
                        if DEBUG: print("[{0}, {1}]: {2}".format(i, j, '!'+conclusion[p]+str(x)+str(y)))





        if DEBUG: print("kb: {0} - {1} seconds".format(len(kb), time.time() - start_time))

        # for x in range(GRID_SIZE, 0, -1):
        #     for y in range(GRID_SIZE, 0, -1):
        # for x in range(1, GRID_SIZE+1):
        #     for y in range(1, GRID_SIZE+1):
        #         room = 'r'+str(x)+str(y)
        random.shuffle(rooms)
        for room in rooms:
            if room not in safe:
                dpll_call_count[room] += 1
                # print("CHECKING IF NO PIT AND NOT WUMPUS AT [{0}, {1}]".format(x,y))
                kb_safe = kb.copy()
                kb_safe.add('p'+room[1:]+' '+'w'+room[1:])
                global total_dpll_calls
                total_dpll_calls = 0
                res = dpll(kb_safe, symbols, {})
                call_count += total_dpll_calls
                is_safe = (res == False)
                if DEBUG: print("dpll {0}: is safe {1}, dpll calls {2}".format('r'+room[1:], is_safe, total_dpll_calls))
                if is_safe:
                    kb.add('!p'+room[1:])
                    kb.add('!w'+room[1:])
                    safe.add('r'+room[1:])
                    action_sequence = plan_route(loc, [GRID_SIZE, GRID_SIZE], safe)
                    if len(action_sequence) != 0:
                        for action in action_sequence:
                            ag.TakeAction(action)
                        return


        if DEBUG: print("safe {0}".format(safe))
        if DEBUG: print("visited {0}".format(visited))

        # assuming there is always a safe room
        next_room = None
        action_sequence = []
        for safe_room in safe:
            if safe_room not in visited:
                next_room = safe_room
                action_sequence = plan_route(loc, [int(next_room[1]), int(next_room[2])], safe)
                if len(action_sequence) != 0:
                    break

        if DEBUG: print("next_room {0}".format(next_room))

        for action in action_sequence:
            ag.TakeAction(action)
    print('total dpll calls {0}'.format(call_count))



#### You can change the main function as you wish. Run this program to see the output. Also see Agent.py code.


def main():

    # symbols:
    #     wumpus - w[i][j]
    #     pit - p[i][j]
    # percepts:
    #     stench - s[i][j]
    #     breeze - b[i][j]


    symbols = set()
    for i in range(1, GRID_SIZE+1):
        for j in range(1, GRID_SIZE+1):
            symbols.add('w'+str(i)+str(j))
            symbols.add('p'+str(i)+str(j))
            symbols.add('b'+str(i)+str(j))
            symbols.add('s'+str(i)+str(j))

    kb = set()

    # no pit or wumpus in [1,1]
    kb.add('!p11')
    kb.add('!p'+str(GRID_SIZE)+str(GRID_SIZE))
    kb.add('!w11')
    kb.add('!w'+str(GRID_SIZE)+str(GRID_SIZE))

    # atleast 1 wumpus and atleast 1 pit
    for k in {'w', 'p'}:
        clause = []
        for i in range(1,GRID_SIZE+1):
            for j in range(1,GRID_SIZE+1):
                clause.append(k+str(i)+str(j))
        clause.sort()
        kb.add(' '.join(clause))

    # atmost 1 wumpus and atmost 1 pit 
    for k in {'w', 'p'}:
        clauses = []
        for P in range(GRID_SIZE*GRID_SIZE):
            for Q in range(P+1, GRID_SIZE*GRID_SIZE):
                i1 = P%GRID_SIZE+1
                j1 = P//GRID_SIZE+1
                i2 = Q%GRID_SIZE+1
                j2 = Q//GRID_SIZE+1
                clauses.append(['!'+k+str(i1)+str(j1), '!'+k+str(i2)+str(j2)])
        for clause in clauses:
            clause.sort()
            kb.add(' '.join(clause))


    ag = Agent()
    hybrid_wumpus_agent(ag, kb, symbols, {})





if __name__=='__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
    print('total dpll calls:',total_dpll_calls)