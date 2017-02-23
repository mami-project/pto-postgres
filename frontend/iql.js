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
  console.log('ex iql', JSON.stringify(iql));
  var query = iql['query'];
  console.log('ex query', JSON.stringify(query));

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
  splitDate('from', dict);
  
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
  splitDate('to', dict);

  extractPathCriteria(ands.slice(3), dict);
}


function splitDate(what, dict) {
  if(!(('time_' + what) in dict)) {
    return false;
  }

  var d = new Date(dict['time_' + what]*1000);

  var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  
  var day =  d.getUTCDate().toString();
  if(day.length != 2)
    day = '0' + day;

  var year = d.getUTCFullYear().toString();

  dict['month_' + what] = months[d.getUTCMonth()];
  dict['day_' + what] = day;
  dict['year_' + what] = year;
  
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

function escapeHtml(str) {
  str = str.replace('&', '&amp;');
  str = str.replace('<', '&lt;');
  str = str.replace('>', '&gt;');
  str = str.replace('\'', '&apos;');
  str = str.replace('"', '&quot;');

  return str;
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
      str += '<b>Count</b> ' + escapeHtml(attrNameToDisplay(params['count'])) + ' ';
    }

    if('per' in params) {
      str += '<b>per</b> ' + escapeHtml(attrNameToDisplay(params['per'])) + '<br>';
    }

    if('group_by' in params) {
      str += '<b>grouped by</b> ' + escapeHtml(attrNameToDisplay(params['group_by'])) + '<br>';
    }

    if('then_by' in params) {
      str += '<b>then by</b> ' + escapeHtml(attrNameToDisplay(params['then_by'])) + '<br>';
    }

    if('conditions' in params) {
      str += '<b>restricted to</b> conditions <b>matching</b> <u>' + escapeHtml(params['conditions']) + '.*</u><br>';
    }

    if('time_from' in params) {
      str +=' <b>from</b> ' + escapeHtml(new Date(params['time_from']*1000).toUTCString()) + '<br>';
    }

    if('time_to' in params) {
      str += '<b>to</b> ' + escapeHtml(new Date(params['time_to']*1000).toUTCString()) + '<br>';
    }

    if('source' in params || 'target' in params) {
      str += '<b>where</b> ';
    }

    if('source' in params) {
      str += 'Vantage Point <b>is one of</b> (' + escapeHtml(params['source']) + ')<br>';
    }

    if('target' in params) {
      if('source' in params) 
        str += '<b>and</b> ';

      str += 'Target <b>is one of</b> (' + escapeHtml(params['target']) + ')';
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
