import numpy as np
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///db/belly_button_biodiversity.sqlite", echo-False)

Base = automap_base()
Base.prepare(engine, reflect=True)
Sample = Base.classes.otu
Metadata = Base.classes.samples_metadata

session = Session(engine)

#################################################
# Routes
#################################################
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/otu')
def otu():
    results = session.query(OTU).statement
    results_df = pd.read_sql_query(results, session.bind)
    results_df.set_index('otu_id', inplace=True)
    return jsonify(list(results_df["lowest_taxonomic_unit_found"]))

@app.route('/names')
def names():
    results = session.query(Sample).statement
    results_df = pd.read_sql_query(results, session.bind)
    results_df.set_index('otu_id', inplace=True)
    return jsonify(list(results_df.columns))

@app.route('/metadata/<sample>')
def meta(sample):
    results = session.query(Metadata).statement
    results_df = pd.read_sql_query(results, session.bind)
    ob_num = int(sample.split("_")[1])
    sample_name = results_df.loc[results_df["SAMPLEID"] == ob_num, :]
    return sample_name.to_json(orient='records')

@app.route('/wfreq/<sample>')
def wfreq(sample):
    results = session.query(Metadata).statement
    results_df = pd.read_sql_query(results, session.bind)
    ob_num = int(sample.split("_")[1])
    sample_name = results_df.loc[results_df["SAMPLEID"] == ob_num, :]
    wfreq = sample_name["WFREQ"].values[0]
    return f"{wfreq}"

@app.route('/samples/<sample>')
def samples(sample):
    res_otus = session.query(OTU).statement
    res_otus_df = pd.read_sql_query(res_otus, session.bind)
    res_otus_df.set_index('otu_id', inplace=True)

    res_samples=session.query(Sample).statement
    res_samples_df = pd.read_sql_query(res_samples, session.bind)
    sample_name = res_samples_df[sample]

    otu_ids = res_samples_df['otu_id']
    unsorted_df = pd.DataFrame({
        "otu_ids":otu_ids,
        "samples":sample_name
    })

    sorted_df = unsorted_df.sort_values(by=['samples'], ascending=False)
    sorted_otus = {'otu_ids': list(sorted_df['otu_ids'].values)}
    sorted_samples = {"sample_values": list(sorted_df['samples'].values)}
    for i in range(len(sorted_otus['otu_ids'])):
        sorted_otus['otu_ids'][i] = int(sorted_otus['otu_ids'][i])
    for i in range(len(sorted_samples['samples_values'])):
        sorted_samples['samples_values'][i] = int(sorted_samples["sample_values"][i])
    results = [sorted_otus, sorted_samples, list(res_otus_df["lowest_taxonomix_unit_found"])]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
