from lsdo_modules.module.module_maker import ModuleMaker
from lsdo_modules.module.module import Module
from python_csdl_backend import Simulator
import csdl
import numpy as np


class TestModule1Maker(ModuleMaker):
    def define_module(self):
        a = self.register_module_input('a', val=5)
        b = self.register_module_input('b', val=0)

        c = a**2 + 2 * csdl.cos(b)
        self.register_module_output('c', c, promotes=True)

        x = self.register_module_output('x', shape=(2, ), promotes=True)
        x[0] = 2 * a
        x[1] = 1 + b
        
        print('declare_vars', self.module_info)


class TestModule2Maker(ModuleMaker):
    def define_module(self):
        c = self.register_module_input('c', shape=(1, ))

        d = c**(1/3)
        self.register_module_output('d', d, promotes=True)

class TestModuleMaker(ModuleMaker):
    def define_module(self):
        print(self.module)
        test_module_1 = TestModule1Maker(module=self.module)
        self.add_module(test_module_1, 'test_module_1')
        print('module_promoted_vars', test_module_1.promoted_vars)
        print('module_inputs', test_module_1.module_inputs)
        
        test_module_2 = TestModule2Maker(module=None)
        self.add_module(test_module_2, 'test_module_2')
        print('module_promoted_vars', test_module_2.promoted_vars)
        print('module_inputs', test_module_2.module_inputs)


class TestModule(Module):    
    def assemble_csdl(self):
        module_maker = TestModuleMaker(
            module=self,
        )
        return module_maker.assemble_module()


test_module = TestModule()

test_module.set_module_input('a', val=5, dv_flag=True)
test_module.set_module_input('b', val=0)
test_module_csdl_model = test_module.assemble_csdl()

sim = Simulator(test_module_csdl_model)
sim.run()
print(sim['d'])
print(sim['x'])
