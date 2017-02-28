function QueryQueue() {
  var me = this;

  this._states = {
    "done" : "completed",
    "running" : "running",
    "new" : "queued",
    "failed" : "failed"
  };

  this.render =
   function(targetElement) {
    if(targetElement == undefined)
      targetElement = me.targetElement;

    targetElement.empty();

    if(me.m == undefined) {
      targetElement.append($('<span>')
                             .attr('class','txt-err')
                             .text('There was an error downloading the data from the server!'));
      return;
    }

    if(me.m.length < 1) {
      targetElement.append($('<span>').text("No queries found"));
      return;
    }

    var table = d3.select(document.createElement('table')).attr('class','table');

    var hrow = table.append("tr");
    hrow.append("th").text("id");
    hrow.append("th").text("State");
    hrow.append("th").text("Duration");
    hrow.append("th").text("Query");

    for(var i = 0; i < me.m.length; i++) {
      var tr = table.append("tr");
      var d = me.m[i];
      tr.append("td").append("a").text(d['id'].substring(0,6)+'...').attr("href","qui.html?" + encodeURIComponent(d['id'])).attr("class","linky2");
      tr.append("td").text(me._states[d['state']]);
      tr.append("td").text(secondsToDisplay(d['duration']));
      tr.append("td").html(toEnglish(d['iql'])).attr("class","code").attr("style", "text-align: left");
    }

    targetElement.append($(table[0]));
   }

  this.updateAndRender =
   function(mNew, targetElement) {
    console.log(me);
    me.m = mNew;
    me.render(targetElement);
   }
}

var _QueryQueue = new QueryQueue();

$(document).ready(function() {
  _QueryQueue.targetElement = $('#c_queryqueue');
  getQQSummary(_QueryQueue.updateAndRender);
});
