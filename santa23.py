

class SymmetricGroup():


    def __init__(self, perm):
        
        self.perm = perm
        if sorted(self.perm)!=list(range(len(perm))):
            raise ValueError('perm should be continuous.')

    def __len__(self):
        return len(self.perm)

    def __str__(self):
        return str(self.perm)

    def __call__(self, x):
        if len(x)!=len(self):
            raise ValueError('same length only.')
        return [x[t] for t in self.perm]

    def __neg__(self):
        _perm_dict = dict(zip(self.perm,list(range(len(self.perm)))))
        _perm = [num for _, num in sorted(_perm_dict.items())]
        return SymmetricGroup(_perm)
    
    def __mul__(self, other):
        _perm = self(other.perm)
        return SymmetricGroup(_perm)

    def __eq__(self, other):
        return self.perm==other.perm
    
    def __pow__(self, num):

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