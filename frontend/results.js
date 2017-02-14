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
  "count" : "Count",
  "location" : "Location",
  "week" : "Week",
  "month" : "Month"
};

function attrNameToDisplay(name) {
  if(name in attr_display_names)
    return attr_display_names[name];
  return name;
}

function findInJSON(query, what, arr) {
  if(typeof(query) != 'object') return;
  var keys = Object.keys(query);
  for(var i = 0; i < keys.length; i++) {
    if(what == keys[i]) {
      arr.push(query[what]);
    }
    findInJSON(query[keys[i]], what, arr);
  }
}

function extractTimestamps(query) {
  var timestamps = [];
  findInJSON(query, 'time', timestamps);
  for(var i = 0; i < timestamps.length; i++) {
    if(Array.isArray(timestamps[i])) {
      timestamps[i] = timestamps[i][0];
      if(timestamps[i] != undefined)
        if(typeof(timestamps[i]) == 'number') {
          timestamps[i] = timestamps[i] + " : " + new Date(timestamps[i]*1000).toUTCString();
        }
    }
  }
  console.log('timestamps', timestamps);
  return timestamps;
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

  if(group_order.length == 2) {
    var top_group_by = group_order[0];
    var bot_group_by = group_order[1];
    console.log('top_group_by', top_group_by);
    console.log('bot_group_by', bot_group_by);

    var top_groups = {};

    for(var i = 0; i < results.length; i++) {
      var k = results[i][top_group_by];

      if(k in top_groups) {
        top_groups[k].push(results[i]);
      }
      else
        top_groups[k] = [results[i]];
    }

    var top_group_keys = Object.keys(top_groups);
    top_group_keys.sort()
    console.log('top_group_keys', top_group_keys);

    for(var i = 0; i < top_group_keys.length; i++) { 
      var results = top_groups[top_group_keys[i]];
      console.log('part_results', results);

      var groups = {};

      for(var j = 0; j < results.length; j++) {
        var k = results[j][bot_group_by];

        if(k in groups) {
          groups[k].push(results[j]);
        }
        else
          groups[k] = [results[j]];
      }

      console.log('part_groups', groups);

      var caption = attrNameToDisplay(top_group_by) + ' ' + top_group_keys[i];
      var title = "Counts of observations per <i>" + attrNameToDisplay(counted_attribute) + "</i> grouped by <i>" + attrNameToDisplay(bot_group_by) + "</i>";

      if(distinct === true) {
        title = "Counts of distinct <i>" + attrNameToDisplay(distinct_attribute) + "s</i> per <i>" + attrNameToDisplay(counted_attribute) + "</i> grouped by <i>" + attrNameToDisplay(bot_group_by) + "</i>";
      }

      renderHBarStacked(groups, title, counted_attribute, bot_group_by, caption);
    }
  }

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
    //  chart(groups[group_keys[i]], attrNameToDisplay(group_by) + ": " + group_keys[i], counted_attribute);
    //}

    var title = "Counts of observations per <i>" + attrNameToDisplay(counted_attribute) + "</i> grouped by <i>" + attrNameToDisplay(group_by) + "</i>";

    if(distinct === true) {
      title = "Counts of distinct <i>" + attrNameToDisplay(distinct_attribute) + "s</i> per <i>" + attrNameToDisplay(counted_attribute) + "</i> grouped by <i>" + attrNameToDisplay(group_by) + "</i>";
    }

    renderHBarStacked(groups, title, counted_attribute, group_by);

  }
  else if(group_order.length == 0) {
    if(distinct === true) {
      renderHBar(results, "Counts of <i>" + attrNameToDisplay(distinct_attribute) + "</i> per <i>" + attrNameToDisplay(counted_attribute) + "</i>", counted_attribute);
    }
    else {
      renderHBar(results, "Counts of observations per <i>" + attrNameToDisplay(counted_attribute) + "</i>", counted_attribute);
    }
  }
}


