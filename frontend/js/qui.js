function disableAndEmpty(it) {
  it.prop('disabled', true);
  it.empty();
}

function enable(it) {
  it.prop('disabled', false);
}

function QUI() {
  var me = this;

  /*
     This contains the selected options and provided
     input values. 
   */
  this.m = {
  };

  /*
     This contains all conditions
   */
  this._conditions = {
    "ecn.connectivity" : {
       "works" : "It works!",
       "broken" : "It broke!"
     },
    "ecn.connectivity.super" : {
       "weird" : "It weird!"
    }
  };

  /*
     This contains all attributes
   */
  this._attributes = {
    "week" : {
      "name" : "Week",
      "desc" : "Week of year"
    }
  };

  this.render = 
   function() {
     me.renderConditionsSelect();
     me.renderPerSelect();
   };

  this.renderPerSelect =
   function() {
     var perSelect = $('#i_per');
     disableAndEmpty(perSelect);

     var attributes = Object.keys(me._attributes);


     var option = 
      $('<option>')
       .attr('value', 'no')
       .text('Observation');
     
     if('per' in me.m)
       if(me.m['per'] == 'no')
         option.prop('selected', true);

     if(!('per' in me.m)) {
       option.prop('selected', true);
     }

     perSelect
      .append(option);

     for(var i = 0; i< attributes.length; i++) {
       option = 
        $('<option>')
         .attr('value', attributes[i])
         .text(me._attributes[attributes[i]]['name'])

       if('per' in me.m)
         if(me.m['per'] == attributes[i])
           option.prop('selected', true);
 
       perSelect
        .append(option);
     }

     enable(perSelect);
   };

  this.renderConditionsSelect =
   function() {
     var conditionsSelect = $('#i_conditions');
     disableAndEmpty(conditionsSelect);

     var conditions = Object.keys(me._conditions);

     console.log('conditions', conditions, conditions.length);

     for(var i = 0; i < conditions.length; i++) {
       console.log(conditions[i], i);
       var conditionText = conditions[i];

       var subConditions = Object.keys(me._conditions[conditions[i]]);

       conditionText = conditionText + ".(" + subConditions.join(', ') + ")";

       conditionsSelect
        .append($('<option>')
                 .attr('value', conditions[i])
                 .text(conditionText));
     }

     enable(conditionsSelect);
   };
}


var _QUI = new QUI();

$(document).ready(function() {
  _QUI.render();
});
