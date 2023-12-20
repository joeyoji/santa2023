

class SymmetricGroup():

    def __init__(self, perm):

        '''
        perm : List
        '''

        self.perm = perm
        if type(self.perm)!=list:
            raise ValueError('permutation should be list.')
        if sorted(self.perm)!=list(range(len(perm))):
            raise ValueError('perm should be continuous.')

    def __str__(self):

        return str(self.perm)

    def __call__(self, x):

        '''
        return same type according to x. (list and SymmetricGroup only so far.)
        '''

        if type(x)==SymmetricGroup:
            if len(x.perm)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = [x.perm[t] for t in self.perm]
            return SymmetricGroup(_perm)
        if type(x)==list:
            if len(x)!=len(self.perm):
                raise ValueError('same length only.')
            _perm = [x[t] for t in self.perm]
        return _perm

    def __neg__(self):

        '''
        return negative element.
        '''

        _perm_dict = dict(zip(self.perm,list(range(len(self.perm)))))
        _perm = [num for _, num in sorted(_perm_dict.items())]
        return SymmetricGroup(_perm)
    
    def __mul__(self, other):

        '''
        same type only
        '''

        return self(other)
    
    def __imul__(self, other):

        '''
        same type only
        '''

        _perm = self(other.perm)
        self.perm = _perm

        return self

    def __eq__(self, other):

        if type(self)==type(other):
            return self.perm==other.perm
        else:
            return False
    
    def __pow__(self, num):

        '''
        num should be integer.
        '''

        if type(num)!=int:
            raise ValueError('power should be integer.')
        else:
            _unit = SymmetricGroup(list(range(len(self.perm))))
            if num>=0:
                _perm = eval('_unit'+' * self'*num)
                return _perm
            else:
                _perm = eval('_unit'+' * (-self)'*(-num))
                return _perm

    def copy(self):

        '''
        duplicate oneself
        '''

        return SymmetricGroup(self.perm)

    def __len__(self):

        '''
        here len means by multipling how many itselves this instance is reobtained.
        
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
