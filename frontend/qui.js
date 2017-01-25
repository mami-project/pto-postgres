var api_base = 'https://observatory.mami-project.eu/papi';

function is_prefix(xs, ys) {
  if (xs.length > ys.length) {
    return false;
  }

  for(var i = 0; i < xs.length; i++) {
    if(xs[i] != ys[i])
      return false;
  }

  return true;
}

function process_failed_response(data) {
  alert('failed :(');
  console.log(JSON.stringify(data));
}

function process_successful_response(data) {
  console.log(JSON.stringify(data));
  if("already" in data) {
    $("#query_msg").empty()
    .append('The results for your query are already present. ')
    .append('Please click on the link below to retrieve your results: <br>')
    .append('<a href="results.html?' + encodeURIComponent(data['query_id']) + '">Retrieve results</a>');
  }
  else {
    $("#query_msg").empty()
    .append('Your query has been submitted and has been put into a queue. You can retrieve your results ')
    .append('through the link below: <br>')
    .append('<a href="results.html?' + encodeURIComponent(data['query_id']) + '">Retrieve results</a>');
  }

}


function toDate(date_s) {
  var t_ms = Date.parse(date_s);
  if(isNaN(t_ms)) {
    return t_ms;
  }

  return Math.floor(t_ms / 1000);
}


function runQuery() {
  var conditions = $("#i_conditions").val();
  var group_by = $("#i_group_by").val();
  var time_from = $("#i_time_from").val();
  var time_to = $("#i_time_to").val();
  var count = $("#i_count").val();


  if((time_from != "" && isNaN(toDate(time_from))) || (time_to != "" && isNaN(toDate(time_to)))) {
    $("#query_msg").empty().append('time_to or time_from contain invalid input. Please correct them!');
    return;
  }

  console.log("conditions",conditions);
  console.log("group_by", group_by);
  console.log("time_from", time_from);
  console.log("time_to", time_to);
  console.log("count", count);

  var all_conditions = [
    {"path":["ecn","connectivity","works"],"id":2},
    {"path":["ecn","connectivity","broken"],"id":3},
    {"path":["ecn","connectivity","offline"],"id":5},
    {"path":["ecn","connectivity","transient"],"id":4},
    {"path":["ecn","negotiation_attempt","succeeded"],"id":7},
    {"path":["ecn","negotiation_attempt","failed"],"id":8},
    {"path":["ecn","ect_one","seen"],"id":-1},
    {"path":["ecn","ect_zero","seen"],"id":-1},
    {"path":["ecn","ce","seen"],"id":-1}
  ];

  var condition_ = conditions.split(".");
  console.log('condition_', condition_);

  var related_conditions = [];
  
  for(var i = 0; i < all_conditions.length; i++) {
    var other_condition = all_conditions[i];
    if( (other_condition['path'].length - condition_.length) != 1)
      continue; //skip because it's not related

    if(is_prefix(condition_, other_condition['path'])) {
      related_conditions.push(other_condition['path'].join('.'));
      console.log('related condition', other_condition);
    }
  }

  console.log('related_conditions',related_conditions);

  var iql_condition_parts = [];

  for(var i = 0; i < related_conditions.length; i++) {
    iql_condition_parts.push({"eq":["@name",related_conditions[i]]});
  }

  console.log('iql_condition_parts', JSON.stringify(iql_condition_parts));

  iql_time_parts = [];

  if(time_from != "")
    iql_time_parts.push({"ge":["@time_from",{"time":[toDate(time_from)]}]})

  if(time_to != "")
    iql_time_parts.push({"le":["@time_to",{"time":[toDate(time_to)]}]})

  var exp_ = {"or":iql_condition_parts};

  if(iql_time_parts.length == 0) {
    exp_ = exp_;
  }
  else if(iql_time_parts.length == 1) {
    exp_ = {"and":[exp_,iql_time_parts[0]]};
  }
  else if(iql_time_parts.length == 2) {
    exp_ = {"and":[exp_,iql_time_parts[0],iql_time_parts[1]]};
  }

  
  var query = {"settings":{"order":['@'+count,'asc']},"query":{"count":[['@' + group_by, '@'+count], {"simple":[exp_]}]}};

  if(group_by == 'no') 
    query = {"settings":{"order":['@'+count,'asc']},"query":{"count":[['@'+count], {"simple":[exp_]}]}};
  
  var str_query = JSON.stringify(query);

  var url = api_base + '/query?q=' + encodeURIComponent(str_query);

  var request = $.ajax({'url': url});
  request.done(process_successful_response);
  request.fail(process_failed_response);
}
