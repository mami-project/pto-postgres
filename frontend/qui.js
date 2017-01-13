var api_base = 'http://localhost:5000';

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

function runQuery() {
  var conditions = $("#i_conditions").val();
  var group_by = $("#i_group_by").val();
  var time_from = $("#i_time_from").val();
  var time_to = $("#i_time_to");

  console.log("conditions",conditions);
  console.log("group_by", group_by);
  console.log("time_from", time_from);
  console.log("time_to", time_to);

  var all_conditions = [
    {"path":["ecn","connectivity","works"],"id":2},
    {"path":["ecn","connectivity","broken"],"id":3},
    {"path":["ecn","connectivity","offline"],"id":5},
    {"path":["ecn","connectivity","transient"],"id":4},
    {"path":["ecn","negotiation_attempt","succeeded"],"id":7},
    {"path":["ecn","negotiation_attempt","failed"],"id":8}
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

  var query = {"query":{"count":[['@' + group_by, '@name'], {"simple":[{"or":iql_condition_parts}]}]}};
  
  var str_query = JSON.stringify(query);

  var url = api_base + '/query?q=' + encodeURIComponent(str_query);

  var request = $.ajax({'url': url});
  request.done(process_successful_response);
  request.fail(process_failed_response);
}
