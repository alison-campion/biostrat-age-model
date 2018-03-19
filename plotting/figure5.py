from SimpleAgeModel import SimpleAgeModel, import_data
import configparser
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read('config/config.ini')
data = import_data(config)
ageModel = SimpleAgeModel(config, data, 'mill')
new_data = {}

color_map = {
    'mill': [.85,.24,.94],
    'oll': [1,.6,.01],
    'ac1': [0.5,0.5,0.5],
    'ac2': [0.5,0.5,0.5],
    'lb': [.23,.7,.44],
    'bal': [1,.4,.4],
    'vds': [.19,.47,.95]
}
for key in ['mill','oll','ac1','ac2','lb','bal','vds']:
    ageModel.create_age_model(key)

f, ax = plt.subplots(figsize=[6, 8])
for key in config['SECTION_DATA_FILES'].keys():
    ax.plot(ageModel.data[key]['D13C'], ageModel.data[key]['AGE'], 'o',
            mfc=color_map[key], markersize=7, mec='k')

ax.set_ylim([345, 320])
ax.set_xlim([-8.5, 6])
ax.set_title('Figure 5', fontsize=14)
ax.grid(True)

