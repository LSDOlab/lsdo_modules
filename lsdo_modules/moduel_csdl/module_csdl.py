from csdl import Model
import numpy as np
from csdl import GraphRepresentation
import warnings
from lsdo_modules.utils.make_xdsm import make_xdsm
from itertools import count


def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return 'UserWarning: ' + str(msg) + '\n'
warnings.formatwarning = custom_formatwarning


class ModuleCSDL(Model):
    """
    Class acting as a liason between CADDEE and CSDL. 
    The API mirrors that of the CSDL Model class. 
    """ 
    _ids = count(0)
    def __init__(self, module=None, sub_modules=None, name=None, **kwargs):
        self.id = next(self._ids)
        self.module = module
        self.sub_modules_csdl = sub_modules
        self.name = name
        self.promoted_vars = list()
        
        self.module_inputs = dict()
        self.module_declared_vars = dict()
        self.module_outputs = dict()
        self.sub_modules = dict()
        self._module_output_names = list()
        self._auto_iv = list()
        
        super().__init__(**kwargs)

        self.objective = dict()
        self.design_variables = dict()
        self.design_constraints = dict()
        self.connections = list()
        

    
    def register_module_input(
            self, 
            name: str,
            val=1.0,
            shape=(1, ),
            units=None,
            desc='',
            importance=0,
        ):
        print('dev_declared_input', name)
        # If there is a module associated with the ModuleCSDL instance
        # The created CSDL variable will be of type Input
        if self.module:
            # Check if the variable set by the user when calling 'set_module_input()' 
            # matches what the variable defined by the (solver) developer when calling
            # 'self.regsiter_module_input' If not, check if the variable is an output 
            # of an upstreams model. If not raise a warning and make the variable
            # an instance of DeclaredVariable
            if name not in self.module.inputs:
                # Get all module outputs of upstream modules and append to a list
                if self.sub_modules_csdl is not None:
                    for sub_module in {**self.sub_modules_csdl, **self.sub_modules}.values():
                        module_outputs = sub_module['outputs']
                        self._module_output_names += [name for name in module_outputs]
                else:
                    for sub_module in self.sub_modules.values():
                        module_outputs = sub_module['outputs']
                        self._module_output_names += [name for name in module_outputs]
                # Check if the variable is computed in an upstream module
                if name in self._module_output_names:
                    input_variable = self.declare_variable(name=name, shape=shape)
                    self.module_declared_vars[name] = dict(
                        shape=shape, 
                        importance=importance)
                # Raise warning if not and store variable name, shape, val in auto_iv
                else:
                    input_variable = self.declare_variable(name=name, val=val, shape=shape)
                    self._auto_iv.append((name, val, shape))
                    self.module_declared_vars[name] = dict(
                        shape=shape, 
                        importance=importance)
                    warnings.warn(f"CSDL variable '{name}' is neither a user-defined input (specified with the 'set_module_input' method) nor an output that is computed upstream (all upstream outputs: {self._module_output_names}). This variable will by of type 'DeclaredVariable' with shape {shape} and value {val}")
            
            # else: the variable is set by the user via 'set_module_input'
            else:
                mod_var = self.module.inputs[name]
                mod_var_val = mod_var['val']
                
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
                if isinstance(mod_var_val, (float, int)) and shape == (1, ):
                    mod_var_shape = (1, )
                elif isinstance(mod_var_val, (float, int)) and shape != (1, ): # corresponds to expanding a scaler to another scaler
                    mod_var_shape = shape
                else:
                    mod_var_shape = mod_var_val.shape
                        
                mod_var_units = mod_var['units']    

                if mod_var['dv_flag'] is False:
                    input_variable = self.create_input(
                        name=name,
                        val=mod_var_val,
                        shape=mod_var_shape,
                        units=mod_var_units,
                        desc=desc,
                    )
                    self.module_inputs[name] = dict(
                        shape=shape, 
                        importance=importance)
                    

                elif mod_var['dv_flag'] is True:
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
                    self.module_inputs[name] = dict(
                        shape=shape, 
                        importance=importance)
                else:
                    raise NotImplementedError
        
        # else: if no module is provided
        # In this case, all variables will be declared variables 
        else: 
            input_variable = self.declare_variable(
                name=name, 
                val=val, 
                shape=shape, 
                units=units, 
                desc=desc,
            )
            self.module_declared_vars[name] = dict(
                shape=shape, 
                importance=importance)

        return input_variable
    
    def register_module_output(
            self, 
            name: str, 
            var=None, 
            shape=None,
            importance=0,
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
        if var is None and shape is None:
            raise Exception(f"Set 'mod_var' key word or specify a shape to create an output that is indexable")
        elif var is not None and shape is not None:
            raise Exception(f"Attempting to register {name} as an output while specifying a shape. A shape can only be specified if 'mod_var' is 'None'.")
        elif var is None and shape is not None:
            output_variable = self.create_output(name=name, shape=shape)
            self.module_outputs[name] = dict(
                shape=shape,
                importance=importance,
            )
        else: 
            output_variable = self.register_output(name=name, var=var)
            self.module_outputs[name] = dict(
                shape=var.shape,
                importance=importance,
            )
        
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
            promotes=None,
            increment : int = 1
        ):

        if self.id == 0:
            pass
        elif self.id == 1:
            raise Exception('Weird nesting of ModuleCSDL sub-classes.')
        elif self.id > 0:
            increment += (self.id - 1)
        else:
            raise NotImplementedError
        """
        Add a submodule to a parent module.

        Calls the `add` method of the csld `Model` class.
        """
        GraphRepresentation(submodule)
        # submodule.define()
        
        # Need to increment each input and output of the sub_module 
        for input in submodule.module_inputs.values():
            input['importance'] += increment
        
        for declared_var in submodule.module_declared_vars.values():
            declared_var['importance'] += increment 

        for output in submodule.module_outputs.values():
            output['importance'] += increment 

        # 1) Only promote a subset of user-defined variables
        if promotes is not None:
            self.add(submodule, name, promotes=promotes)
            self.promoted_vars += promotes
            self.sub_modules[name] = dict(
                inputs=submodule.module_inputs,
                declared_vars=submodule.module_declared_vars,
                outputs=submodule.module_outputs,
                promoted_vars=promotes,
                submodules=submodule.sub_modules,
            )
        
        # 2) Promote the entire submodel
        else:
            self.add(submodule, name)
            self.promoted_vars += list(submodule.module_inputs.keys()) + list(submodule.module_outputs.keys())
            self.sub_modules[name] = dict(
                inputs=submodule.module_inputs,
                declared_vars=submodule.module_declared_vars,
                outputs=submodule.module_outputs,
                promoted_vars=list(submodule.module_inputs.keys()) + list(submodule.module_outputs.keys()),
                submodules=submodule.sub_modules,
            )
        # print('sub_module', self.sub_modules)

    def connect_modules(self, a: str, b: str):
        """
        Connect variables between modules. 

        Calls the `connect` method of the csdl `Model` class.
        """
        self.connect(a, b)


    def visualize_implementation(self, importance=0):
        from pyxdsm.XDSM import (
            XDSM,
            OPT,
            SUBOPT,
            SOLVER,
            DOE,
            IFUNC,
            FUNC,
            GROUP,
            IGROUP,
            METAMODEL,
            LEFT,
            RIGHT,
        )
        def find_up_stream_module(list_of_tuples, inputs_from_upstream):
            modules = []
            for input_from_upstream in inputs_from_upstream:
                for module, output in list_of_tuples:
                    if input_from_upstream == output:
                        modules.append(module)
            return modules

        def find_inputs_outputs(dictionary, inp_out_list=[], inp_out='inputs'):
            for k, v in dictionary.items():
                if k == inp_out:
                    for k2, v2 in v.items():
                        if v2['importance'] <= (importance+1):
                            inp_out_list.append(k2)
                        else:
                            pass
                    else:
                        pass
                elif isinstance(v, dict):
                    if inp_out_list:
                        find_inputs_outputs(v, inp_out_list, inp_out=inp_out)
                    else:
                        find_inputs_outputs(v, inp_out_list, inp_out=inp_out)
                else:
                    pass
            
            return inp_out_list
        # TODO: dsm connections for nesting 
        def unpack_sub_modules(dictionary, importance_outputs = []):
            for module, module_values in dictionary.items():
                # Collect all module outputs with importance less than
                # or equal to the importance specified by the user
                for sub_mod_out, sub_mod_out_par in module_values['outputs'].items():
                    if sub_mod_out_par['importance'] <= importance:
                        importance_outputs.append((module, sub_mod_out))
                # If there are "important" outputs call 'add_system'
                if importance_outputs:
                    print(module)
                    print(importance_outputs)
                   
                    x.add_system(module, FUNC, generate_dsm_text(module))
                    
                    # Add any inputs defined by the user
                    inputs_from_user = list(set(user_module_inputs) & set(list(module_values['inputs'].keys())))
                    if inputs_from_user:
                        x.add_input(module, [generate_dsm_text(connection) for connection in inputs_from_user])
                    
                    # Check if there are any inputs from upstream modules
                    inputs_from_upstream = list(set(list(module_values['declared_vars'].keys())) & set([t[1] for t in importance_outputs]))
                    print(inputs_from_upstream)
                    print('\n')
                    if inputs_from_upstream:
                        upstream_modules = find_up_stream_module(importance_outputs, inputs_from_upstream)
                        for upstream_module in upstream_modules:
                            x.connect(upstream_module, module, [generate_dsm_text(connection) for connection in inputs_from_upstream])
                if module_values['submodules']:
                    unpack_sub_modules(module_values['submodules'], importance_outputs=[])

            return module, module_values


        x = XDSM()
        from examples.viz_test import generate_dsm_text
        
        # print(find_inputs_outputs(self.sub_modules, inp_out_list=[], inp_out='inputs'))
        # print(find_inputs_outputs(self.sub_modules, inp_out_list=[], inp_out='outputs'))
        # exit()
        
        user_module_inputs =  find_inputs_outputs(self.sub_modules,inp_out_list=[], inp_out='inputs')
                                                  
        if importance == 0:
            x.add_system(self.name, OPT, generate_dsm_text(self.name))
            parent_module_inputs = list(self.module_inputs.keys())
            parent_module_outputs = list(self.module_outputs.keys())
            if not parent_module_inputs:
                parent_module_inputs = user_module_inputs
            if not parent_module_outputs:
                parent_module_outputs = find_inputs_outputs(self.sub_modules[list(self.sub_modules)[-1]], inp_out_list=[],inp_out='outputs')

            x.add_input(self.name, [generate_dsm_text(input) for input in parent_module_inputs])
            x.add_output(self.name, [generate_dsm_text(input) for input in parent_module_outputs], side=RIGHT)
        
        else:
            module, module_values = unpack_sub_modules(self.sub_modules)
            # for module, module_values in self.sub_modules.items():
                # pass

            # Lastly, show outputs of last module
            x.add_output(module, [generate_dsm_text(output) for output in list(module_values['outputs'].keys())], side=RIGHT)
            # print(list(module_values['outputs'].keys()))
        exit()
        x.write(f'{self.name}_xdsm')


    


