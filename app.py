import numpy as np
import pandas as pd
import json

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    Response
    )

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///db/belly_button_biodiversity.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)
Sample = Base.classes.samples
OTU = Base.classes.otu
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
    sample_info = results_df[results_df["SAMPLEID"] == ob_num, :]
    wfreq = sample_info["WFREQ"].values[0]
    return f"{wfreq}"

@app.route('/samples/<sample>')
def samples(sample):
    results = session.query(Sample).statement    
    results_df = pd.read_sql_query(results, session.bind)
    sample_df = results_df[['otu_id',sample]]

    sample_df=sample_df.loc[sample_df[sample]>0]
    sort_sample_df = sample_df.sort_values(by=sample, ascending=False)

    otu_ids = {"otu_ids": list(sort_sample_df['otu_id'].values)}
    sorted_samples = {"sample_values": list(sort_sample_df[sample].values)}

    for i in range(len(otu_ids["otu_ids"])):
        otu_ids["otu_ids"][i] = int(otu_ids["otu_ids"][i])
    for i in range(len(sorted_samples["sample_values"])):
        sorted_samples["sample_values"][i] = int(sorted_samples["sample_values"][i])

    sample_list=[otu_ids,sorted_samples]
    return jsonify(list(sample_list))

if __name__ == "__main__":
    app.run(debug=True)
