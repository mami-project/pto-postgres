function Navigation() {
  this.m = [
    ["PTO Home" , "./"],
    ["Run Query" , "./qui.html"],
    ["Query Queue" , "./qq.html"],
    ["Upload statistics" , "./uploadstats.html"]
  ];
}

Navigation.prototype.render = 
  function(targetElement) {
    console.log(targetElement);
    var ul = $('<ul>');

    for(var i = 0; i < this.m.length; i++) {
      ul.append($('<li>')
        .append($('<a>')
          .attr("href", this.m[i][1])
          .text(this.m[i][0])));
    }

    targetElement.empty().append(ul);
  }

var _Navigation = new Navigation();

$(document).ready(function(){
  _Navigation.render($('#c_navigation'));
});


