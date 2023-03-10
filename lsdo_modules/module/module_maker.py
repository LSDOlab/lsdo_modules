from typing import Any, Dict, List, Set, Tuple, Union
from csdl.lang.declared_variable import DeclaredVariable
from csdl.lang.output import Output
from csdl.lang.input import Input
from csdl.lang.concatenation import Concatenation
from csdl.operations import *
from csdl.utils.check_default_val_type import check_default_val_type
from csdl import Model


class ModuleMaker:
    def __init__(self, module, **kwargs) -> None:
        self.declared_variables = list()
        self.inputs = list()
        self.registered_outputs = list()
        self.created_outputs = list()
        
        self.module_info = list()
        self.module_inputs = list()
        self.module_outputs = list()
        self.promoted_vars = list()
        self.design_variables = dict()
        self.module = module #kwargs['module']

    def initialize_module(self):
        """
        User-defined method
        """
        pass

    def define_module(self): 
        """
        User-define method
        """
        pass

    def register_module_input(
        self,
        name: str,
        val=1.0,
        shape=(1, ),
        src_indices=None,
        flat_src_indices=None,
        units=None,
        desc='',
        tags=None,
        shape_by_conn=False,
        copy_shape=None,
        distributed=None,
    ):
        
        if self.module is None:
            # print('NO MODULE')
            v = DeclaredVariable(
                name,
                val=check_default_val_type(val),
                shape=shape,
                src_indices=src_indices,
                flat_src_indices=flat_src_indices,
                units=units,
                desc=desc,
                tags=tags,
                shape_by_conn=shape_by_conn,
                copy_shape=copy_shape,
                distributed=distributed,
            )
            self.module_info.append(v)
            self.module_inputs.append(name)
            return v
        
        else:
            # print('YES MODULE')
            if name not in self.module.inputs:
                raise Exception(f"CSDL variable '{name}' is not found within the set module inputs: {list(self.module.inputs.keys())}. When calling 'set_module_input()', make sure the string matches '{name}'.")
            else:
                mod_var = self.module.inputs[name]
                mod_var_units = mod_var['units']
                mod_var_val = mod_var['val']
                if isinstance(mod_var_val, (int, float)):
                    mod_var_shape = (1, )
                else:
                    mod_var_shape = mod_var_val.shape

                

            if mod_var['computed_upstream'] is False and mod_var['dv_flag'] is False:
                i = Input(
                    name,
                    val=check_default_val_type(mod_var_val),
                    shape=mod_var_shape,
                    units=mod_var_units,
                    desc=desc,
                    tags=tags,
                    shape_by_conn=shape_by_conn,
                    copy_shape=copy_shape,
                    distributed=distributed,
                )
                self.module_info.append(i)
                self.module_inputs.append(name)
                return i

            elif mod_var['computed_upstream'] is False and mod_var['dv_flag'] is True:
                i = Input(
                    name,
                    val=check_default_val_type(mod_var_val),
                    shape=mod_var_shape,
                    units=mod_var_units,
                    desc=desc,
                    tags=tags,
                    shape_by_conn=shape_by_conn,
                    copy_shape=copy_shape,
                    distributed=distributed,
                )

                self.design_variables[name] = {
                    'lower': mod_var['lower'],
                    'upper': mod_var['upper'],
                    'scaler': mod_var['scaler']
                }
                self.module_info.append(i)
                self.module_inputs.append(name)
                return i 

            elif mod_var['computed_upstream'] is True:
                v = DeclaredVariable(
                    name,
                    val=check_default_val_type(mod_var_val),
                    shape=mod_var_shape,
                    src_indices=src_indices,
                    flat_src_indices=flat_src_indices,
                    units=mod_var_units,
                    desc=desc,
                    tags=tags,
                    shape_by_conn=shape_by_conn,
                    copy_shape=copy_shape,
                    distributed=distributed,
                )
                self.module_info.append(v)
                self.module_inputs.append(name)
                return v
            
            else:
                raise NotImplementedError
                
        
    def register_module_output(self, 
        name: str, 
        var: Output=None, 
        val=1.0, 
        shape=None, 
        units=None,
        res_units=None,
        desc='',
        lower=None,
        upper=None,
        ref=1.0,
        ref0=0.0,
        res_ref=1.0,
        tags=None,
        shape_by_conn=False,
        copy_shape=None,
        distributed=None,
        promotes: bool = False): 
        
        if shape and var:
            raise Exception(f'Attempting to create output with shape {shape}, while providing a variable to register as an output.')
    

        if shape:
            c = Concatenation(
            name,
            val=check_default_val_type(val),
            shape=shape,
            units=units,
            desc=desc,
            tags=tags,
            shape_by_conn=shape_by_conn,
            copy_shape=copy_shape,
            res_units=res_units,
            lower=lower,
            upper=upper,
            ref=ref,
            ref0=ref0,
            res_ref=res_ref,
            distributed=distributed,
        )
            # self.register_output(name, c)
            self.module_info.append(c)
            self.module_outputs.append(name)
            if promotes is True:
                self.promoted_vars.append(name)

            return c
        else:
            if not isinstance(var, Output):
                raise TypeError(
                    'Can only register Output object as an output. Received type {}.'
                    .format(type(var)))
            else:
                if var in self.registered_outputs:
                    raise ValueError(
                        "Cannot register output twice; attempting to register "
                        "{} as {}.".format(var.name, name))
                if name in [r.name for r in self.registered_outputs]:
                    raise ValueError(
                        "Cannot register two outputs with the same name; attempting to register two outputs with name {}."
                        .format(name))
                if name in [r.name for r in self.inputs]:
                    raise ValueError(
                        "Cannot register output with the same name as an input; attempting to register output named {} with same name as an input."
                        .format(name))
                if name in [r.name for r in self.declared_variables]:
                    raise ValueError(
                        "Cannot register output with the same name as a declared variable; attempting to register output named {} with same name as a declared variable."
                        .format(name))

            var.name = name
            self.module_info.append(var)
            self.module_outputs.append(name)
            if promotes is True:
                self.promoted_vars.append(name)

            return var 

    def add_module(
        self,
        submodule,
        name=None,
        promote_all=False
        # promotes=None
    ):
        csdl_model = submodule.assemble_module()
        self.promoted_vars += submodule.promoted_vars
        sub_module_info = {
            'csdl_model': csdl_model,
            'sub_module': submodule,
            'name': name,
            'promote_all': promote_all,
            'all_promoted_vars': submodule.promoted_vars
        }
        self.module_info.append(sub_module_info)
        
        return sub_module_info


    def assemble_module(self): 
        self.define_module()
        all_promoted_vars = self.promoted_vars
        design_variables = self.design_variables
        model = Model()
        for entry in self.module_info:
            # Inputs
            if isinstance(entry, DeclaredVariable):
                model.declare_variable(entry.name, entry.val, entry.shape)
            elif isinstance(entry, Input):
                model.create_input(name=entry.name, val=entry.val, shape=entry.shape)
                if entry.name in design_variables:
                    dv = design_variables[entry.name]
                    model.add_design_variable(
                        dv_name=entry.name,
                        lower=dv['lower'],
                        upper=dv['upper'],
                        scaler=dv['scaler'],
                    )
                
            # Outputs
            elif isinstance(entry, Output):
                model.register_output(entry.name, entry)
            elif isinstance(entry, Concatenation):
                model.register_output(name=entry.name, val=entry)
            # Adding submodel
            elif isinstance(entry, dict):
                csdl_submodel = entry['csdl_model']
                submodule = entry['sub_module']
                module_inputs = submodule.module_inputs
                name = entry['name']
                promote_all = entry['promote_all']
                if promote_all is True:
                    promotes=None
                else:
                    promotes = submodule.promoted_vars + [e for e in all_promoted_vars if e in module_inputs]

                model.add(csdl_submodel, name, promotes)
            else:
                raise NotImplementedError

            

        return model
        # class CSDLModel(Model):
        #     def initialize(self): pass

        #     def define(self): 
        #         for var in self.

