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

var api_base = 'https://observatory.mami-project.eu/papi';

$().ready(loadResults);

function loadResults() {
  var id = window.location.search.substring(1);
  getResults(id);
}

var attr_display_names = {
  "observation_set" : "Observation set",
  "full_path" : "Path",
  "name" : "Condition",
  "count" : "Count"
};

function attr_name_to_display(name) {
  if(name in attr_display_names)
    return attr_display_names[name];
  return name;
}

function renderCounts(results, group_order, distinct) {
  if(!Array.isArray(group_order)) {
    console.log("group_order not an array");
    return;
  }

  if(results.length < 0) {
    console.log("empty result set");
    return;
  }

  var counted_attribute = group_order[group_order.length-1].substring(1);
  var distinct_attribute = counted_attribute;

  group_order.pop();

  if(distinct === true)
    counted_attribute = group_order.pop().substring(1);

  for(var i = 0; i < group_order.length; i++) {
    group_order[i] = group_order[i].substring(1);
  }

  var cols = Object.keys(results[0]);
  cols.sort();

  console.log('group_order', group_order);
  console.log('results.length', results.length);
  console.log('cols', cols);
  console.log('counted_attribute', counted_attribute);

  if(group_order.length == 1) {

    var group_by = group_order[0];
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
    group_keys.sort();

    //for(var i = 0; i < group_keys.length; i++) {
    //  chart(groups[group_keys[i]], attr_name_to_display(group_by) + ": " + group_keys[i], counted_attribute);
    //}

    var title = "Counts of observations per <i>" + attr_name_to_display(counted_attribute) + "</i> grouped by <i>" + attr_name_to_display(group_by) + "</i>";

    if(distinct === true) {
      title = "Counts of distinct <i>" + attr_name_to_display(distinct_attribute) + "s</i> per <i>" + attr_name_to_display(counted_attribute) + "</i> grouped by <i>" + attr_name_to_display(group_by) + "</i>";
    }

    hbar_stacked(groups, title, counted_attribute, group_by);

  }
  else if(group_order.length == 0) {
    chart(results, "Counts", counted_attribute);
  }
}


function renderResults(results) {
  var rawResultsDiv = document.getElementById('raw_results');
  var result = results['result'];
  $('#raw_results').append(JSON.stringify(result));
  var iql = results['iql'];
  $('#raw_query').append(JSON.stringify(iql));



  results = result['results'];


  console.log('iql', JSON.stringify(iql));

  if(!('query' in iql)) {
    return; //abort. something's more than fishy
  }


  var query = iql['query'];

  if('count' in query) {
      renderCounts(results, query['count'][0]);
  }
  else if('count-distinct' in query) {
      renderCounts(results, query['count-distinct'][0], true);
  }

  if(results.length > 0)
    table(results);
}


function getResults(id) {
  var request = 
    $.ajax(
      {'url' : api_base + '/result?id=' + encodeURIComponent(id)})
     .done(renderResults)
     .fail(function() { alert('fail :('); });
}


function table(data) {
  var table = d3.select(".table");

  var cols = Object.keys(data[0]);
  cols.sort();


  var hrow = table.append("tr");

  for(var i = 0; i < cols.length; i++) {
    hrow.append("th").text(function() { return attr_name_to_display(cols[i]); });
  }

  var row = table.selectAll(".row").data(data).enter().append("tr");

  for(var i = 0; i < cols.length; i++) {
    row.append("td").text(function(d) { return d[cols[i]] });
  }

}

function trim_long(str) {
  str = str.toString();
  if(str.length > 35)
    return str.substring(0,32) + "...";
  return str;
}

function to_e(num) {
  if(num < 10000)
    return num;
  var lg = Math.floor(Math.log10(num));
  var b = num / (Math.pow(10,lg));
      b = Math.round(10*b)/10;
  return "" + b + "e" + lg;
}


