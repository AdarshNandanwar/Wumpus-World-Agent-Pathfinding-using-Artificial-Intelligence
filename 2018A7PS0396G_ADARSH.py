#!/usr/bin/env python3
from Agent import * # See the Agent.py file


#### All your code can go here.

def find_pure_symbols(clauses, symbols, model):
    for sym in symbols:
        value = None
        is_pure_symbol = True
        for clause in clauses:
            for c in clause:
                if sym in c:
                    if value is None:
                        value = sym[0] is not '!'
                    else:
                        if value != (sym[0] is not '!'):
                            is_pure_symbol = False
                            break
            if not is_pure_symbol:
                break
        if is_pure_symbol:
            return sym, value
    return None, None

def find_unit_clause(clauses, model):
    for clause in clauses:
        if len(clause) is 1:
            return clause[0], clause[0][0] is not '!'
    return None, None

def dpll(clauses, symbols, model):

    # Remove true clauses as we go

    # checking if all clauses are true or if any clause is false
    is_all_true = True
    next_clauses = []
    for clause in clauses:
        new_clause = []
        is_not_assigned = False    # True when the clause is False
        is_true = False    
        add_clause = True
        for c in clause:
            sym, sign = (c, True) if c[0] is not '!' else (c[1:], False)
            add_literal = True
            if sym in model:
                if model.get(sym) is sign:
                    is_true = True
                    # Remove this clause from clauses for pure symbol heuristic
                    add_clause = False
                else:
                    # Remove this literal from clause for unit clause heuristic
                    add_literal = False
            else:
                is_not_assigned = True
            if add_literal is True:
                new_clause.append(c)
        if not is_true:
            is_all_true = False
        is_false = not is_true and not is_not_assigned
        if is_false:
            return False
        if add_clause is True:
            next_clauses.append(new_clause)


    if is_all_true:
        return True

    # finding pure symbols
    pure_symbol, value = find_pure_symbols(next_clauses, symbols, model)
    if pure_symbol is not None:
        next_symbols = symbols.copy()
        next_symbols.remove(pure_symbol)
        next_model = model.copy()
        next_model[pure_symbol] = value
        return dpll(next_clauses, next_symbols, next_model)

    # finding unit clause
    unit_clause, value = find_unit_clause(next_clauses, model)
    if unit_clause is not None:
        next_symbols = symbols.copy()
        next_symbols.remove(unit_clause)
        next_model = model.copy()
        next_model[unit_clause] = value
        return dpll(next_clauses, next_symbols, next_model)

    first = symbols[0]
    rest = symbols[1:]
    next_model = model.copy()
    next_model[first] = True
    if dpll(next_clauses, rest, next_model): return True
    next_model[first] = False
    if dpll(next_clauses, rest, next_model): return True
    return False

def plan_route(src, dest, allowed_rooms):
    allowed_rooms.add('r'+str(dest[0])+str(dest[1]))
    visited = set()
    queue = []
    queue.append(src) 
    room = 'r'+str(src[0])+str(src[1])
    visited.add(room)
    parent = dict()
    while queue:
        cur = queue.pop(0)
        if cur == dest:
            break
        dir = [0, -1, 0, 1, 0]
        for i in range(4):
            nbr = [cur[0]+dir[i], cur[1]+dir[i+1]]
            nbr_room = 'r'+str(nbr[0])+str(nbr[1])
            if nbr_room in allowed_rooms and nbr_room not in visited:
                parent[nbr_room] = [cur, i]
                queue.append(nbr)
                visited.add(nbr_room)

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

    if len(actions) == 0:
        print("No path available")
        return []

    return actions


