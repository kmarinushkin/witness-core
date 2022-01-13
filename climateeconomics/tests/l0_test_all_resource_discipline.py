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
'''
mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8
'''
import unittest
from os.path import join, dirname
from pandas import read_csv
from climateeconomics.core.core_resources.all_resources_model import AllResourceModel
from climateeconomics.core.core_resources.resources_model import ResourceModel
from sos_trades_core.execution_engine.execution_engine import ExecutionEngine


class AllResourceModelTestCase(unittest.TestCase):

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.year_start = 2020
        self.year_end = 2100

        data_dir = join(dirname(__file__), 'data')

        self.oil_production_df = read_csv(
            join(data_dir, 'oil.predictible_production.csv'))
        self.oil_production_df.set_index('years', inplace=True)
        self.gas_production_df = read_csv(
            join(data_dir, 'gas.predictible_production.csv'))
        self.coal_production_df = read_csv(
            join(data_dir, 'coal.predictible_production.csv'))
        self.uranium_production_df = read_csv(
            join(data_dir, 'uranium.predictible_production.csv'))
        self.oil_stock_df = read_csv(
            join(data_dir, 'oil.stock.csv'))
        self.gas_stock_df = read_csv(
            join(data_dir, 'gas.stock.csv'))
        self.uranium_stock_df = read_csv(
            join(data_dir, 'uranium.stock.csv'))
        self.coal_stock_df = read_csv(
            join(data_dir, 'coal.stock.csv'))
        self.oil_price_df = read_csv(
            join(data_dir, 'oil.price.csv'))
        self.gas_price_df = read_csv(
            join(data_dir, 'gas.price.csv'))
        self.coal_price_df = read_csv(
            join(data_dir, 'coal.price.csv'))
        self.uranium_price_df = read_csv(
            join(data_dir, 'uranium.price.csv'))
        self.oil_use_df = read_csv(
            join(data_dir, 'oil.use.csv'))
        self.gas_use_df = read_csv(
            join(data_dir, 'gas.use.csv'))
        self.coal_use_df = read_csv(
            join(data_dir, 'coal.use.csv'))
        self.uranium_use_df = read_csv(
            join(data_dir, 'uranium.use.csv'))
        self.non_modeled_resource_df = read_csv(
            join(data_dir, 'resource_data_price.csv'))
        self.all_demand= read_csv(
            join(data_dir, 'all_demand_from_energy_mix.csv'))

        self.resource_list=['natural_gas_resource', 'uranium_resource', 'coal_resource', 'oil_resource']

        self.param = {'All_Demand':self.all_demand,
                      'year_start': self.year_start,
                      'year_end': self.year_end,
                      'resource_list':self.resource_list,
                      'oil_resource.predictible_production':self.oil_production_df,
                      'natural_gas_resource.predictible_production':self.gas_production_df,
                      'uranium_resource.predictible_production':self.uranium_production_df,
                      'coal_resource.predictible_production':self.coal_production_df,
                      'oil_resource.use_stock':self.oil_use_df,
                      'natural_gas_resource.use_stock':self.gas_use_df,
                      'uranium_resource.use_stock':self.uranium_use_df,
                      'coal_resource.use_stock':self.coal_use_df,
                      'oil_resource.resource_stock' : self.oil_stock_df,
                      'natural_gas_resource.resource_stock' : self.gas_stock_df,
                      'uranium_resource.resource_stock' : self.uranium_stock_df,
                      'coal_resource.resource_stock' : self.coal_stock_df,
                      'oil_resource.resource_price': self.oil_price_df,
                      'natural_gas_resource.resource_price': self.gas_price_df,
                      'coal_resource.resource_price': self.coal_price_df,
                      'uranium_resource.resource_price': self.uranium_price_df,
                      'non_modeled_resource_price':self.non_modeled_resource_df}

    def test_all_resource_model(self):
        '''
        Basique test of land use model
        Mainly check the overal run without value checks (will be done in another test)
        '''
        All_resource = AllResourceModel(self.param)
        All_resource.compute(self.param)

    def test_All_resource_discipline(self):
        '''
        Check discipline setup and run
        '''
        name = 'Test'
        model_name = 'All_resource'
        ee = ExecutionEngine(name)
        ns_dict = {'ns_public': f'{name}',
                   'coal_resource': f'{name}.{model_name}',
                   'oil_resource': f'{name}.{model_name}',
                   'natural_gas_resource': f'{name}.{model_name}',
                   'uranium_resource': f'{name}.{model_name}',
                  'ns_resource': f'{name}.{model_name}'}
        ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_resources.sos_wrapping_all_resource.all_resource_model.all_resource_disc.AllResourceDiscipline'
        builder = ee.factory.get_builder_from_module(model_name, mod_path)

        ee.factory.set_builders_to_coupling_builder(builder)

        ee.configure()
        ee.display_treeview_nodes()
        inputs_dict = {f'{name}.year_start': self.year_start,
                       f'{name}.year_end': self.year_end,
                       f'{name}.{model_name}.{ResourceModel.DEMAND}': self.all_demand,
                       f'{name}.{model_name}.oil_resource.{ResourceModel.PRODUCTION}':self.oil_production_df,
                       f'{name}.{model_name}.oil_resource.{ResourceModel.RESOURCE_STOCK}':self.oil_stock_df,
                       f'{name}.{model_name}.oil_resource.{ResourceModel.RESOURCE_PRICE}':self.oil_price_df,
                       f'{name}.{model_name}.oil_resource.{ResourceModel.USE_STOCK}':self.oil_use_df,
                       f'{name}.{model_name}.natural_gas_resource.{ResourceModel.PRODUCTION}':self.gas_production_df,
                       f'{name}.{model_name}.natural_gas_resource.{ResourceModel.RESOURCE_STOCK}':self.gas_stock_df,
                       f'{name}.{model_name}.natural_gas_resource.{ResourceModel.RESOURCE_PRICE}':self.gas_price_df,
                       f'{name}.{model_name}.natural_gas_resource.{ResourceModel.USE_STOCK}':self.gas_use_df,
                       f'{name}.{model_name}.coal_resource.{ResourceModel.PRODUCTION}':self.coal_production_df,
                       f'{name}.{model_name}.coal_resource.{ResourceModel.RESOURCE_STOCK}':self.coal_stock_df,
                       f'{name}.{model_name}.coal_resource.{ResourceModel.RESOURCE_PRICE}':self.coal_price_df,
                       f'{name}.{model_name}.coal_resource.{ResourceModel.USE_STOCK}':self.coal_use_df,
                       f'{name}.{model_name}.uranium_resource.{ResourceModel.PRODUCTION}':self.uranium_production_df,
                       f'{name}.{model_name}.uranium_resource.{ResourceModel.RESOURCE_STOCK}':self.uranium_stock_df,
                       f'{name}.{model_name}.uranium_resource.{ResourceModel.RESOURCE_PRICE}':self.uranium_price_df,
                       f'{name}.{model_name}.uranium_resource.{ResourceModel.USE_STOCK}':self.uranium_use_df,
                       f'{name}.{model_name}.{AllResourceModel.NON_MODELED_RESOURCE_PRICE}': self.non_modeled_resource_df}

        ee.load_study_from_input_dict(inputs_dict)
        ee.execute()
        disc = ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        filter = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filter)
        for graph in graph_list:
          graph.to_plotly().show()
