function getUploadStats() {
  var request = 
    $.ajax(
      {'url' : api_base + '/upload-stats'})
     .done(renderUploadStats)
     .fail(showError);
}

function showError() { 
  var cell = $('#uploadstats_cell').empty();
  cell.append('There was an error downloading the upload statistics from the server. Please come back later.');
}

function renderUploadStats(data) {
  var table = d3.select("#uploadstats");

  var cols = Object.keys(data);
  cols.sort();
  console.log('cols', cols);

  var hrow = table.append("tr");
  hrow.append("th").text("Campaign");
  hrow.append("th").text("Uploads");


  for(var i = 0; i < cols.length; i++) {
    var row = table.append("tr");
    console.log(data[cols[i]]);
    row.append("td").text(cols[i]);
    row.append("td").text(data[cols[i]]);
    console.log('row added');
  }

  console.log('done');
}
