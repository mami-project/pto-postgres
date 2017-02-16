function getRecent() {
  var request = 
    $.ajax(
      {'url' : api_base + '/qq/recent'})
     .done(function (data) { renderQQ(data) })
     .fail(showError);
}

function getNew() {
  var request = 
    $.ajax(
      {'url' : api_base + '/qq/new'})
     .done(function (data) { renderQQ(data) })
     .fail(showError);
}

function getRunning() {
  var request = 
    $.ajax(
      {'url' : api_base + '/qq/running'})
     .done(function (data) { renderQQ(data, true) })
     .fail(showError);
}

function showError() { 
  var cell = $('#qq_err').empty();
  cell.append('There was an error downloading the data from the server. Please come back later.');
}


function renderQQ(data, have_duration) {

  $('#qq').empty();
  $('#qqerr').empty();

  if(have_duration == undefined || have_duration == null)
    have_duration = false;

  console.log('have_duration',have_duration);

  if(data.length == 0) {
    var cell = $('#qqerr').empty();
    cell.append('No queries found.');
    return;
  }

  var table = d3.select("#qq");

  

  var hrow = table.append("tr");
  hrow.append("th").text("id");
  if(have_duration)
    hrow.append("th").text("Duration");
  hrow.append("th").text("IQL").attr("style","text-align: center");


  for(var i = 0; i < data.length; i++) {
    var row = table.append("tr");
    row.append("td").append("a").text(data[i]['id']).attr("href","results.html?" + encodeURIComponent(data[i]['id'])).attr("class","linky2");
    if(have_duration)
      row.append("td").text(data[i]['duration']+'s')
    row.append("td").text(JSON.stringify(data[i]['iql'])).attr("class","code").attr("style", "text-align: left");
    console.log('row added');
  }

  console.log('done');
}