function renderResults(results) {

  if(results['state'] == 'new') {
    $('#results_msg').empty().append('<span class="txt-warn">Your query is in the queue waiting for execution. Please try again in an hour.</span>');
    return;
  }

  if(results['state'] == 'running') {
    $('#results_msg').empty().append('<span class="txt-warn">Your query is currently being executed and the results are not available yet. Please try again in an hour.</span>');
    return;
  }

  $('#results_msg').empty().append('<span class="txt-info">Rendering results...</span>');

  var rawResultsDiv = document.getElementById('raw_results');
  var result = results['result'];
  $('#raw_results').append('<pre>'+JSON.stringify(result, null, ' ')+'</pre>');
  var iql = results['iql'];
  $('#raw_query').append(JSON.stringify(iql));

  if(result != null) {
    $('#raw_results_section').css('display','block');
  }

  $('#raw_query_section').css('display','block');

  results = result['results'];


  console.log('iql', JSON.stringify(iql));

  if(!('query' in iql)) {
    return; //abort. something's more than fishy
  }

  var timestamps = extractTimestamps(iql);

  for(var i = 0; i < timestamps.length; i++) {
    if(i == 0)
     $('#raw_query').append('<br><br>----<br>Timestamps in this query:<br>');
    else
     $('#raw_query').append('<br>');
    $('#raw_query').append(timestamps[i]);
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

  $('#results_msg').empty().append('<span class="txt-info">Your results are visible below.</span>');
}


function showError(xhr, status) {
  console.log('estatus',xhr.status);
  if(xhr.status == 404) {
    $('#results_msg').empty().append('<span class="txt-warn">The supplied result id could not be found in our database. Most likely the results expired and are no longer available. Please run a new query.</span>');
  }
  else {
    $('#results_msg').empty().append('<span class="txt-err">Downloading results from server failed! Try again in an hour. If you keep seeing this message please contact us.</span>');
  }
}


function getResults(id) {
  var request = 
    $.ajax(
      {'url' : api_base + '/result?id=' + encodeURIComponent(id)})
     .done(renderResults)
     .fail(showError);
}


function table(data) {
  var table = d3.select(".table");

  var cols = Object.keys(data[0]);
  cols.sort();


  var hrow = table.append("tr");

  for(var i = 0; i < cols.length; i++) {
    hrow.append("th").text(function() { return attrNameToDisplay(cols[i]); });
  }

  var row = table.selectAll(".row").data(data).enter().append("tr");

  for(var i = 0; i < cols.length; i++) {
    row.append("td").text(function(d) { return d[cols[i]] });
  }

  $('#table_section').css('display','block');
}

function trimLongStr(str) {
  str = str.toString();
  var max_len = 33;
  if(str.length > max_len)
    return str.substring(0,max_len-2) + "...";
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


function renderHBarStacked(groups, title, counted_attribute, group_by, caption) {
  console.log('renderHBarStacked', groups, title, counted_attribute);

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

  if(caption !== undefined) {
    figure.append("div").attr("class","caption").html(caption);
  } else { console.log('no caption'); }


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
      .attr("y", barHeight /2).attr("dy", ".35em").text(trimLongStr(group_keys[i]))
      .attr("style","font-family: monospace; font-size: 13px; text-anchor: start");

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

    
    if(offset_x > 200)
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
    legend.append("text").attr("x",offset_x + barHeight+5).attr("y", offset_y + barHeight /2).attr("dy", ".35em").text(trimLongStr(cols[i]) + " (" + to_e(counted_total[cols[i]]) +")")
     .attr("style","font-family: sans-serif; font-size: 14px; text-anchor: start;")
     .attr("fill", colors[i]);
    offset_x += Math.floor(width / 2);
    if(i % 2 == 1) {
      offset_y += barHeight+5;
      offset_x = 0;
    }
  }

  
  $('#chart_section').css('display','block');
}

function renderHBar(data, title, counted_attribute) {

  console.log('chart',data);

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
      figure.append("div").attr("class","title").html(title);

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
    .text(function(d) { return trimLongStr(d[counted_attribute]) + " [" + Math.round((100*d.count/sum_count)*10)/10 + "%]"; });



  var lines = chart.append("g");
  var footer = chart.append("g")
       .attr("transform", function() { return "translate(0," + (data.length * (5+barHeight)) + ")"; });

  lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("fill","black").attr("x",width-2);
  footer.append("text").attr("x",0).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return "0"; }).attr("fill","black");

  lines.append("rect").attr("width", 2).attr("height", (5+barHeight)*data.length -5).attr("x", 0).attr("fill","black");
  footer.append("text").attr("x",width).attr("y", barHeight /2).attr("dy", ".35em").text(function() { return max_count + ""; }).attr("fill","black").attr("style","text-anchor: end;");

  $('#chart_section').css('display','block');
}
