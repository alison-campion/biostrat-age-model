from SimpleAgeModel import SimpleAgeModel, import_data
import configparser
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read('config/config.ini')
data = import_data(config)
ageModel = SimpleAgeModel(config, data, 'mill')
age_matrix = ageModel.get_reference_age_matrix()

color_map = {
    'mill': [.85,.24,.94],
    'oll': [1,.6,.01],
    'ac1': [0.5,0.5,0.5],
    'ac2': [0.5,0.5,0.5],
    'lb': [.23,.7,.44],
    'bal': [1,.4,.4],
    'vds': [.19,.47,.95]
}
section_order = ['vds', 'oll', 'lb', 'bal', 'ac1', 'ac2', 'mill']
for key in section_order:
    ageModel.create_age_model(key, age_matrix)

# --------------
# Plot D13C Data
# --------------
f, ax = plt.subplots(figsize=[6, 8])
for key in section_order:
    ax.plot(ageModel.data[key]['D13C'], ageModel.data[key]['AGE'], 'o',
            mfc=color_map[key], markersize=7, mec='k')

x_lim = [-9, 6]
ax.set_ylim([345, 322])
ax.set_xlim(x_lim)
ax.set_title('Figure 5', fontsize=14)
ax.grid(True)
ax.legend(section_order, bbox_to_anchor=(1.15, 0.25))

# ----------------------
# Plot First Occurrences
# ----------------------
bioheights = ageModel.return_biozone_ages('mill', age_matrix)
# Rename for plotting purposes
bioheights = bioheights.rename(index = {
    'G. bilineatus': 'Gn. bilineatus',
    'G. truyolsi': 'Gn. truyolsi',
    'D. noduliferous inaequalis': 'D. inaequalis'}
)
for i in ['Gn. texanus', 'Gn. praebilineatus', 'Gn. bilineatus', 'L. nodosa', 'L. ziegleri',
          'Gn. truyolsi', 'D. bernesgae','D. inaequalis']:
    ax.plot(x_lim, [bioheights.loc[i, 'AGE'], bioheights.loc[i, 'AGE']], '--', color='grey')
    ax.text(x_lim[0], bioheights.loc[i, 'AGE'], i, fontsize=13)

# ----------
# Plot Dates
# ----------
age_matrix = ageModel.get_reference_age_matrix()
for i in age_matrix['date']:
    ax.plot(x_lim[1]-.25, i*-1, 'k*', markersize=10)
    ax.text(x_lim[1], i*-1, str(i*-1))

plt.savefig('figure5.svg', bbox_inches='tight')
print('%0.2f to %0.2f: Hiatus = %0.2f' % (ageModel.data['ac1']['AGE'][212], ageModel.data['ac2']['AGE'][0], 
                                          ageModel.data['ac1']['AGE'][212] - ageModel.data['ac2']['AGE'][0]))