def hybrid_wumpus_agent(ag, kb, symbols, model):

    safe = set()
    safe.add('r11')
    visited = set()

    while True:
        print()

        loc = ag.FindCurrentLocation()
        print(loc)

        if loc is [4,4]:
            break

        percept = ag.PerceiveCurrentLocation()
        print("percept: {0}".format(percept))
        visited.add('r'+str(loc[0])+str(loc[1]))


        if percept[0]:
            # breeze
            kb.append(['b'+str(loc[0])+str(loc[1])])

        if percept[1]:
            # stench
            kb.append(['s'+str(loc[0])+str(loc[1])])

        # if dpll(kb+[[]], symbols, {}) is True:
        dir = [0, -1, 0, 1, 0]
        for k in range(4):
            x = loc[0]+dir[k]
            y = loc[1]+dir[k+1]
            if x>=1 and x<=4 and y>=1 and y<=4 and 'r'+str(x)+str(y) not in visited:
                print("================ DPLL ================")
                is_no_pit = (dpll(kb+[['p'+str(x)+str(y)]], symbols, {}) == False)
                print("xxxxxxxxxxxxxxxx DPLL xxxxxxxxxxxxxxxx")
                print("================ DPLL ================")
                is_no_wumpus = (dpll(kb+[['w'+str(x)+str(y)]], symbols, {}) == False)
                print("xxxxxxxxxxxxxxxx DPLL xxxxxxxxxxxxxxxx")
                print("dpll {0}: pit {1}, wumpus {2}".format('r'+str(x)+str(y), not is_no_pit, not is_no_wumpus))
                if is_no_pit and is_no_wumpus:
                    safe.add('r'+str(x)+str(y))

        print("safe {0}".format(safe))
        print("visited {0}".format(visited))

        # assuming there is always a safe room
        if len(safe) == 0:
            print("no safe room")
            return

        next_room = safe.pop()
        print("next_room {0}".format(next_room))

        action_sequence = plan_route(loc, [int(next_room[1]), int(next_room[2])], visited)
        # print("action_sequence {0}".format(action_sequence))

        for action in action_sequence:
            ag.TakeAction(action)



#### You can change the main function as you wish. Run this program to see the output. Also see Agent.py code.


def main():

    # symbols:
    #     wumpus - w[i][j]
    #     pit - p[i][j]
    # percepts:
    #     stench - s[i][j]
    #     breeze - b[i][j]


    symbols = []
    for i in range(1, 5):
        for j in range(1, 5):
            symbols.append('w'+str(i)+str(j))
            symbols.append('p'+str(i)+str(j))
            symbols.append('b'+str(i)+str(j))
            symbols.append('s'+str(i)+str(j))

    kb = []

    # no pit or wumpus in [1,1]
    kb.append(['!p11'])
    kb.append(['!w11'])

    # add breeze <-> pit and stench <-> wumpus sentences
    dir = [0, -1, 0, 1, 0]
    percept = ['b', 's']
    conclusion = ['p', 'w']
    for p in range(2):
        for i in range(1,5):
            for j in range(1,5):
                sentence = []
                for k in range(4):
                    x = i+dir[k]
                    y = j+dir[k+1]
                    if x>=1 and x<=4 and y>=1 and y<=4:
                        if len(sentence) == 0:
                            sentence.append(['!'+percept[p]+str(i)+str(j)])
                        sentence[0].append(conclusion[p]+str(x)+str(y))
                        sentence.append([percept[p]+str(i)+str(j), '!'+conclusion[p]+str(x)+str(y)])
                if len(sentence) > 0:
                    kb.extend(sentence)
                    # print("[{0},{1}]: {2}".format(i, j, sentence))

    # atleast 1 wumpus and atleast 1 pit
    for k in {'w', 'p'}:
        clause = []
        for i in range(1,5):
            for j in range(1,5):
                clause.append(k+str(i)+str(j))
        kb.append(clause)

    # atmost 1 wumpus and atmost 1 pit 
    for k in {'w', 'p'}:
        clauses = []
        for P in range(4*4):
            for Q in range(P+1, 4*4):
                i1 = P%4+1
                j1 = P//4+1
                i2 = Q%4+1
                j2 = Q//4+1
                clauses.append(['!'+k+str(i1)+str(j1), '!'+k+str(i2)+str(j2)])
        kb.extend(clauses)
        # print(len(clauses))

    # print(len(kb))
    # print(kb)

    ag = Agent()

    hybrid_wumpus_agent(ag, kb, symbols, {})

    # print("action_seq: {0}".format(plan_route([1,3],[1,4], set(['r11','r12','r13']))))


if __name__=='__main__':
    main()
