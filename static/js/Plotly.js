function populateDropdown(){
  var selector = document.getElementById('selDataset');
  var url = "/names";
  Plotly.d3.json(url, function(error, response) {
    if (error) return console.warn(error);
    var data = response;
    data.map(function(sample){
      var option = document.createElement('option')
      option.text = sample
      option.value = sample
      selector.appendChild(option)
    });
  });
};

//initialize page with default sample BB_940
var initSample = "BB_940"
populateDropdown(initSample);
pieChart(initSample);
bubbleChart(initSample);
metaData(initSample)

function optionChanged(sample){
  pieChart(sample);
  bubbleChart(sample);
  metaData(sample)
};

/*****************************************************************
* PIE CHART
*****************************************************************/
function pieChart(sample){
  // This is the JSON-populated URL (I am serving it in app.py)
  var sampleURL = `/samples/${sample}`;
  var otuURL = `/otu`;

  // This is where I store the JSON variables into separate arrays
  Plotly.d3.json(sampleURL,function(error,response){
    if (error) return console.log(error);
    //PIE: Use the OTU ID as the labels for the pie chart
    var otu_ids = [];
    //PIE: Use the Sample Value as the values for the PIE chart
    var samp_values = [];
    //PIE: Use the OTU Description as the hovertext for the chart
    var otu_descs = [];
    
    //FOR THE PIE CHART I ONLY GO UP TO TEN (FEWER IF LESS THAN TEN)
    var length = response[0].otu_ids.length;
    var j = Math.min(10,length);

    for(i=0; i<j; i++){
      var otu_id = response[0].otu_ids[i];
      otu_ids.push(otu_id);
      var samp_value = response[1].sample_values[i];
      samp_values.push(samp_value);
      
      Plotly.d3.json(otuURL,function(error,response){
        if (error) return console.log(error);
        var otu_desc = response[otu_id-1];
        otu_descs.push(otu_desc);
      });
    };
    // information for PIE chart
    var trace = {
      values: samp_values,
      labels: otu_ids,
      type: "pie",
      text: otu_descs,
      hoverinfo: "text",
      textinfo: "percent"
    };
    var data = [trace]
    var layout = {
      title: "Top Ten OTUs"
    }
    Plotly.newPlot("pie",data,layout);
  });
};

/*****************************************************************
* BUBBLE CHART
*****************************************************************/
function bubbleChart(sample){
  // This is the JSON-populated URL (I am serving it in app.py)
  var sampleURL = `/samples/${sample}`;
  var otuURL = `/otu`;

  // This is where I store the JSON variables into separate arrays
  Plotly.d3.json(sampleURL,function(error,response){
    if (error) return console.log(error);
    //BUBBLE: Use OTU IDs for the X values, marker colors
    var otu_ids = [];
    //BUBBLE: Use the Sample Values for the y values, marker sizes
    var samp_values = [];
    //BUBBLE: Use the OTU Description Data for the text values
    var otu_descs = [];
    
    //FOR THE BUBBLE CHART I GO PAST TEN
    var length = response[0].otu_ids.length;

    for(i=0; i<length; i++) {
      var otu_id = response[0].otu_ids[i];
      otu_ids.push(otu_id);
      var samp_value = response[1].sample_values[i];
      samp_values.push(samp_value);
      
      Plotly.d3.json(otuURL,function(error,response){
        if (error) return console.log(error);
        var otu_desc = response[otu_id-1];
        otu_descs.push(otu_desc.substring(0, 30));
      });
    };
    // information for BUBBLE chart
    var trace = {
      x: otu_ids,
      y: samp_values,
      mode: 'markers',
      type: 'scatter',
      text: otu_descs,
      marker: {
          size: samp_values,
          color: otu_ids,
          colorscale: "Rainbow"
      }
    };
    var data = [trace]
    var layout = {
      title: "Sample Size by OTU ID",
      yaxis: {
        title: 'Sample Values',
      },
      xaxis: {
        title: 'OTU IDs',
      }
    }
    Plotly.newPlot("bubble",data,layout);
  });
};

/*****************************************************************
* BUBBLE CHART
*****************************************************************/
function metaData(sample){
  var sampleURL = `/metadata/${sample}`;
  //Display each key/value pair from the metadata JSON object somewhere on the page
  Plotly.d3.json(sampleURL,function(error,response){
    if (error) return console.log(error);
    var data = response[0];
    var metaList = document.getElementById('sampleMetadata');

    metaList.innerHTML = '';

    var newH4=document.createElement('h4')
    newH4.innerHTML = "Metadata: ";
    metaList.appendChild(newH4);
    
    var metaItems = [["Sample","SAMPLEID"],["Ethnicity","ETHNICITY"],["Gender","GENDER"],["Age","AGE"],
      ["Weekly Wash Frequency","WFREQ"],["Type (Innie/Outie)","BBTYPE"],["Country","COUNTRY012"],["Dog Owner","DOG"],["Cat Owner","CAT"]];
    for(i=0; i<metaItems.length; i++){
      var newLi = document.createElement('li');
      newLi.innerHTML = `${metaItems[i][0]}: ${data[metaItems[i][1]]}`;
      metaList.appendChild(newLi);
    };
  });
};

