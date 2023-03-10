from csdl import Model
import numpy as np


class ModuleCSDL(Model):
    """
    Class acting as a liason between CADDEE and CSDL. 
    The API mirrors that of the CSDL Model class. 
    """ 
    def __init__(self, **kwargs):
        # Option 1: 'module' is a required positional argument of the constructor
        # self.module = module
        # super().__init__(**kwargs)

        # Option 2: 'module' is part of kwargs (not required)
        self.module = kwargs['module']
        self.promoted_vars = list()
        self.inputs_list = list()
        kwargs.pop('module', 0)
        super().__init__(**kwargs)
        #     Disadvantages:
        #           1) Will not throw an error when  module is not passed into 
        #           the constructor upon instantiation 
        #           2) Need to pop 'module' from kwargs before calling 
        #           super().__init__(**kwargs)

        self.module_created_inputs = dict()
        self.module_declared_vars = dict()
        self.module_registered_outputs = dict()
        self.module_created_outputs = dict()
        self.objective = dict()
        self.design_variables = dict()
        self.design_constraints = dict()
        self.sub_modules = dict()
        self.connections = list()
        

    
    def register_module_input(
            self, 
            name: str,
            val=1.0,
            shape=(1, ),
            units=None,
            desc='',
        ):

        # Check if the variable set by the user when calling 'set_module_input()' 
        # matches what the variable defined by the (solver) developer when calling
        # 'self.regsiter_module_input'
        if name not in self.module.inputs:
            raise Exception(f"CSDL variable '{name}' is not found within the set module inputs: {list(self.module.inputs.keys())}. When calling 'set_module_input()', make sure the string matches '{name}'.")
        else:
            mod_var = self.module.inputs[name]
            mod_var_val = mod_var['val']
            if mod_var_val:
                pass
            else:
                mod_var_val = val
            
        # Check whether the sizes of the set module input and the to be 
        # created/declares CSDL variable match in size
        if not isinstance(mod_var_val, (float, int)) and np.size(mod_var_val) != np.prod(shape):
            raise Exception(f'Size mismatch- module input {name} has size {np.size(mod_var)} but the corresponding csdl variable has shape {shape}')
        elif np.size(mod_var_val) == 1:
            pass
        else:
            mod_var_val = mod_var_val.reshape(shape)
        
        # Check whether variable is a float, int or array and assign 
        # shape accordingly
        if isinstance(mod_var_val, (float, int)) and shape is (1, ):
            mod_var_shape = (1, )
        elif isinstance(mod_var_val, (float, int)) and shape is not (1, ): # corresponds to expanding a scaler to another scaler
            mod_var_shape = shape
        elif mod_var_val is None:
            mod_var_shape = shape,
        else:
            mod_var_shape = mod_var_val.shape
                
        mod_var_units = mod_var['units']    

        if mod_var['computed_upstream'] is True:
            self.module.csdl_inputs.append(name)
            input_variable = self.declare_variable(
                name=name, 
                val=mod_var_val,
                shape=mod_var_shape,
                units=mod_var_units,
                desc=desc,
            )
        elif mod_var['computed_upstream'] is False and mod_var['dv_flag'] is False:
            self.module.csdl_inputs.append(name)
            input_variable = self.create_input(
                name=name,
                val=mod_var_val,
                shape=mod_var_shape,
                units=mod_var_units,
                desc=desc,
            )
        elif mod_var['computed_upstream'] is False and mod_var['design_variable'] is True:
            self.module.csdl_inputs.append(name)
            input_variable = self.create_input(
                name=name,
                val=mod_var_val,
                shape=mod_var_shape,
                units=mod_var_units,
                desc=desc,
            )
            lower = mod_var['lower']
            upper = mod_var['upper']
            scaler = mod_var['scaler']
            self.add_design_variable(name, lower=lower, upper=upper, scaler=scaler)
        else:
            raise NotImplementedError
        
        return input_variable
    
    def register_module_output(
            self, 
            name: str, 
            mod_var=None, 
            promotes: bool=False,
            shape=None,
        ):
        """
        Register a module variable as a csdl output variable.
        Calls the method `register_output` of the csdl `Model` class or 
        the `create_ouput` method. 

        Parameters
        ----------
        `name : str`
            String name of the module and csdl variable

        `var : Output`
            csdl output variable

        `promotes : bool`
            If true, the registered output will be promoted if the model that 
            contains the output is added as a submodel. The default is `False`.
        
        `shape : Tuple[int]`
            The shape of the output. Can only be `not None` if the user wants to
            create the csdl variable with the `create_output` method of the csdl
            `Model` class. Otherwise the shape of the output variable will be 
            determined by the variables used in the operations that compute the 
            output. The default is `None`
        """

        # Check if the method key words set by the user make sense
        if mod_var is None and shape is None:
            raise Exception(f"Set 'mod_var' key word or specify a shape to create an output that is indexable")
        elif mod_var is not None and shape is not None:
            raise Exception(f"Attempting to register {name} as an output while specifying a shape. A shape can only be specified if 'mod_var' is 'None'.")
        elif mod_var is None and shape is not None:
            output_variable = self.create_output(name=name, shape=shape)
        else:
            if promotes is True:
                print('PROMOTES is TRUE')
                self.promoted_vars.append(name)
                self.module.promoted_vars.append(name)
            output_variable = self.register_output(name=name, var=mod_var)
        
        # if promotes is True:
        #     print('PROMOTES is TRUE')
        #     self.promoted_vars.append(name)
        # else:
        #     pass
        
        return output_variable
    
    def add_module(
            self,
            submodule,
            name,
            promote_all : bool = False,
        ): 
        """
        Add a submodule to a parent module.

        Calls the `add` method of the csld `Model` class.
        """
        # Two options for promotions 
        # (by default, promotions are suppressed when adding submodules):
        # 1) Promote the entire submodel
        if promote_all is True:
            self.add(submodule, name)
        # 2) Only promote output variable that were registered
        #    with register_module_output(name, mod_var, promotes=True)
        elif promote_all is False:
            print(f'promoted variables for module {self.module}', self.module.promoted_vars)
            print(self.module.csdl_inputs)
            # self.module.promoted_vars = list()
            self.module.csdl_inputs = list()
            self.add(submodule, name, promotes=['radius', 'thrust'])#self.module.promoted_vars)
        
        pass

    def connect_modules(self, a: str, b: str):
        """
        Connect variables between modules. 

        Calls the `connect` method of the csdl `Model` class.
        """
        self.connect(a, b)
    

