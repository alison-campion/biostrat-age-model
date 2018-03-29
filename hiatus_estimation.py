from SimpleAgeModel import SimpleAgeModel, import_data
import configparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# ---------------
# Initialize Data
# ---------------
config = configparser.ConfigParser()
config.read('config/config.ini')
data = import_data(config)
ageModel = SimpleAgeModel(config, data, 'mill')

# -----------------------
# Define Helper Functions
# -----------------------
def generate_random_height(age_dist, i):
    height = np.random.choice(list(age_dist[i][0]),1,list(age_dist[i][1]))[0]
    return height

def generate_random_age_matrix(age_dist):
    age_matrix = pd.DataFrame([
        [generate_random_height(age_dist, 1), -339.01],
        [generate_random_height(age_dist, 2), -333.87],
        [generate_random_height(age_dist, 3), -332.50,],
        [generate_random_height(age_dist, 4), -326.36]
    ], columns = ['height', 'date'])

    return age_matrix

def generate_probability_dist(dist, mean, variance):
    weights = norm.pdf(dist, mean, variance)
    weights = (weights-min(weights))/(max(weights)-min(weights))

    return (dist, weights)

# -----------------------------------------
# Degine Probability Distribution Functions
# -----------------------------------------
age_distributions = {}
# First Date
(dist, weights) = generate_probability_dist(np.linspace(4.4, 5.3, 50), 4.8, .1)
age_distributions[1] = (dist, weights)

# Second Date
(dist, weights) = generate_probability_dist(np.linspace(15.29, 16.52, 50) , 16.00, .1)
age_distributions[2] = (dist, weights)

# Third Date
(dist, weights) = generate_probability_dist(np.linspace(16.53, 18.31, 50), 17.5, 1)
age_distributions[3] = (dist, weights)

# Fourth Date
(dist, weights) = generate_probability_dist(np.linspace(36.5, 37.5, 50), 37, .1)
age_distributions[4] = (dist, weights)

# --------------
# Run Iterations
# --------------
N = 10000
start_date = np.zeros(N)
end_date = np.zeros(N)
hiatus = np.zeros(N)
age_matrix_options = {}

for i in np.arange(0,start_date.shape[0]):
    age_matrix_options[i] = generate_random_age_matrix(age_distributions)
    ageModel.create_age_model('ac1', age_matrix_options[i])
    ageModel.create_age_model('ac2', age_matrix_options[i])
    
    start_date[i] = ageModel.data['ac1']['AGE'][212]
    end_date[i] = ageModel.data['ac2']['AGE'][0]
    hiatus[i] = start_date[i]-end_date[i]

# ------------
# Plot Results
# ------------
f, ax = plt.subplots()
ax.hist(start_date-end_date)
ax.axvline(x=np.median(hiatus), color='r')