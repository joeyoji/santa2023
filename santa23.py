import os
import re
from glob import glob
from pathlib import Path
from tqdm import tqdm
import gc


import numpy as np
import pandas as pd


class Permutation():

    def __init__(self, perm):

        ''' perm : List '''

        self.perm = perm
        if type(self.perm)!=list:
            raise ValueError('perm should be list.')
        if sorted(self.perm)!=list(range(len(perm))):
            raise ValueError('perm should be continuous.')

    def __str__(self):

        return str(self.perm)

    def __call__(self, x):

        ''' return same type according to x. (list and Permutation only so far.) '''
        if type(x)==Permutation:
            if len(x.perm)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = [x.perm[t] for t in self.perm]
            return Permutation(_perm)
        if type(x)==list:
            if len(x)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = [x[t] for t in self.perm]
        return _perm

    def __neg__(self):

        ''' return negative element. '''

        _perm_dict = dict(zip(self.perm,list(range(len(self.perm)))))
        _perm = [num for _, num in sorted(_perm_dict.items())]
        return Permutation(_perm)
    
    def __mul__(self, other):

        ''' same type only '''

        return self(other)
    
    def __imul__(self, other):

        ''' same type only '''

        _perm = self(other.perm)
        self.perm = _perm

        return self

    def __eq__(self, other):

        if type(self)==type(other):
            return self.perm==other.perm
        else:
            return False
    
    def __pow__(self, num):

        ''' num should be integer. '''

        if type(num)!=int:
            raise ValueError('power should be integer.')
        else:
            _unit = Permutation(list(range(len(self.perm))))
            if num>=0:
                _perm = eval('_unit'+' * self'*num)
                return _perm
            else:
                _perm = eval('_unit'+' * (-self)'*(-num))
                return _perm

    def copy(self):

        ''' duplicate oneself '''

        return Permutation(self.perm)

    def __len__(self):

        '''
        here len means by multipling how many itselves this instance is reobtained.
        
        e.g.)
        self**len(self) == unit
        self**(len(self)+1) == self
        '''

        _perm = self.copy()
        k = 0
        while True:
            _perm *= self.copy()
            k += 1
            if _perm == self.copy():
                break
            
        return k


class Puzzle():

    def __init__(self, pd_row, info_pth):

        self.puzzle_type = pd_row.puzzle_type
        self.solution_state = self.state_encoder(pd_row.solution_state)
        self.initial_state = self.state_encoder(pd_row.initial_state)
        self.num_wildcards = pd_row.num_wildcards
        self._info_pth = info_pth
        self.puzzle_info = pd.read_csv(info_pth)
        
        self.current_state = self.state_encoder(pd_row.initial_state)
        self.move_log = []

        self._set_moves()


    def copy(self):

        newp = Puzzle(self.puzzle_type, self._info_pth)

        newp.current_state = self.current_state
        newp.move_log = self.move_log

    
    def state_encoder(self, state_str):
        
        if re.match('[A-Z];', state_str):
            return ''.join(state_str.split(';'))
        if re.match('N[0-9]+;', state_str):
            return [int(k) for k in state_str[1:].split(';N')]
        

    def state_decoder(self, state):

        if type(state)==str:
            return ';'.join(list(state))
        if type(state)==list:
            return 'N'+';N'.join(state)



    def _set_moves(self):

        _allowed_moves = self.puzzle_info[self.puzzle_info.puzzle_type==self.puzzle_type].allowed_moves.iloc[0]
        self.allowed_moves = {key:Permutation(perm) for key, perm in eval(_allowed_moves).items()}


    def __call__(self,key):

        if not key in list(self.allowed_moves.keys()):
            raise ValueError('key should be in allowed_moves.')
        
        _Permutation = self.allowed_moves[key]
        self.move_log.append(self.current_state)
        self.current_state = _Permutation(self.current_state)