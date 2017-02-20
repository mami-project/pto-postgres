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
  if(name.indexOf('@') == 0 || name.indexOf('$') == 0)
    name = name.substring(1);

  if(name in attr_display_names)
    return attr_display_names[name];
  return name;
}

function convertGrouping(grouping, distinct) {
  var count_str;

  console.log('grouping',grouping);

  if(grouping.length == 1) {
    count_str = 'Count <i>' + distinct + 's</i> per <i>' + attrNameToDisplay(grouping[0]) + '</i>';
  }
  else if(grouping.length == 2) {
    count_str = 'Count <i>' + distinct + 's</i> per <i>' + attrNameToDisplay(grouping[1]) + '</i> grouped by ';
    count_str += '<i>' + attrNameToDisplay(grouping[0]) + '</i>';
  }
  else if(grouping.length == 3) {
    count_str = 'Count <i>' + distinct + 's</i> per <i>' + attrNameToDisplay(grouping[2]) + '</i> grouped by ';
    count_str += '<i>' + attrNameToDisplay(grouping[0]) + '</i> then by <i>' + attrNameToDisplay(grouping[1]) + '</i>';
  }
  
  return count_str;
}

function convertSimple(simple) {
  console.log('simple', JSON.stringify(simple));

  if(simple.length != 1) {
    throw "Can't convert this. #1";
  }
  
  simple = simple[0];

  var ands = [];
  
  if(!('and' in simple))
    ands = [simple];
  else  
    ands = simple['and'];
  
  if(!(ands.length >= 1))
    throw "Can't convert this. #3";
    
  var in_ = ands[0];
  
  if(!('in' in in_))
    throw "Can't convert this. #4";
    
  in_ = in_['in'];
  
  if(!(in_.length == 2))
    throw "Can't convert this. #5";
    
  if(in_[0] != '@name')
    throw "Can't convert this. #6";
    
  if(in_[1].length < 1)
    throw "Can't convert this. #7";
    
  var condition = in_[1][0];
  
  var parts = condition.split('.');
  parts = parts.slice(0,parts.length-1);
  condition = parts.join('.') + '.';
  
  for(var i = 0; i < in_[1].length; i++)
    if(in_[1][i].indexOf(condition) != 0)
      throw "Can't convert this. #8";
  
  condition = condition + '*';

  console.log('condition', condition);

  var ge = ands[1];
  
  if(!('ge' in ge))
    throw "Can't convert this. #9";
    
  ge = ge['ge'];
  
  if(ge.length != 2)
    throw "Can't convert this. #10";
    
  if(ge[0] != "@time_from")
    throw "Can't convert this. #11";
    
  var ge_time = ge[1];
  
  if(!('time' in ge_time))
    throw "Can't convert this. #12";
    
  ge_time = ge_time['time'];
  
  if(ge_time.length != 1)
    throw "Can't convert this. #13";
    
  var time_from = ge_time[0];
  
  var le = ands[2];
  
  if(!('le' in le))
    throw "Can't convert this. #14";
  
  le = le['le'];
  
  if(le.length != 2)
    throw "Can't convert this. #15";
    
  if(le[0] != "@time_to")
    throw "Can't convert this. #16";
    
  var le_time = le[1];
  
  if(!('time' in le_time))
    throw "Can't convert this. #17";
    
  le_time = le_time['time'];
  
  if(le_time.length != 1)
    throw "Can't convert this. #18";
    
  var time_to = le_time[0];
  
  return " for conditions " + condition + '<br>from <i>' + new Date(time_from*1000.0).toUTCString()
    + '</i><br>to <i>' + new Date(time_to*1000.0).toUTCString() + '</i>';
}

function convertIQL(iql) {
  var query = iql['query'];
  
  if('count' in query) {
    var count_str = "";
  
    var operands = query['count'];
    if(operands.length == 3) {
      count_str = convertGrouping(operands[0], 'observation') + '<br>';
      count_str += convertSimple(operands[1]['simple']);
    }
    

    
    return count_str;
  }
  else if('count-distinct' in query) {
    
    
    var count_str = "";

    var operands = query['count-distinct'];

    if(operands.length == 3) {
      var distinct_attr = operands[0][operands[0].length-1];
      operands[0] = operands[0].slice(0,operands[0].length-1);

      count_str = convertGrouping(operands[0], attrNameToDisplay(distinct_attr)) + '<br>';
      count_str += convertSimple(operands[1]['simple']);
    }

    return count_str;
  }
}

function toEnglish(iql) {
  try {
    return convertIQL(iql);
  }
  catch(err) {
    console.log(err, JSON.stringify(iql));
    return JSON.stringify(iql);
  }
}
