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
        disk_area = self.register_module_input('disk_area', shape=(1, ))

        radius = (s * disk_area / np.pi)**0.5
        self.register_module_output('radius', radius)

class ThrustCSDL(ModuleCSDL):
    def initialize(self): 
        self.parameters.declare('rho') 

    def define(self):
        rho = self.parameters['rho']

        R = self.register_module_input('radius', shape=(1, ))
        C_T = self.register_module_input('C_T', shape=(1, ))
        rpm = self.register_module_input('rpm', shape=(1, ))
        
        n = rpm / 60
        D = 2 * R

        T = C_T * rho * n**2 * D**4
        self.register_module_output('thrust', T)

class ThrustComputationCSDL(ModuleCSDL):
    def initialize(self): 
        self.parameters.declare('scaling_factor')
        self.parameters.declare('rho') 

    def define(self):
        scaling_factor = self.parameters['scaling_factor']
        rho = self.parameters['rho']

        self.register_module_input('disk_area', shape=(1, ))
        radius_module_csdl = RadiusCSDL(
            # module=self.module,
            scaling_factor=scaling_factor,
        )
        self.add_module(radius_module_csdl, 'radius_module')

        C_T = self.register_module_input('C_T', shape=(1, ))
        rpm = self.register_module_input('rpm', shape=(1, ))
        thrust_module_csdl = ThrustCSDL(
            # module=self.module,
            # sub_modules=self.sub_modules,
            rho=rho,
        )
        self.add_module(thrust_module_csdl, 'thrust_module')

        thrust = self.register_module_input('thrust',  shape=(1, ))
        self.register_module_output('T', thrust**0.9)


# define your module (pure python object)
class ThrustModule(Module):
    def __init__(self) -> None:
        super().__init__()
    
    def assemble_csdl(self):
        csdl_model = ThrustComputationCSDL(
            module=self,
            scaling_factor=1.5,
            rho=1.2,
            name='Thrust Computation',
        )
        graph = GraphRepresentation(csdl_model)
        return csdl_model



# set up the simulation 
thrust_module = ThrustModule()
thrust_module.set_module_input('disk_area', val=4.)
thrust_module.set_module_input('C_T', val=0.25)
thrust_module.set_module_input('rpm', val=1200)

thrust_module_csdl = thrust_module.assemble_csdl()
print('\n')
print('module_inputs',thrust_module_csdl.module_inputs)
print('module_outputs',thrust_module_csdl.module_outputs)
print('sub_modules', thrust_module_csdl.sub_modules['radius_module']['inputs'])
print('sub_modules', thrust_module_csdl.sub_modules['thrust_module']['inputs'])
# print('sub_module_inputs',thrust_module_csdl.sub_modules[1].module_inputs)
# print('module_inputs', thrust_module_csdl.module_outputs)
# graph = GraphRepresentation(thrust_module_csdl)
thrust_module_csdl.visualize_implementation()
exit()
# print(graph.module)
sim = Simulator(thrust_module_csdl)
# print('module_inputs',thrust_module_csdl.sub_modules)
sim.run()
# print(thrust_module_csdl.module.promoted_vars)
print('module_outputs',thrust_module_csdl.module_outputs)
print('Promoted vars', thrust_module_csdl.promoted_vars)
print('thrust', sim['thrust'])
print('T', sim['T'])
print('rpm', sim['rpm'])
