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

from sos_trades_core.tools.post_processing.post_processing_factory import PostProcessingFactory
from sos_trades_core.study_manager.study_manager import StudyManager

from os.path import join, dirname
from numpy import asarray, arange, array
import pandas as pd
import numpy as np
from sos_trades_core.execution_engine.func_manager.func_manager import FunctionManager
from sos_trades_core.execution_engine.func_manager.func_manager_disc import FunctionManagerDisc
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from climateeconomics.sos_processes.iam.witness.sectorization_process.usecase import Study as witness_sect_usecase

AGGR_TYPE = FunctionManagerDisc.AGGR_TYPE
AGGR_TYPE_SUM = FunctionManager.AGGR_TYPE_SUM
AGGR_TYPE_SMAX = FunctionManager.AGGR_TYPE_SMAX


class Study(StudyManager):

    def __init__(self, year_start=2000, year_end=2020, time_step=1, name='', execution_engine=None, run_usecase=False):
        super().__init__(__file__, execution_engine=execution_engine, run_usecase=run_usecase)
        self.study_name = 'usecase'
        self.macro_name = '.Macroeconomics'
        self.obj_name = '.Objectives'
        self.coupling_name = ".Sectorization_Eval"
        self.optim_name = ".SectorsOpt"
        self.ns_industry = self.study_name + self.optim_name + self.coupling_name + self.macro_name +'.Industry'
        self.ns_agriculture = self.study_name + self.optim_name + self.coupling_name + self.macro_name + '.Agriculture'
        self.ns_services = self.study_name + self.optim_name + self.coupling_name + self.macro_name + '.Services'
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        self.witness_sect_uc = witness_sect_usecase(self.year_start, self.year_end, self.time_step, execution_engine=execution_engine)


    def setup_usecase(self):
        
        ns = self.study_name
        ns_coupling = self.study_name + self.optim_name + self.coupling_name
        ns_above = self.study_name + self.optim_name 
        #Optim param
        INEQ_CONSTRAINT = FunctionManager.INEQ_CONSTRAINT
        OBJECTIVE = FunctionManager.OBJECTIVE

        dspace_dict = {'variable': ['output_alpha_services_in', 'prod_gr_start_services_in',' decl_rate_tfp_services_in','prod_start_services_in', 
                                    'energy_eff_k_services_in', 'energy_eff_cst_services_in', 'energy_eff_xzero_services_in','energy_eff_max_services_in',
                                    'output_alpha_agri_in', 'prod_gr_start_agri_in',' decl_rate_tfp_agri_in','prod_start_agri_in', 
                                    'energy_eff_k_agri_in', 'energy_eff_cst_agri_in', 'energy_eff_xzero_agri_in','energy_eff_max_agri_in',
                                    'output_alpha_indus_in', 'prod_gr_start_indus_in',' decl_rate_tfp_indus_in','prod_start_indus_in', 
                                    'energy_eff_k_indus_in', 'energy_eff_cst_indus_in', 'energy_eff_xzero_indus_in','energy_eff_max_indus_in',
                                    ],
                       'value': [[0.87], [0.02], [0.02],[0.27], 
                                 [0.05], [0.98], [2012.0], [3.51], 
                                 [0.87], [0.02], [0.02],[0.27], 
                                 [0.05], [0.98], [2012.0], [3.51], 
                                 [0.87], [0.02], [0.02],[0.27], 
                                 [0.05], [0.98], [2012.0], [3.51]],
                       'lower_bnd': [[0.5], [0.001], [0.00001], [0.01],
                                     [0.0], [0.0],[1900.0], [1.0],
                                      [0.5], [0.001], [0.00001], [0.01],
                                      [0.0], [0.0],[1900.0], [1.0],
                                      [0.5], [0.001], [0.00001], [0.01],
                                      [0.0], [0.0],[1900.0], [1.0]],
                       'upper_bnd': [[0.99], [0.2], [0.1],[2],
                                      [1.0], [2.0],[2050.0], [8.0],
                                      [0.99], [0.2], [0.1],[2],
                                      [1.0], [2.0],[2050.0], [8.0],
                                      [0.99], [0.2], [0.1],[2],
                                      [1.0], [2.0],[2050.0], [8.0]]}
 
        dspace = pd.DataFrame(dspace_dict)
        
        design_var_descriptor = {'output_alpha_services_in': {'out_name': 'output_alpha','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'prod_gr_start_services_in': {'out_name': 'productivity_gr_start','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'decl_rate_tfp_services_in': {'out_name': 'decline_rate_tfp','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'prod_start_services_in': {'out_name': 'productivity_start', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'energy_eff_k_services_in': {'out_name': 'energy_eff_k', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'energy_eff_cst_services_in': {'out_name': 'energy_eff_cst', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'energy_eff_xzero_services_in': {'out_name': 'energy_eff_xzero', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'energy_eff_max_services_in': {'out_name': 'energy_eff_max', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_services}'},
                                'output_alpha_agri_in': {'out_name': 'output_alpha','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'prod_gr_start_agri_in': {'out_name': 'productivity_gr_start','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'decl_rate_tfp_agri_in': {'out_name': 'decline_rate_tfp','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'prod_start_agri_in': {'out_name': 'productivity_start', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'energy_eff_k_agri_in': {'out_name': 'energy_eff_k', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'energy_eff_cst_agri_in': {'out_name': 'energy_eff_cst', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'energy_eff_xzero_agri_in': {'out_name': 'energy_eff_xzero', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'energy_eff_max_agri_in': {'out_name': 'energy_eff_max', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_agriculture}'},
                                'output_alpha_indus_in': {'out_name': 'output_alpha','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'prod_gr_start_indus_in': {'out_name': 'productivity_gr_start','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'decl_rate_tfp_indus_in': {'out_name': 'decline_rate_tfp','out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'prod_start_indus_in': {'out_name': 'productivity_start', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'energy_eff_k_indus_in': {'out_name': 'energy_eff_k', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'energy_eff_cst_indus_in': {'out_name': 'energy_eff_cst', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'energy_eff_xzero_indus_in': {'out_name': 'energy_eff_xzero', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},
                                'energy_eff_max_indus_in': {'out_name': 'energy_eff_max', 'out_type': 'float', 'key': 'value',
                                                              'namespace_in': f'{ns_above}','namespace_out': f'{self.ns_industry}'},         
                             }

        disc_dict = {}
        #disc_dict[f'{ns_above}.DesignVariables.design_var_descriptor'] = design_var_descriptor
        disc_dict[f'{ns_coupling}.DesignVariables.design_var_descriptor'] = design_var_descriptor

        # Optim inputs
        disc_dict[f'{ns_above}.max_iter'] = 100
        disc_dict[f'{ns_above}.algo'] = "L-BFGS-B"
        disc_dict[f'{ns_above}.design_space'] = dspace
        #disc_dict[f'{ns_coupling}.design_space'] = dspace
        disc_dict[f'{ns_above}.formulation'] = 'DisciplinaryOpt'
        disc_dict[f'{ns_above}.objective_name'] = 'objective_lagrangian'
        disc_dict[f'{ns_above}.ineq_constraints'] = []
        disc_dict[f'{ns_above}.algo_options'] = {
            #"maxls": 6,
            #"maxcor": 3,
            "ftol_rel": 1e-15,
        }
        
        # design var inputs
        disc_dict[f'{ns_above}.output_alpha_services_in'] = 0.87
        disc_dict[f'{ns_above}.prod_gr_start_services_in'] = 0.02
        disc_dict[f'{ns_above}.decl_rate_tfp_services_in'] = 0.02
        disc_dict[f'{ns_above}.prod_start_services_in'] = 0.27
        disc_dict[f'{ns_above}.energy_eff_k_services_in'] = 0.05
        disc_dict[f'{ns_above}.energy_eff_cst_services_in'] = 0.98
        disc_dict[f'{ns_above}.energy_eff_xzero_services_in'] = 2012.0
        disc_dict[f'{ns_above}.energy_eff_max_services_in'] = 3.51
        
        disc_dict[f'{ns_above}.output_alpha_agri_in'] = 0.87
        disc_dict[f'{ns_above}.prod_gr_start_agri_in'] = 0.02
        disc_dict[f'{ns_above}.decl_rate_tfp_agri_in'] = 0.02
        disc_dict[f'{ns_above}.prod_start_agri_in'] = 0.27
        disc_dict[f'{ns_above}.energy_eff_k_agri_in'] = 0.05
        disc_dict[f'{ns_above}.energy_eff_cst_agri_in'] = 0.98
        disc_dict[f'{ns_above}.energy_eff_xzero_agri_in'] = 2012.0
        disc_dict[f'{ns_above}.energy_eff_max_agri_in'] = 3.51
        
        disc_dict[f'{ns_above}.output_alpha_indus_in'] = 0.87
        disc_dict[f'{ns_above}.prod_gr_start_indus_in'] = 0.02
        disc_dict[f'{ns_above}.decl_rate_tfp_indus_in'] = 0.02
        disc_dict[f'{ns_above}.prod_start_indus_in'] = 0.27
        disc_dict[f'{ns_above}.energy_eff_k_indus_in'] = 0.05
        disc_dict[f'{ns_above}.energy_eff_cst_indus_in'] = 0.98
        disc_dict[f'{ns_above}.energy_eff_xzero_indus_in'] = 2012.0
        disc_dict[f'{ns_above}.energy_eff_max_indus_in'] = 3.51
        
        func_df = pd.DataFrame(
            columns=['variable', 'ftype', 'weight', AGGR_TYPE, 'namespace'])
        func_df['variable'] = [ 'error_pib_total', 'error_cap_total']
        func_df['ftype'] =  [OBJECTIVE,OBJECTIVE]
        func_df['weight'] = [0.125, 0.125]
        func_df[AGGR_TYPE] = [AGGR_TYPE_SUM, AGGR_TYPE_SUM]
        func_df['namespace'] = ['ns_obj', 'ns_obj']
        func_mng_name = 'FunctionsManager'

        prefix = f'{self.study_name}{self.optim_name}{self.coupling_name}.{func_mng_name}.'
        values_dict = {}
        values_dict[prefix +FunctionManagerDisc.FUNC_DF] = func_df

        disc_dict.update(values_dict)     

        # Inputs for objective 
        data_dir = join(
            dirname(dirname(dirname(dirname(dirname(__file__))))), 'tests', 'data/sectorization_fitting')
        hist_gdp = pd.read_csv(join(data_dir, 'hist_gdp_sect.csv'))
        hist_capital = pd.read_csv(join(data_dir, 'hist_capital_sect.csv'))
        sect_input = {}
        sect_input[ns_coupling + self.obj_name +  '.historical_gdp'] = hist_gdp
        sect_input[ns_coupling + self.obj_name +  '.historical_capital'] = hist_capital
        disc_dict.update(sect_input)
       
    #TO BE UPDATED WITH RIGHT DATA 
        self.witness_sect_uc.study_name = f'{ns_coupling}'
        witness_sect_uc_data = self.witness_sect_uc.setup_usecase()
        for dict_data in witness_sect_uc_data:
            disc_dict.update(dict_data)

        return [disc_dict]


if '__main__' == __name__:
    uc_cls = Study(run_usecase=True)
    uc_cls.load_data()
    uc_cls.execution_engine.display_treeview_nodes(display_variables=True)
    # uc_cls.execution_engine.set_debug_mode()
    uc_cls.run()
    