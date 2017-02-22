var attr_display_names = {
  "observation_set" : "Observation set",
  "full_path" : "Path",
  "name" : "Condition",
  "count" : "Count",
  "location" : "Location",
  "week" : "Week",
  "month" : "Month"
};

/**
 * attrNameToDisplay
 *  - name
 *
 * Convert the name of an attribute to human readable
 * names.
 */
function attrNameToDisplay(name) {
  if(name.indexOf('@') == 0 || name.indexOf('$') == 0)
    name = name.substring(1);

  if(name in attr_display_names)
    return attr_display_names[name];
  return name;
}


function extractGrouping(grouping, dict) {
  if(grouping.length == 0) {
    return;
  }
  else if(grouping.length == 1) {
    dict['per'] = grouping[0];
  }
  else if(grouping.length == 2) {
    dict['group_by'] = grouping[0];
    dict['per'] = grouping[1];
  }
  else if(grouping.length == 3) {
    dict['group_by'] = grouping[0];
    dict['then_by'] = grouping[1];
    dict['per'] = grouping[2];
  }
}


function extractQuery(iql) {
  var query = iql['query'];

  var dict = {};
  
  if('count' in query) {  
    var operands = query['count'];

    if(operands.length == 3) {
      dict['count'] = 'observations'
      extractGrouping(operands[0], dict);
      extractSimple(operands[1]['simple'], dict);
      return dict;
    }

  }
  else if('count-distinct' in query) {
    var operands = query['count-distinct'];

    if(operands.length == 3) {
      var distinct_attr = operands[0][operands[0].length-1];
      dict['count'] = distinct_attr;

      operands[0] = operands[0].slice(0,operands[0].length-1);

      extractGrouping(operands[0], dict);
      extractSimple(operands[1]['simple'], dict);
      return dict;
    }

  }
  
  throw "Can't extract";
}


function extractSimple(simple, dict) {
  console.log('simple', JSON.stringify(simple));

  if(simple.length != 1) {
    throw "Can't extract";
  }
  
  simple = simple[0];

  var ands = [];
  
  if(!('and' in simple))
    ands = [simple];
  else  
    ands = simple['and'];
  
  if(!(ands.length >= 1))
    throw "Can't extract";
    
  var in_ = ands[0];
  
  if(!('in' in in_))
    throw "Can't extract";
    
  in_ = in_['in'];
  
  if(!(in_.length == 2))
    throw "Can't extract";
    
  if(in_[0] != '@name')
    throw "Can't extract";
    
  if(in_[1].length < 1)
    throw "Can't extract";
    
  var condition = in_[1][0];
  
  var parts = condition.split('.');
  parts = parts.slice(0,parts.length-1);
  condition = parts.join('.') ;
  
  for(var i = 0; i < in_[1].length; i++)
    if(in_[1][i].indexOf(condition) != 0)
      throw "Can't extract";


  console.log('condition', condition);

  dict['conditions'] = condition;

  var ge = ands[1];
  
  if(!('ge' in ge))
    throw "Can't extract";
    
  ge = ge['ge'];
  
  if(ge.length != 2)
    throw "Can't extract";
    
  if(ge[0] != "@time_from")
    throw "Can't extract";
    
  var ge_time = ge[1];
  
  if(!('time' in ge_time))
    throw "Can't extract";
    
  ge_time = ge_time['time'];
  
  if(ge_time.length != 1)
    throw "Can't extract";
    
  var time_from = ge_time[0];

  dict['time_from'] = time_from;
  
  var le = ands[2];
  
  if(!('le' in le))
    throw "Can't extract";
  
  le = le['le'];
  
  if(le.length != 2)
    throw "Can't extract";
    
  if(le[0] != "@time_to")
    throw "Can't extract";
    
  var le_time = le[1];
  
  if(!('time' in le_time))
    throw "Can't extract";
    
  le_time = le_time['time'];
  
  if(le_time.length != 1)
    throw "Can't extract";
    
  var time_to = le_time[0];

  dict['time_to'] = time_to;

  extractPathCriteria(ands.slice(3), dict);
}


function extractPathCriteria(ands, dict) {
  if(ands.length == 0)
    return "";

  for(var i = 0; i < ands.length; i++) {
    var and_ = ands[i];
    if(!('in' in and_))
      throw "Can't extract";

    var in_ = and_['in'];

    if(in_.length != 2)
      throw "Can't extract";

    var attr = in_[0];
    var values = in_[1];

    if(attr == "@source" || attr == "@target") {
      dict[attr.substring(1)] = values.join(', ');
    }
  }
}



/**
 * toEnglish
 *  - iql
 *  - default_ - default text
 * 
 * convert IQL to english (html).
 * if default_ is undefined in case no translation
 * is available it returns the IQL as string.
 * if default_ is set in case no translation is available
 * it returns default_.
 */
function toEnglish(iql, default_) {
  iql = JSON.parse(JSON.stringify(iql)); // work on a copy to be on the safe side.

  try {
    var params = extractQuery(iql);
    var str = "";

    if('count' in params) {
      str += '<b>Count</b> ' + attrNameToDisplay(params['count']) + ' ';
    }

    if('per' in params) {
      str += '<b>per</b> ' + attrNameToDisplay(params['per']) + '<br>';
    }

    if('group_by' in params) {
      str += '<b>grouped by</b> ' + attrNameToDisplay(params['group_by']) + '<br>';
    }

    if('then_by' in params) {
      str += '<b>then by</b> ' + attrNameToDisplay(params['then_by']) + '<br>';
    }

    if('time_from' in params) {
      str +=' <b>from</b> ' + new Date(params['time_from']*1000).toUTCString() + '<br>';
    }

    if('time_to' in params) {
      str += '<b>to</b> ' + new Date(params['time_to']*1000).toUTCString() + '<br>';
    }

    if('source' in params || 'target' in params) {
      str += '<b>where</b> ';
    }

    if('source' in params) {
      str += 'Vantaga Point <b>is one of</b> (' + params['source'] + ')<br>';
    }

    if('target' in params) {
      if('source' in params) 
        str += '<b>and</b> ';

      str += 'Target <b>is one of</b> (' + params['target'] + ')';
    }

    return str;
  }
  catch(err) {
    console.log(err, JSON.stringify(iql));
    if(default_ == undefined)
      return JSON.stringify(iql);
    else
      return default_;
  }
}
