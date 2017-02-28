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

function getQQSummary(callback) {
  var request =
    $.ajax(
      {'url' : api_base + '/qq/summary'})
     .done(function (data) { callback(data); })
     .fail(function() { callback(undefined); });
}
