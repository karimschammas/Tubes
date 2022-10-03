import pandas as pd
import itertools as it
import numpy as np

def last_element(ls):
    # Last non-null element of tube
    if len(ls) == 0:
        return None
    if ls[-1] is None:
        return last_element(ls[:-1])
    else:
        return ls[-1]
def is_empty(ls):
    return set(ls) == {None}
    
class Tube():
    def __init__(self, tube, nmax_tube = 4, removed_elements = [], added_elements = []):
        if isinstance(tube,list):
            self.tube = tube + [None] * (nmax_tube - len(tube))
            self.stripped = [el for el in tube if el is not None]
            self.nmax_tube = nmax_tube
            self.is_empty = is_empty(self.tube)
            self.is_full = bool(self.stripped == self.tube)
            self.last_element = last_element(self.tube)
            self.is_homo = bool(len(set(self.stripped)) == 1)
            self.is_done = self.is_full and self.is_homo
            self.removed_elements = removed_elements
            self.added_elements = added_elements
        else:
            # Si l'objet est déjà un tube, on recupère ses attribus
            self.tube = tube.tube
            self.stripped = tube.stripped
            self.nmax_tube = tube.nmax_tube
            self.is_empty = tube.is_empty
            self.is_full = tube.is_full
            self.last_element = tube.last_element
            self.is_homo = tube.is_homo
            self.is_done = tube.is_done
            self.removed_elements = tube.removed_elements
            self.added_elements = tube.added_elements
            
    def __repr__(self): return str(self.tube)
        
    def can_add(self):
        return not(len(self.stripped) == self.nmax_tube)
    
    def can_add_element(self, element, verbose = False):
        # Is it possible to add element "element" to tube?
        if not(self.can_add()):
            if verbose: print('Tube is full')
            return False
        elif (self.last_element != element) and (self.last_element is not None):
            if verbose: 
                print(f'Incompatible colors: {element} vs {self.last_element}')
                print(self)
            return False
        elif element == last_element(self.removed_elements):
            if verbose: print(f'Had just removed this element ({element})')
            return False
        else:
            return True
     
    def add_element(self, element, verbose = False):
        # Action of adding an element to an existing tube
        if self.can_add_element(element, verbose = verbose):
            tube_res = Tube(tube = self.stripped + [element],
                        nmax_tube = self.nmax_tube,
                        removed_elements = self.removed_elements,
                        added_elements = self.added_elements
                       )
            return tube_res
        else:
            if verbose: print('cannot add element')
    
    def can_remove(self):
        # Tells us if we can remove an element from tube
        return not(self.is_empty or self.is_done or (last_element(self.stripped) == last_element(self.added_elements)))
        
    def remove_last_element(self):
        # Action of removing last element if possible
        if self.can_remove():
            tube_res = Tube(tube = self.stripped[:-1],
                        nmax_tube = self.nmax_tube,
                        removed_elements = self.removed_elements + [self.stripped[-1]],
                       added_elements = self.added_elements)
            return tube_res
        else:
            return self

    
