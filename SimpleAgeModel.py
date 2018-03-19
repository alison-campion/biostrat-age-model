import configparser
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.interpolate import interp1d

config = configparser.ConfigParser()
config.read('config/config.ini')

# TODO: make a more flexible read-in, have pandas parse xlsx, hdf
def import_data(config):
    """
    Read in all the spreadsheets in the data folder as dataframes in a dictionary.
    """
    data = {}
    fp = config['FILEPATHS']['data_file_path']

    for key, value in config['SECTION_DATA_FILES'].items():
        # Read in each datafrmae
        data[key] = pd.read_csv(os.path.join(fp, value))
        # Convert all column header names to those standard names specified in the config file
        data[key] = data[key].rename(columns = dict(config._sections['DATAFRAME_SPECIFICS']))
        if 'AGE' not in data[key].columns:
            data[key]['AGE'] = np.nan

    return data

class SimpleAgeModel(object):
    """
    Takes several geologic sections, in the form of spreadsheets, and correlates them for ages.
    """

    def __init__(self, config, data, ref_sec):
        self.data = data
        self.config = config
        self.ref_sec = ref_sec

    def get_biozones(self):
        """
        Returns a list of the biozones specified in the biozone section of the config file
        """
        bz_list = []
        for key, value in self.config['BIOZONES'].items():
            bz_list.append(value)
        return bz_list

    def find_nearest(self, array, value):
        idx = (np.abs(array-float(value))).argmin()
        return int(idx)

    def return_sed_rate(self, age_matrix):
        """
        Find the sed rates between the points in an age matrix.
        """
        sed_rate = pd.DataFrame(columns = ['rate'])
        sed_rate['rate'] = age_matrix['date'].diff() / age_matrix['height'].diff()
        sed_rate = sed_rate.dropna()
        return sed_rate

    def get_reference_age_matrix(self):
        """
        Get the age matrix for the reference section given in the config file.
        """
        age_matrix = pd.DataFrame()
        i = 0
        for key, value in self.config['AGE_MATRIX'].items():
            age_matrix.loc[i,'height'] = float(key)
            age_matrix.loc[i,'date'] =  float(value)
            i = i + 1

        return age_matrix

    def create_reference_age_model(self):
        """
        Create reference section age model.
        """
        age_matrix = self.get_reference_age_matrix()
#        sed_rate = self.return_sed_rate(age_matrix)
#        df = self.data[self.ref_sec].copy()

        x_list = np.array(self.data[self.ref_sec]['SAMP_HEIGHT'])
        model_list = []
        constraint_list = []

        for i in np.arange(0, age_matrix.shape[0]-1):
            m = interp1d(age_matrix.loc[i: i + 1,'height'], age_matrix.loc[i: i + 1,'date'],
                             bounds_error=False, fill_value='extrapolate')
            model_list.append(m)

            lower_bound = age_matrix.loc[i, 'height']
            upper_bound = age_matrix.loc[i + 1, 'height']

            if i == 0:
                lower_bound = self.data[self.ref_sec].loc[0, 'SAMP_HEIGHT']
            if i == age_matrix.shape[0]-2:
                upper_bound = np.nanmax(self.data[self.ref_sec]['SAMP_HEIGHT'])

            constraint_list.append([lower_bound < x for x in x_list <= upper_bound])

        ages = np.piecewise(x_list, constraint_list, model_list)
        self.data[self.ref_sec]['AGE'] = ages
        self.ref_model = {'x_list': x_list, 
                          'constraint_list': constraint_list,
                          'model_list': model_list}

        return True

# TDOD: Correlate sections by biozone using ages from reference section, put in error messages saying ref sec needs AGE
    def correlate_sec_biozones(self, sec):
        """
        Match each section to the reference section according to shared biozone first appearances. The age from the reference
        section for each first appearance will be assigned as the age for the corresponding first appearance in each section.
        """
        ref_df = self.data[self.ref_sec]

        ref_bz_list = list(ref_df['FIRST_OCCURRENCE'].dropna())

        # Extract section dataframe
        sec_df = self.data[sec]

        # Pull biozones from the section
        sec_bz_list = list(sec_df['FIRST_OCCURRENCE'].dropna())

        # Find list of biozones in both the section and the reference section
        select_bz_list = [i for i in sec_bz_list if i in ref_bz_list]

        temp_ref_df = ref_df[ref_df['FIRST_OCCURRENCE'].isin(select_bz_list)].set_index('FIRST_OCCURRENCE')
        bioheight_inds = []
        for i in temp_ref_df['BIOHEIGHT'].values:
            bioheight_inds.append(self.find_nearest(ref_df['SAMP_HEIGHT'], i))

        temp_sec_df = sec_df[sec_df['FIRST_OCCURRENCE'].isin(select_bz_list)].set_index('FIRST_OCCURRENCE')

        age_matrix = pd.DataFrame([temp_sec_df.loc[select_bz_list, 'BIOHEIGHT'].reset_index(drop=True), 
                                   ref_df.loc[bioheight_inds, 'AGE'].reset_index(drop=True)]).T.reset_index(drop=True)

        age_matrix = age_matrix.rename(columns= {'BIOHEIGHT': 'height', 'AGE': 'date'})

        return age_matrix


    def create_age_model(self, sec):
        """
        Create reference section age model.
        """
        self.create_reference_age_model()
        age_matrix = self.correlate_sec_biozones(sec)

        x_list = np.array(self.data[sec]['SAMP_HEIGHT'].dropna())
        model_list = []
        constraint_list = []

        for i in np.arange(0, age_matrix.shape[0]-1):
            m = interp1d(age_matrix.loc[i: i + 1,'height'], age_matrix.loc[i: i + 1,'date'],
                             bounds_error=False, fill_value='extrapolate')
            model_list.append(m)

            lower_bound = age_matrix.loc[i, 'height']
            upper_bound = age_matrix.loc[i + 1, 'height']

            if i == 0:
                lower_bound = self.data[sec].loc[0, 'SAMP_HEIGHT']
            if i == age_matrix.shape[0]-2:
                upper_bound = np.nanmax(self.data[sec]['SAMP_HEIGHT'])

            constraint_list.append(list(np.array([lower_bound <= x for x in x_list]) * 
                                        np.array([x <= upper_bound for x in x_list])))

        ages = np.piecewise(x_list, constraint_list, model_list)

        return (ages, age_matrix)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    data = import_data(config)
    ageModel = SimpleAgeModel(config, data, 'mill')
    a, b = ageModel.create_age_model('lb')
