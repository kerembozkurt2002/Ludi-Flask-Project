from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json
from datetime import datetime

app = Flask(__name__)

# Load JSON data
with open('users.json') as f:
    users_data = json.load(f)

with open('simulations.json') as f:
    simulations_data = json.load(f)

# Create DataFrames
users_df = pd.DataFrame(users_data['users'])
simulations_df = pd.DataFrame(simulations_data['simulations'])

# Calculate company user counts
company_user_counts = users_df.groupby('simulation_id').size().reset_index(name='User Count')
company_user_counts = company_user_counts.merge(simulations_df[['simulation_id', 'company_name']], on='simulation_id')
company_user_counts = company_user_counts.groupby('company_name')['User Count'].sum().reset_index()

# Generate user growth plot
users_df['signup_datetime'] = pd.to_datetime(users_df['signup_datetime'], unit='d', origin='1899-12-30')
user_growth = users_df.groupby(users_df['signup_datetime'].dt.date).size().cumsum()

plt.figure(figsize=(10, 6))
plt.plot(user_growth.index, user_growth.values, marker='o')
plt.title('Ludi User Growth Over Time')
plt.xlabel('Date')
plt.ylabel('Total Users')
plt.grid(True)

# Save plot to a bytes object and encode it to base64
buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
ludi_growth_plot = base64.b64encode(buf.read()).decode('utf-8')
buf.close()

@app.route('/')
def index():
    return render_template('index.html', company_summary=company_user_counts.to_dict(orient='records'), ludi_growth_plot=ludi_growth_plot)

if __name__ == '__main__':
    app.run(debug=True)