function hbar_stacked(groups, title, counted_attribute, group_by) {
  console.log('hbar_stacked', groups, title, counted_attribute);

  document.getElementById('chart_section').style.display = 'block';

  var group_keys = Object.keys(groups);
  group_keys.sort()
  console.log('group_keys', group_keys);
  var max_overall = 0;
  var cols = [];

  var counted_total = {};

  for(var i = 0; i < group_keys.length; i++) {
    var data = groups[group_keys[i]];
    var temp = 0;
    for(var j = 0; j < data.length; j++) {
      temp += data[j]['count'];

      if(cols.indexOf(data[j][counted_attribute]) < 0)
        cols.push(data[j][counted_attribute]);

      if(data[j][counted_attribute] in counted_total) {
        counted_total[data[j][counted_attribute]] += data[j]['count'];
      }
      else {
        counted_total[data[j][counted_attribute]] = data[j]['count'];
      }
    }

    max_overall = d3.max([max_overall, temp]);
  }

  cols.sort();
  console.log('cols', cols);
  console.log('max_overall', max_overall);
  console.log('counted_total', counted_total);

  var width = 720,
      barHeight = 30;

  var colors = ['salmon','steelblue','peru','mediumorchid','red','darkgray','green','orangered','magenta','maroon','blue','darkgreen','burlywood','indigo'];


  var x = d3.scale.linear()
      .domain([0, max_overall])
      .range([0, width-200]);

  var figure = d3.select("#figures").append("div").attr("class","figure");
      figure.append("div").attr("class","title").html(title);

  var chart = figure.append("svg")
      .attr("width", width)
      .attr("height", (5+barHeight) * (group_keys.length + 1 + Math.ceil((cols.length)/2)));


  for(var i = 0; i < group_keys.length; i++) {
    var data = groups[group_keys[i]];

    var region = chart.append("g").attr("transform","translate(0," + i*(5+barHeight) + ")");
    
    data.sort(function (a,b) { 
     if(a[counted_attribute] > b[counted_attribute]) return 1;
     if(a[counted_attribute] < b[counted_attribute]) return -1;
     return 0;
    });

    console.log('data',data);

    var offset_x = 200;

    region.append("text")
      .attr("y", barHeight /2).attr("dy", ".35em").text(trim_long(group_keys[i]))
      .attr("style","font-family: sans-serif; font-size: 14px; text-anchor: start");

    for(var j = 0; j < data.length; j++) {
      region.append("rect")
      .attr("width", x(data[j].count))
      .attr("height", barHeight)
      .attr("fill", colors[cols.indexOf(data[j][counted_attribute])])
      .attr("x", offset_x);
      offset_x += x(data[j].count);
    }

    offset_x = 200;

    for(var j = 0; j < data.length; j++) {
      region.append("rect")
      .attr("width", 2)
      .attr("height", barHeight)
      .attr("fill","black")
      .attr("x", offset_x);
      offset_x += x(data[j].count);
    }

    region.append("rect")
      .attr("width", 2)
      .attr("height", barHeight)
      .attr("fill","black")
      .attr("x", offset_x-2);
  }

  var lines = chart.append("g");

  var footer = chart.append("g")
    .attr("transform", function() { return "translate(0," + (group_keys.length * (5+barHeight)) + ")"; });

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*group_keys.length -5).attr("fill","black").attr("x",width-2);
    footer.append("text").attr("x",200).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return "0"; }).attr("fill","black");

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*group_keys.length -5).attr("x", 200).attr("fill","black");
    footer.append("text").attr("x",width).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return max_overall + ""; }).attr("fill","black").attr("style","text-anchor: end;");

  var legend = chart.append("g");
      legend.attr("transform", "translate(0," + ((group_keys.length+1) * (5+barHeight)) + ")");

  offset_x = 0;
  offset_y = 0;

  for(var i = 0; i < cols.length; i++) {
    legend.append("rect").attr("y", offset_y).attr("x",offset_x + 0).attr("width", barHeight).attr("height", barHeight).attr("fill", colors[i]);
    legend.append("text").attr("x",offset_x + barHeight+5).attr("y", offset_y + barHeight /2).attr("dy", ".35em").text(trim_long(cols[i]) + " (" + to_e(counted_total[cols[i]]) +")")
     .attr("style","font-family: sans-serif; font-size: 14px; text-anchor: start;")
     .attr("fill", colors[i]);
    offset_x += Math.floor(width / 2);
    if(i % 2 == 1) {
      offset_y += barHeight+5;
      offset_x = 0;
    }
  }
}

function chart(data, title, counted_attribute) {

console.log('chart',data);

document.getElementById('chart_section').style.display = 'block';

var counts = [];

for(var i = 0; i < data.length; i++) 
  counts.push(data[i].count);

var width = 720,
    barHeight = 30;

var max_count = d3.max(counts);
var sum_count = d3.sum(counts);

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
         if(x(d.count) > width/2)
           return x(d.count)-5;
         else
           return x(d.count)+5;
      })
    .attr("y", barHeight / 2)
    .attr("dy", ".35em")
    .attr("fill", function(d) {
        if(x(d.count) > width/2)
          return "white";
        else return "black";
      })
    .attr("style", function(d) {
        if(x(d.count) > width/2)
          return "font-family: monospace, monospace; font-size: 13px; text-anchor: end";
        else
          return "font-family: monospace, monospace; font-size: 13px; text-anchor: start";
      })
    .text(function(d) { return trim_long(d[counted_attribute]) + " [" + Math.round((100*d.count/sum_count)*10)/10 + "%]"; });



var lines = chart.append("g");

var footer = chart.append("g")
  .attr("transform", function() { return "translate(0," + (data.length * (5+barHeight)) + ")"; });

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("fill","black").attr("x",width-2);
    footer.append("text").attr("x",0).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return "0"; }).attr("fill","black");

    lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("x", 0).attr("fill","black");
    footer.append("text").attr("x",width).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return max_count + ""; }).attr("fill","black").attr("style","text-anchor: end;");
}
