/*function getUploadStatistics() {
      $.ajax({
         'url': './api/uploadstats'})
       .done(function(data) {
         document.getElementById('uploads_total').innerHTML = data.total;

         var rows = []

         $.each(data.msmntCampaigns, function(key, item) {
            rows.push('<tr><td>'+item._id+'</td><td>'+item.count+'</td></tr>')
          });

         document.getElementById('measurement_campaigns').innerHTML = rows.join("\n");
        })
       .fail(function() {
         err = '<span class="error">(error: could not load data)</span>';
         document.getElementById('uploads_total').innerHTML = err;
         document.getElementById('measurement_campaigns').innerHTML = 
            '<tr><td>' + err + '</td><td>' + err + '</td></tr>';
        });
     }*/

var api_base = 'http://localhost:5000';

$().ready(loadResults);

function loadResults() {
  var id = window.location.search.substring(1);
  getResults(id);
}

var attr_display_names = {
  "observation_set" : "Observation set",
  "full_path" : "Path"
};


function renderResults(results) {
  var rawResultsDiv = document.getElementById('raw_results');
  var result = results['result'];
  $('#raw_results').append(JSON.stringify(result));
  var iql = results['iql'];
  $('#raw_query').append(JSON.stringify(iql));



  results = result['results'];

  console.log('results.length', results.length);

  if(results.length > 0) {
    var cols = Object.keys(results[0])
    console.log('cols', cols);

    if(cols.indexOf('name') >= 0 && cols.indexOf('count') >= 0) {
      if(cols.length == 2) {
        chart(results);
      }
      else if(cols.length == 3) {
        var group_by = "";

        for(var i = 0; i < cols.length; i++) {
          if(cols[i] != 'name' &&  cols[i] != 'count')
            group_by = cols[i];
        }

        console.log('group_by', group_by);

        var groups = {};

        for(var i = 0; i < results.length; i++) {
          var k = results[i][group_by];

          if(k in groups) {
            groups[k].push(results[i]);
          }
          else
            groups[k] = [results[i]];
        }

        var group_keys = Object.keys(groups);

        for(var i = 0; i < group_keys.length; i++) {
          chart(groups[group_keys[i]], attr_display_names[group_by] + ": " + group_keys[i]);
        }
      }
    }
  }
}


function getResults(id) {
  var request = 
    $.ajax(
      {'url' : api_base + '/result?id=' + encodeURIComponent(id)})
     .done(renderResults)
     .fail(function() { alert('fail :('); });
}


function chart(data, title) {

console.log('chart',data);

var counts = [];

for(var i = 0; i < data.length; i++) 
  counts.push(data[i].count);

var width = 720,
    barHeight = 30;

var max_count = d3.max(counts);

var x = d3.scale.linear()
    .domain([0, max_count])
    .range([0, width]);

var figure = d3.select("#figures").append("div").attr("class","figure");
    figure.append("div").attr("class","title").text(title);

var chart = figure.append("svg")
    .attr("width", width)
    .attr("height", (5+barHeight) * (data.length + 1));

var bar = chart.selectAll(".bars")
    .data(data)
  .enter().append("g")
    .attr("transform", function(d, i) { return "translate(0," + i* (5+barHeight) + ")"; });

bar.append("rect")
    .attr("width", function(d) { return x(d.count); })
    .attr("height", barHeight)
    .attr("fill",function(d) { return "salmon"; });

bar.append("text")
    .attr("x", function(d) {
         if(x(d.count) > 255)
           return x(d.count)-5;
         else
           return x(d.count)+5;
      })
    .attr("y", barHeight / 2)
    .attr("dy", ".35em")
    .attr("fill", function(d) {
        if(x(d.count) > 255)
          return "white";
        else return "black";
      })
    .attr("style", function(d) {
        if(x(d.count) > 255)
          return "text-anchor: end";
        else
          return "text-anchor: start";
      })
    .text(function(d) { return d.name; });



var lines = chart.append("g");

var footer = chart.append("g")
  .attr("transform", function() { return "translate(0," + (data.length * (5+barHeight)) + ")"; });

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("fill","black").attr("x",width-2);
    footer.append("text").attr("x",0).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return "< 0"; }).attr("fill","black");

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("x", 0).attr("fill","black");
    footer.append("text").attr("x",width).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return max_count + ">"; }).attr("fill","black").attr("style","text-anchor: end;");

var table = d3.select(".table");

var hrow = table.append("tr");
    hrow.append("th").text(function() { return "Condition"; });
    hrow.append("th").text(function() { return "Count"; } );

var row = table.selectAll(".row").data(data).enter().append("tr");
    row.append("td").text(function(d) { return d.name; });
    row.append("td").text(function(d) { return d.count; });
}
