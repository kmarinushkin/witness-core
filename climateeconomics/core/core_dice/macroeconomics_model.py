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
import numpy as np
import pandas as pd


class MacroEconomics():
    '''
    Economic model that compute the evolution of capital, population, consumption, output...
    '''

    def __init__(self, param, inputs):
        '''
        Constructor
        '''
        self.param = param
        self.inputs = inputs
        self.economics_df = None
        self.set_data()

    def set_data(self):
        self.year_start = self.param['year_start']
        self.year_end = self.param['year_end']
        self.time_step = self.param['time_step']
        self.productivity_start = self.param['productivity_start']
        self.init_gross_output = self.param['init_gross_output']
        self.capital_start = self.param['capital_start']
        self.pop_start = self.param['pop_start']
        self.output_elasticity = self.param['output_elasticity']
        self.popasym = self.param['popasym']
        self.population_growth = self.param['population_growth']
        self.productivity_gr_start = self.param['productivity_gr_start']
        self.decline_rate_tfp = self.param['decline_rate_tfp']
        self.depreciation_capital = self.param['depreciation_capital']
        self.abatecost = self.inputs['abatecost']
        self.damefrac = self.inputs['damage_frac_output']
        self.init_rate_time_pref = self.param['init_rate_time_pref']
        self.conso_elasticity = self.param['conso_elasticity']
        self.lo_capital = self.param['lo_capital']
        self.lo_conso = self.param['lo_conso']
        self.lo_per_capita_conso = self.param['lo_per_capita_conso']
        self.nb_per = round(
            (self.param['year_end'] -
             self.param['year_start']) /
            self.param['time_step'] +
            1)
        self.years_range = np.arange(
            self.year_start,
            self.year_end + 1,
            self.time_step)
        self.saving_rate = pd.Series(
            [self.param['saving_rate']] * self.nb_per, index=self.years_range)
        self.frac_damage_prod = self.param['frac_damage_prod']
        self.damage_to_productivity = self.param['damage_to_productivity']

    def create_dataframe(self):
        '''
        Create the dataframe and fill it with values at year_start
        '''
        param = self.param
        economics_df = pd.DataFrame(
            index=self.years_range,
            columns=[
                'year',
                'saving_rate',
                'gross_output',
                'output_net_of_d',
                'net_output',
                'population',
                'productivity',
                'productivity_gr',
                'consumption',
                'pc_consumption',
                'capital',
                'investment',
                'interest_rate'])
        economics_df.loc[param['year_start'],
                         'gross_output'] = self.init_gross_output
        economics_df.loc[param['year_start'], 'population'] = self.pop_start
        economics_df.loc[param['year_start'], 'capital'] = self.capital_start
        economics_df.loc[param['year_start'],
                         'productivity'] = self.productivity_start
        economics_df.loc[param['year_start'],
                         'productivity_gr'] = self.productivity_gr_start
        economics_df['saving_rate'] = self.saving_rate
        economics_df['year'] = self.years_range
        self.economics_df = economics_df

        self.economics_df = self.economics_df.replace(
            [np.inf, -np.inf], np.nan)
        return economics_df.fillna(0.0)

    def compute_population(self, year):
        '''
        Population, L
        Returns:
            :returns: L(t-1) * (L_max / L(t-1)) ** L_g
        '''
        p_population = self.economics_df.loc[year -
                                             self.time_step, 'population']
        population = p_population * \
            (self.popasym / p_population) ** self.population_growth
        self.economics_df.loc[year, 'population'] = population
        return population

    def compute_productivity_growthrate(self, year):
        '''
        A_g, Growth rate of total factor productivity.
        Returns:
            :returns: A_g(0) * exp(-Δ_a * (t-1))
        '''
        t = ((year - self.year_start) / self.time_step) + 1
        productivity_gr = self.productivity_gr_start * \
            np.exp(-self.decline_rate_tfp * 5 * (t - 1))
        self.economics_df.loc[year, 'productivity_gr'] = productivity_gr
        return productivity_gr

    def compute_productivity(self, year):
        '''
        productivity
        if damage_to_productivity= True add damage to the the productivity
        if  not: productivity evolves independently from other variables (except productivity growthrate)
        '''
        damage_to_productivity = self.damage_to_productivity
        p_productivity = self.economics_df.loc[year -
                                               self.time_step, 'productivity']
        p_productivity_gr = self.economics_df.loc[year -
                                                  self.time_step, 'productivity_gr']
        damefrac = self.damefrac[year]
        if damage_to_productivity == True:
            #damage = 1-damefrac
            productivity = (1 - self.frac_damage_prod * damefrac) * \
                (p_productivity / (1 - p_productivity_gr))
        else:
            productivity = p_productivity / (1 - p_productivity_gr)
        self.economics_df.loc[year, 'productivity'] = productivity
        return productivity

    def compute_capital(self, year):
        """K(t+1), Capital for next time period, trillions $USD
        Args:
            :param capital: capital
            :param depreciation: depreciation rate
            :param investment: investment
        """
        if year == self.year_end:
            pass
        else:
            investment = self.economics_df.loc[year, 'investment']
            capital = self.economics_df.loc[year, 'capital']
            capital_a = capital * \
                (1 - self.depreciation_capital) ** self.time_step + \
                self.time_step * investment
            # Lower bound for capital
            self.economics_df.loc[year + self.time_step,
                                  'capital'] = max(capital_a, self.lo_capital)
            return capital_a

    def compute_investment(self, year):
        """
        I(t), Investment, trillions $USD

        """
        saving_rate = self.saving_rate[year]
        net_output = self.economics_df.loc[year, 'net_output']
        investment = saving_rate * net_output
        self.economics_df.loc[year, 'investment'] = investment
        return investment

    def compute_gross_output(self, year):
        """Gross output, trillions USD
        Args:
            :param productivity: productivity in current time step
            :param capital: capital in current time step
            :param output_elasticity: elasticity of output
            :param population: population in current time step
        Returns:
            :returns: A(t) * K(t) ^ γ * L ^ (1 - γ)
        """
        capital = self.economics_df.loc[year, 'capital']
        population = self.economics_df.loc[year, 'population']
        productivity = self.economics_df.loc[year, 'productivity']
        gross_output = productivity * capital ** self.output_elasticity * \
            (population / 1000) ** (1 - self.output_elasticity)
        self.economics_df.loc[year, 'gross_output'] = gross_output
        return gross_output

    def compute_output_net_of_damage(self, year):
        """Output net of damages, trillions USD
        """
        damage_to_productivity = self.damage_to_productivity
        damefrac = self.damefrac[year]
        gross_output = self.economics_df.loc[year, 'gross_output']
