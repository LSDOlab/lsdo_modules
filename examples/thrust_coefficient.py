from lsdo_modules.module.module import Module
from lsdo_modules.moduel_csdl.module_csdl import ModuleCSDL
import numpy as np
from python_csdl_backend import Simulator
from csdl import GraphRepresentation


# Create csdl modules
class RadiusCSDL(ModuleCSDL):
    def initialize(self):
        self.parameters.declare('scaling_factor')

    def define(self):
        s = self.parameters['scaling_factor']
        disk_area = self.register_module_input('disk_area')

        radius = (s * disk_area / np.pi)**0.5
        self.register_module_output('radius', radius, promotes=True)

class ThrustCSDL(ModuleCSDL):
    def initialize(self): 
        self.parameters.declare('rho') 

    def define(self):
        rho = self.parameters['rho']

        R = self.register_module_input('radius', shape=(1, ))
        self.print_var(R)
        C_T = self.register_module_input('C_T')
        rpm = self.register_module_input('rpm')
        
        n = rpm / 60
        D = 2 * R

        T = C_T * rho * n**2 * D**4
        self.register_module_output('thrust', T, promotes=True)

class ThrustComputationCSDL(ModuleCSDL):
    def initialize(self): 
        self.parameters.declare('scaling_factor')
        self.parameters.declare('rho') 

    def define(self):
        scaling_factor = self.parameters['scaling_factor']
        rho = self.parameters['rho']

        radius_module_csdl = RadiusCSDL(
            module=self.module,
            scaling_factor=scaling_factor,
        )
        # GraphRepresentation(radius_module_csdl)
        self.add_module(radius_module_csdl, 'radius_module')
        print('radius_module_inputs', radius_module_csdl.module_inputs)
        print('modules', self.sub_modules[0].module_inputs)
        print('\n')

        a = self.create_input('a', val=100)
        self.register_output('a_10', a/10)

        thrust_module_csdl = ThrustCSDL(
            module=self.module,
            rho=rho,
        )
        # GraphRepresentation(thrust_module_csdl)
        self.add_module(thrust_module_csdl, 'thrust_module')
        print('thrust_module_inputs', thrust_module_csdl.module_inputs)

        thrust = self.register_module_input('thrustt', val=2, shape=(1, ))
        self.register_module_output('thrust_test', thrust*1)


# define your module (pure python object)
class ThrustModule(Module):
    def __init__(self) -> None:
        super().__init__()
    
    def assemble_csdl(self):
        csdl_model = ThrustComputationCSDL(
            module=self,
            scaling_factor=1.5,
            rho=1.2,
        )
        graph = GraphRepresentation(csdl_model)
        return csdl_model


# class TestModule(Module):
#     def assemble_csdl(self):
#         csdl_model = RadiusCSDL(
#             module=self,
#             scaling_factor=1.5
#         )
#         print(csdl_model.promoted_vars)
#         print(csdl_model.module.promoted_vars)
#         return csdl_model
# test_module = TestModule()
# test_module.set_module_input('disk_area', val=4)

# test_csdl = test_module.assemble_csdl()
# print(test_csdl.promoted_vars)
# sim = Simulator(test_csdl)
# print(test_csdl.promoted_vars)
# sim.run()

# exit()

# set up the simulation 
thrust_module = ThrustModule()
thrust_module.set_module_input('disk_area', val=4.)
thrust_module.set_module_input('radius', val=None, computed_upstream=True)
thrust_module.set_module_input('C_T', val=0.25)
thrust_module.set_module_input('rpm', val=1200)

thrust_module_csdl = thrust_module.assemble_csdl()
print('\n')
print('module_inputs',thrust_module_csdl.sub_modules[0].module_inputs[0].name)
graph = GraphRepresentation(thrust_module_csdl)

# print(graph.module)
sim = Simulator(thrust_module_csdl)
print('module_inputs',thrust_module_csdl.sub_modules)
sim.run()
print(thrust_module_csdl.module.promoted_vars)
print('thrust', sim['thrust'])
print('thrust_test', sim['thrust_test'])