class Tubes():
    def __init__(self, tubes, nmax = 4, history = []):
        # Lengths of tubes
        self.nmax_tube = nmax
        self.objects = [
            Tube(tube = tube, nmax_tube = self.nmax_tube)
            for tube in tubes
        ]
        
        pp = [i for a in self.objects for i in a.stripped]
        if (len(set([pp.count(col) for col in set(pp)])) != 1):
            print('Tubes incoherent')
            raise ValueError
            
        self.tubes = [
            tube.tube
            for tube in self.objects
        ]

        # Number of tubes
        self.n_tubes = len(tubes)
        # Colors
        self.colors = set([elem for ls in self.tubes for elem in ls if elem is not None])
        self.n_colors = len(self.colors)
        self.history = history
        
        
    def __repr__(self):
        # Representation of the object when we print it
        config = [list(x) for x in np.array(self.tubes).transpose()[::-1]]
        s = [[str(e) for e in row] for row in config]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '|' + '|\t|'.join('{{:{}}}'.format(x) for x in lens) + '|'
        table = [fmt.format(*row) for row in s]
        res = '\n'.join(table)
        return (res + '\n\n' + '\t'.join([('T'+str(i)) for i in range(1, tubes.n_tubes+1)]) + '\n')       
        
    def characterize(self):
        print(f'there are {self.n_tubes} tubes of {self.n_colors} colors: {self.colors}\n')
        
    def all_actions(self):
        # All possible actions. Represented as a list of strings "x>y" = tube x to tube y
        return [str(x[0]) + '>' + str(x[1]) for x in it.permutations([i for i in range(1, self.n_tubes + 1)],2)]
    
    def assess_action(self, action, verbose = False):
        # Assess action: can it be done (True), or not (False)?
        obj1 = self.objects[int(action[0]) -1] # Tube object n1
        obj2 = self.objects[int(action[2]) -1] # Tube object n2
        try:
            tube1 = Tube(tube = obj1,
                        nmax_tube = self.nmax_tube
                        )
            tube2 = Tube(tube = obj2,
                        nmax_tube = self.nmax_tube
                        )
            res = (tube1.can_remove() and tube2.can_add_element(element = tube1.last_element, verbose = verbose)) and not(tube1.is_homo and tube2.is_empty)
            # if tube1 is homogenous and tube2 is empty, useless
        except:
            print('action invalid', action)
            print('tubes\n', self)
            print('objects', self.objects)
            print('obj1', obj1)
            print('obj2', obj2)
            print(self.history)
            return False
        return res
        
    def possible_actions(self):
        # List of all possible actions that are doable
        try:
            return [action for action in self.all_actions() if self.assess_action(action, False)]
        except:
            print(self)
            print(self.all_actions())
            return [action for action in self.all_actions() if self.assess_action(action, True)]
    
    # Is called at each step to know if we can continue the game
    def can_continue(self):
        if len(self.possible_actions())>0:
            return True
        else:
            return False
#         elif tubes.have_won():
#             print('CONGRATS YOU WIN')
#         else:
#             print('GAME OVER')
    
    def have_won(self):
        # All tubes are either done or empty
        return len([tube for tube in self.objects if (tube.is_done or tube.is_empty)]) == self.n_tubes
    
    def move(self, action, verbose = True):
        # Method that realizes action: displacement from one tube to another.
        # action "3>2" = displace last element of tube 3 to tube 2
        index_from = int(action[0]) - 1
        index_to = int(action[2]) - 1
        if self.assess_action(action, verbose = verbose):
            try:
                element = last_element(self.tubes[index_from])
                self.objects[index_from] = self.objects[index_from].remove_last_element()
                self.objects[index_to] = self.objects[index_to].add_element(element, False)
                res = Tubes(self.objects, history = self.history + [action])
                return res
            except:
                return self
        else:
            if verbose:
                print('cant make action', action)
                print(self.objects[index_from], self.objects[index_to])
            return self
    
    def make_moves(self, actions, verbose = False):
        # Make a series of moves stored in list "actions" as strings
        for action in actions:
            self = self.move(action, verbose = verbose)
        return self
    
    def play_till_over(self, verbose = False):
        # Does all the possible scenarios and return the history of the winning scenario
        if self.can_continue():
            try:
                poss_actions = self.possible_actions()
            except:
                print('poss actions invalid')
                return self
            for poss in poss_actions:
                try:
                    move = self.move(action = poss, verbose = verbose)
                except:
                    print('failed to move', poss)
                    print('current state:', self)
                    print('history:',self.history)
                    move = self.move(action = poss, verbose = True)
                    
                # Recursion
                scenar = move.play_till_over()
                if scenar == True:
                    return scenar 
                else:
                    continue
        elif self.have_won():
            print('have won with', self.history)
            return True
        else:
            #print('Game over', self.history)
            return False

        
# Application

arr = [
    [1,2,2,3],
    [1,4,5,6],
    [1,7,5,3],
    [4,2,6,3],
    [5,6,3,4],
    [7,5,4,7],
    [1,7,2,6],
    [],
    []
]

tubes = Tubes(arr,4)
tubes

move = '1>8'
tubes = tubes.move(move)
tubes

tubes.possible_actions()

tubes.play_till_over()
