import os
import re
from glob import glob
from pathlib import Path
from tqdm import tqdm
import gc

import numpy as np
import pandas as pd


CFG_INFO_PTH = ''

class Permutation():

    def __init__(self, perm):

        ''' perm : List '''

        self.perm = np.array(perm)
        if type(self.perm)!=np.ndarray:
            raise ValueError('perm should be np.ndarray.')
        if np.abs(np.sort(self.perm)-np.arange(len(perm))).sum()>0:
            raise ValueError('perm should be continuous.')


    def __call__(self, x):

        ''' return same type according to x. (Permutation and np.ndarray only so far.) '''
        if type(x)==Permutation:
            if len(x.perm)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = x.perm[self.perm]
            return Permutation(_perm)
        elif type(x)==np.ndarray:
            if len(x)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = x[self.perm]
            return _perm
        else:
            raise ValueError('type should be Permutation, list, or str.')


    def __neg__(self):

        ''' return negative element. '''

        _perm = np.argsort(self.perm)
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
            return np.abs(self.perm-other.perm).sum()==0
        else:
            return False
    
    def __pow__(self, num):

        ''' num should be integer. '''

        if type(num)!=int:
            raise ValueError('power should be integer.')
        else:
            _unit = Permutation(np.arange(len(self.perm)))
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

    def __init__(self, puzzle_type, solution_state, initial_state, num_wildcards):

        self.puzzle_type = puzzle_type
        self.solution_state = self.state_encoder(solution_state)
        self.initial_state = self.state_encoder(initial_state)
        self.num_wildcards = num_wildcards
        self.puzzle_info = pd.read_csv(CFG_INFO_PTH)
        
        self.current_state = self.state_encoder(initial_state)
        self.move_log = [self.state_encoder(initial_state),]

        self._set_moves()


    def reset(self):

        self.__init__(self.puzzle_type, self.solution_state, self.initial_state, self.num_wildcards)


    def __str__(self):

        return self.state_decoder(self.current_state)


    def state_encoder(self, state_str):
    
        if re.match('[A-Z];', state_str):
            return np.array(state_str.split(';'),dtype='<U1')
        if re.match('N[0-9]+;', state_str):
            return np.array([int(k) for k in state_str[1:].split(';N')])
        

    def state_decoder(self, state):

        if state.dtype==np.dtype('<U1'):
            return ';'.join(state)
        if state.dtype==np.dtype('int64'):
            return 'N'+';N'.join(state.astype(str))


    def _set_moves(self):

        _allowed_moves = self.puzzle_info[self.puzzle_info.puzzle_type==self.puzzle_type].allowed_moves.iloc[0]
        _allowed_moves = {key:Permutation(perm) for key, perm in eval(_allowed_moves).items()}
        self.allowed_moves = _allowed_moves | {'-'+key:(-perm) for key, perm in _allowed_moves.items()}
        _perm_len = len(list(_allowed_moves.values())[0].perm)
        _u0 = Permutation(np.arange(_perm_len))
        self.allowed_moves['u0'] = _u0


    def __call__(self,key):

        if not key in list(self.allowed_moves.keys()):
            raise ValueError('key should be in allowed_moves.')
        
        _gotten_perm = self.allowed_moves[key]
        self.current_state = _gotten_perm(self.current_state)
        self.move_log += [key, self.current_state, ]
        return self
    

    def random_walk(self,stepsize,seed=None):

        if seed:
            np.random.seed(seed)

        _not_stop = list(set(self.allowed_moves.keys()) - set('u0'))
        _walk = np.random.choice(_not_stop,size=stepsize,replace=True)
        for key in _walk:
            self(key)
        return self
    

    def march_inplace(self,stepsize):

        for _ in range(stepsize):
            self('u0')
        return self


    def _reverse_op(self, op):

        if op=='u0':
            return op
        elif op.startswith('-'):
            return op[1:]
        else:
            return '-'+op

    def reverse_log(self):

        _temp_log = self.move_log[::-1]
        _temp_log[1::2] = [self._reverse_op(op) for op in _temp_log[1::2]]
        self.initial_state = _temp_log[0]
        self.current_state = _temp_log[-1]
        self.move_log = _temp_log

        return self