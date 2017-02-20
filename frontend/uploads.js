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


function sizeToStr(size) {
  if(size >= 1024*1024) {
    return Math.round(10*size / (1024*1024))/10 + "TB";
  }
  if(size >= 1024) {
    return Math.round(10*size / (1024))/10 + "GB";
  }
  if(size == null || size == undefined)
    return "n/a";

  if(size < 1)
    return "<1MB";

  return Math.round(10*size)/10 + "MB";
}


function convertDate(date) {
  return new Date(date).toUTCString();
}


function renderUploadStats(data) {
  var table = d3.select("#uploadstats");

  var cols = Object.keys(data);
  cols.sort();
  console.log('cols', cols);

  var hrow = table.append("tr");
  hrow.append("th").text("Campaign");
  hrow.append("th").text("Uploads");
  hrow.append("th").text("From");
  hrow.append("th").text("To");
  hrow.append("th").text("Size");


  for(var i = 0; i < cols.length; i++) {
    var row = table.append("tr");
    console.log(data[cols[i]]);
    row.append("td").text(cols[i]);
    row.append("td").text(data[cols[i]]['count']).attr("style","text-align: right;");
    row.append("td").text(convertDate(data[cols[i]]['first_msmnt']));
    row.append("td").text(convertDate(data[cols[i]]['last_msmnt']));
    row.append("td").text(sizeToStr(data[cols[i]]['file_size'])).attr("style","text-align: right;");
    console.log('row added');
  }

  console.log('done');
}
