'''
Copyright 2022 Airbus SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
from time import sleep
from shutil import rmtree
from pathlib import Path

from sos_trades_core.execution_engine.execution_engine import ExecutionEngine
from climateeconomics.sos_processes.iam.witness.witness.usecase_witness import Study
from numpy import array


class TestComparisonNR_GS(unittest.TestCase):
    """
    SoSDiscipline test class
    """
    #AbstractJacobianUnittest.DUMP_JACOBIAN = True
    obj_const = ['welfare_objective', 'temperature_objective', 'CO2_objective', 'ppm_objective',  'EnergyMix.methane.demand_violation', 'EnergyMix.hydrogen.gaseous_hydrogen.demand_violation', 'EnergyMix.biogas.demand_violation', 'EnergyMix.syngas.demand_violation', 'EnergyMix.liquid_fuel.demand_violation',
                 'EnergyMix.solid_fuel.demand_violation', 'EnergyMix.biomass_dry.demand_violation', 'EnergyMix.electricity.demand_violation', 'EnergyMix.biodiesel.demand_violation', 'EnergyMix.hydrogen.liquid_hydrogen.demand_violation', 'EnergyMix.primary_energies_production']

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.dirs_to_del = []
        self.namespace = 'MyCase'
        self.study_name = f'{self.namespace}'

    def tearDown(self):

        for dir_to_del in self.dirs_to_del:
            sleep(0.5)
            if Path(dir_to_del).is_dir():
                rmtree(dir_to_del)
        sleep(0.5)

    def test_01_check_comparison_nr_gs(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        repo = 'climateeconomics.sos_processes.iam.witness'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'witness')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{usecase.study_name}.sub_mda_class'] = 'GSNewtonMDA'
        full_values_dict[f'{usecase.study_name}.linearization_mode'] = 'adjoint'
        full_values_dict[f'{usecase.study_name}.tolerance'] = 1e-7
        full_values_dict[f'{usecase.study_name}.relax_factor'] = 0.99
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.display_treeview_nodes()
        self.ee.execute()

        ####################
        self.name = 'Test2'
        self.ee2 = ExecutionEngine(self.name)
        builder2 = self.ee2.factory.get_builder_from_process(
            repo, 'witness')

        self.ee2.factory.set_builders_to_coupling_builder(builder2)
        self.ee2.configure()
        usecase = Study(execution_engine=self.ee2)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{usecase.study_name}.sub_mda_class'] = 'MDAGaussSeidel'
        full_values_dict[f'{usecase.study_name}.max_mda_iter'] = 200
        full_values_dict[f'{usecase.study_name}.linearization_mode'] = 'adjoint'
        full_values_dict[f'{usecase.study_name}.tolerance'] = 1e-7
        full_values_dict[f'{usecase.study_name}.relax_factor'] = 0.99
        self.ee2.load_study_from_input_dict(full_values_dict)

        # self.ee2.display_treeview_nodes()
        self.ee2.execute()

        for output in self.obj_const:
            value_nr = self.ee.dm.get_value(
                f'Test.{output}')
            value_gs = self.ee2.dm.get_value(f'Test2.{output}')
            for value1, value2 in zip(value_nr, value_gs):
                self.assertAlmostEqual(
                    value1, value2, msg=f'{output} values are different', delta=1.0e-4)

        ####################
        self.name = 'Test3'
        self.ee3 = ExecutionEngine(self.name)
        builder3 = self.ee3.factory.get_builder_from_process(
            repo, 'witness')

        self.ee3.factory.set_builders_to_coupling_builder(builder3)
        self.ee3.configure()
        usecase = Study(execution_engine=self.ee3)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{usecase.study_name}.sub_mda_class'] = 'GSPureNewtonMDA'
        full_values_dict[f'{usecase.study_name}.max_mda_iter'] = 200
        full_values_dict[f'{usecase.study_name}.linearization_mode'] = 'adjoint'
        full_values_dict[f'{usecase.study_name}.tolerance'] = 1e-7
        full_values_dict[f'{usecase.study_name}.relax_factor'] = 0.99
        self.ee3.load_study_from_input_dict(full_values_dict)

        # self.ee2.display_treeview_nodes()
        self.ee3.execute()

        for output in self.obj_const:
            value_nr = self.ee.dm.get_value(
                f'Test.{output}')
            value_gs = self.ee3.dm.get_value(f'Test2.{output}')
            for value1, value2 in zip(value_nr, value_gs):
                self.assertAlmostEqual(
                    value1, value2, msg=f'{output} values are different', delta=1.0e-4)