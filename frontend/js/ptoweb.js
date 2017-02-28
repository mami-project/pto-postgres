/*
  Function: Navigation

  Responsible for rendering the navigation on the top.
 */
function Navigation() {
  var me = this;

  this.m = [
    ["PTO Home" , "./"],
    ["Run Query" , "./qui.html"],
    ["Query Queue" , "./qq.html"],
    ["Upload statistics" , "./uploadstats.html"]
  ];

  this.render = 
   function(targetElement) {
    if(targetElement == undefined)
      targetElement = this.targetElement;
 
    var ul = $('<ul>');

    for(var i = 0; i < this.m.length; i++) {
      ul.append($('<li>')
        .append($('<a>')
          .attr("href", this.m[i][1])
          .text(this.m[i][0])));
    }

    targetElement.empty().append(ul);
   }

  this.updateAndRender = 
   function(mNew, targetElement) {
     me.m = mNew;
     me.render(targetElement);
   }
}

var _Navigation = new Navigation();

$(document).ready(function(){
  _Navigation.render($('#c_navigation'));
});

/*
  Function: secondsToDisplay

  Converts seconds into a human readable string
  using suffixes such as s, min and h.

  Parameters:

    seconds - Integer

  Returns:

    String
 */
function secondsToDisplay(seconds) {
  if(seconds < 90) {
    return seconds + "s";
  }
  else if(seconds < 60*60) {
    minutes = Math.round(10*seconds/60)/10;
    return minutes + "min";
  }
  else {
    hours = Math.round(10*seconds/(60*60))/10;
    return hours + "h";
  }
}

/*
  Function: getQQSummary

  API-Call to /qq/summary

  Parameters:

    callback - Function to call when data is ready

  Returns:

    Nothing.
 */
function getQQSummary(callback) {
  var request =
    $.ajax(
      {'url' : api_base + '/qq/summary'})
     .done(function (data) { callback(data); })
     .fail(function() { callback(undefined); });
}

/*
   Function: extractMonthFromTimestamp

   Extracts the month as 3-letter string from the unix timestamp (seconds).

   Parameters:

     timestamp - Unix timestamp as seconds passed since 1970.

   Returns:

     3-letter string (Jan, Feb, ...)
 */
function extractMonthFromTimestamp(timestamp) {
  var d = new Date(timestamp*1000);
  var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  return months[d.getUTCMonth()];
}

/*
   Function: extractDayFromTimestamp

   Extracts the day as 2-letter string from the unix timestamp (seconds).

   Parameters:

     timestamp - Unix timestamp as seconds passed since 1970.

   Returns:

     2-letter string (01, 31, ...)
 */
function extractDayFromTimestamp(timestamp) {
  var d = new Date(timestamp*1000);
  var day =  d.getUTCDate().toString();

  if(day.length != 2)
    day = '0' + day;

  return day;
}

/*
   Function: extractYearFromTimestamp

   Extracts the year as 4-letter string from the unix timestamp (seconds).

   Parameters:

     timestamp - Unix timestamp as seconds passed since 1970.

   Returns:

     4-letter string (2016, 2017, ...)
 */
function extractYearFromTimestamp(timestamp) {
  var d = new Date(timestamp*1000);
  var year = d.getUTCFullYear().toString();

  while(year.length < 4)
    year = '0' + year;
  
  return year;
}
