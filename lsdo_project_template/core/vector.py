import numpy as np

class Vector():
    """
    Base class used to store the entries inside a vector and perform basic opearations.

    Attributes
    ----------
    size : int
        Size of the vector
    data : np.ndarray
        The vector stored as a numpy array

    """
    # Methods
    # -------
    # __init__:
    #     Initialize
    # iadd:
    #     Add inplace
    # add:
    #     Add
    # scalar_mult:
    #     Scalar multiply
    # """

    def __init__(self, n, x=None):
        '''
        Initialize the vector class

        Parameters
        ----------
        n : int
            Size of the vector
        x : np.ndarray
            Initial value for the vector
        '''
        self.size = n
        if x is None:
            self.data = np.zeros((n,))
        elif x.size != n:
            raise ValueError("Input numpy array is not of the given shape")
        else:
            self.data=x


    def iadd(self, y):
        '''
        Add inplace a numpy vector to a Vector() object

        Parameters
        ----------
        y : np.ndarray
            Numpy vector to be added

        Examples
        --------
        >>> vec = Vector(10)
        >>> print(vec.data)
        >>> import numpy as np
        >>> x = np.ones((10,))
        >>> vec.iadd(x)
        >>> print(vec.data)

        See also
        --------
        add : Return the sum of input numpy vector with a Vector() object
        '''
        if y.size != self.size:
            raise ValueError("Input numpy array is not of the same shape")
        
        self.data += y

    def add(self, y):
        '''
        Return the sum of input numpy vector with the Vector() object

        Parameters
        ----------
        y : np.ndarray
            Numpy vector to be added

        Returns
        -------
        np.ndarray
            Sum of the input vector and the Vector() object
        
        Examples
        --------
        >>> vec = Vector(10)
        >>> print(vec.data)
        >>> import numpy as np
        >>> x = np.ones((10,))
        >>> y = vec.add(x)
        >>> print(y)

        See also
        --------
        iadd : Add inplace a numpy vector to a Vector() object

        Notes
        -----
        **Return values**

        `add()` method will return a *numpy* object whereas `iadd()` does not return anything
        '''
        if y.size != self.size:
            raise ValueError("Input numpy array is not of the same shape")
        
        return self.data + y

    def scalar_mult(self, c):
        '''
        Return a scalar multiple of the Vector() object as a numpy array

        Parameters
        ----------
        c: int or float
            Scalar to be multiplied

        Returns
        -------
        z : np.ndarray
            Scalar multiple of the Vector() object

        Examples
        --------
        >>> import numpy as np
        >>> vec = Vector(10, np.ones((10,)))
        >>> print(vec.data)
        >>> z = vec.scalar_mult(5.)
        >>> print(z)

        '''
        if isinstance(c, (int, float)):
            z = c * self.data
            return z

        else:
            raise TypeError("Input scalar is not of type 'int' or 'float'")