#        if damage_to_productivity == True :
#            D = 1 - damefrac
#            damage_to_output = D/(1-self.frac_damage_prod*(1-D))
#            output_net_of_d = gross_output * damage_to_output
#            damtoprod = D/(1-self.frac_damage_prod*(1-D))
        if damage_to_productivity == True:
            damage = 1 - ((1 - damefrac) /
                          (1 - self.frac_damage_prod * damefrac))
            output_net_of_d = (1 - damage) * gross_output
        else:
            output_net_of_d = gross_output * (1 - damefrac)
        self.economics_df.loc[year, 'output_net_of_d'] = output_net_of_d
        return output_net_of_d

    def compute_net_output(self, year):
        """Net output, trillions USD
        """
        abatecost = self.abatecost[year]
        output_net_of_d = self.economics_df.loc[year, 'output_net_of_d']
        net_output = output_net_of_d - abatecost
        self.economics_df.loc[year, 'net_output'] = net_output
        return net_output

    def compute_consumption(self, year):
        """Equation for consumption
        C, Consumption, trillions $USD
        Args:
            output: Economic output at t
            savings: Savings rate at t
        """
        net_output = self.economics_df.loc[year, 'net_output']
        investment = self.economics_df.loc[year, 'investment']
        consumption = net_output - investment
        # lower bound for conso
        self.economics_df.loc[year, 'consumption'] = max(
            consumption, self.lo_conso)
        return consumption

    def compute_consumption_pc(self, year):
        """Equation for consumption per capita
        c, Per capita consumption, thousands $USD
        """
        consumption = self.economics_df.loc[year, 'consumption']
        population = self.economics_df.loc[year, 'population']
        consumption_pc = consumption / population * 1000
        # Lower bound for pc conso
        self. economics_df.loc[year, 'pc_consumption'] = max(
            consumption_pc, self.lo_conso)
        return consumption_pc

    def compute_interest_rate(self, year):
        """Equation for interest rate
        """
        if year == self.year_end:
            pass
        else:
            consumption = self.economics_df.loc[year, 'consumption']
            consumption_a = self.economics_df.loc[year +
                                                  self.time_step, 'consumption']
            interest_rate = (1 + self.init_rate_time_pref) * (consumption_a /
                                                              consumption)**(self.conso_elasticity / self.time_step) - 1
            self.economics_df.loc[year, 'interest_rate'] = interest_rate
            return interest_rate

    def compute(self, inputs, damage_prod=False):
        """
        Compute all models for year range
        """
        self.damage_prod = damage_prod
        self.inputs = inputs
        self.abatecost = self.inputs['abatecost'].reindex(
            self.years_range)
        self.damefrac = self.inputs['damage_frac_output'].reindex(
            self.years_range)

        self.create_dataframe()
        # YEAR START
        self.compute_output_net_of_damage(self.year_start)
        self.compute_net_output(self.year_start)
        self.compute_investment(self.year_start)
        self.compute_consumption(self.year_start)
        self.compute_consumption_pc(self.year_start)
        # for year 0 compute capital +1
        self.compute_capital(self.year_start)
        # Then iterate over years from year_start + tstep:
        for year in self.years_range[1:]:
            # First independant variables
            self.compute_population(year)
            self.compute_productivity_growthrate(year)
            self.compute_productivity(year)
            # Then others:
            self.compute_gross_output(year)
            self.compute_output_net_of_damage(year)
            self.compute_net_output(year)
            self.compute_investment(year)
            self.compute_consumption(year)
            self.compute_consumption_pc(year)
            # capital t+1 :
            self.compute_capital(year)
        # Then interest rate
        for year in self.years_range:
            self.compute_interest_rate(year)
        self.economics_df = self.economics_df.replace(
            [np.inf, -np.inf], np.nan)
        return self.economics_df.fillna(0.0)
