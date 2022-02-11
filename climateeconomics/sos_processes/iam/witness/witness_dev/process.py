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

from energy_models.core.energy_study_manager import DEFAULT_TECHNO_DICT
from energy_models.sos_processes.witness_sub_process_builder import WITNESSSubProcessBuilder
from energy_models.core.energy_process_builder import INVEST_DISCIPLINE_OPTIONS


class ProcessBuilder(WITNESSSubProcessBuilder):
    def __init__(self, ee, process_level='dev'):
        WITNESSSubProcessBuilder.__init__(
            self, ee)
        self.invest_discipline = INVEST_DISCIPLINE_OPTIONS[2]
        self.process_level = process_level

    def get_builders(self):

        chain_builders = []
        # retrieve energy process
        chain_builders_witness = self.ee.factory.get_builder_from_process(
            'climateeconomics.sos_processes.iam', 'witness_wo_energy_dev')
        chain_builders.extend(chain_builders_witness)

        # if one invest discipline then we need to setup all subprocesses
        # before get them
        techno_dict = DEFAULT_TECHNO_DICT

        chain_builders_energy = self.ee.factory.get_builder_from_process(
            'energy_models.sos_processes.energy.MDA', 'energy_process_v0_mda',
            techno_dict=self.techno_dict, invest_discipline=self.invest_discipline)

        chain_builders.extend(chain_builders_energy)

        if self.process_level != 'dev':
            land_use_path = 'climateeconomics.sos_wrapping.sos_wrapping_land_use.land_use.land_use_disc.LandUseDiscipline'
            chain_builders_land_use = self.ee.factory.get_builder_from_module(
                'Land_Use', land_use_path)
            chain_builders.append(chain_builders_land_use)

        # Update namespace regarding land use and energy mix coupling
        ns_dict = {'ns_land_use': f'{self.ee.study_name}.EnergyMix',
                   'ns_functions': f'{self.ee.study_name}.EnergyMix',
                   'ns_ref': f'{self.ee.study_name}.NormalizationReferences'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        self.ee.post_processing_manager.add_post_processing_module_to_namespace(
            'ns_witness',
            'climateeconomics.sos_wrapping.sos_wrapping_witness.post_proc_witness_optim.post_processing_witness_full')

        return chain_builders