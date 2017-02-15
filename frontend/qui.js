
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
    .append(new Date().toString() + '<br>')
    .append('The results for your query are already present. ')
    .append('Please click on the link below to retrieve your results: <br>')
    .append('<a href="results.html?' + encodeURIComponent(data['query_id']) + '">Retrieve results</a>');
  }
  else {
    $("#query_msg").empty()
    .append(new Date().toString() + '<br>')
    .append('Your query has been submitted and has been put into a queue. You can retrieve your results ')
    .append('through the link below: <br>')
    .append('<a href="results.html?' + encodeURIComponent(data['query_id']) + '">Retrieve results</a>');
  }

}


function toDate(date_s) {

  date_s = date_s.replace("start","00:00:00 GMT+0000");
  date_s = date_s.replace("end","23:59:59 GMT+0000");

  var t_ms = Date.parse(date_s);
  if(isNaN(t_ms)) {
    return t_ms;
  }

  return Math.floor(t_ms / 1000);
}


function submitQuery(query) {
  var str_query = JSON.stringify(query);

  var url = api_base + '/query?q=' + encodeURIComponent(str_query);

  console.log('str_query',str_query);

  var request = $.ajax({'url': url});
  request.done(process_successful_response);
  request.fail(process_failed_response); 
}

function ecnSupportQuery() {
  var selected_window = $('#i_ecn_support_time_window').val();

  var windows = {
    "Nov 2016" : [toDate("01 Nov 2016 start"), toDate("30 Nov 2016 end")],
    "Dec 2016" : [toDate("01 Dec 2016 start"), toDate("31 Dec 2016 end")],
    "Jan 2017" : [toDate("01 Jan 2017 start"), toDate("31 Jan 2017 end")]
  };

  var exp_conditions = {"or":[
        {"eq":["@name","ecn.connectivity.works"]},
        {"eq":["@name","ecn.connectivity.broken"]},
        {"eq":["@name","ecn.connectivity.transient"]},
        {"eq":["@name","ecn.connectivity.offline"]}
   ]};

  var exp_ = {"and":[
     exp_conditions,
     {"ge":["@time_from",{"time":[windows[selected_window][0]]}]},
     {"le":["@time_to",{"time":[windows[selected_window][1]]}]}
   ]};

  query = {"query":{"count":[["@name"],{"simple":[exp_]},"asc"]}};

  submitQuery(query);
}


function runQuery() {
  var conditions = $("#i_conditions").val();
  var group_by = $("#i_group_by").val();
  var then_by = $("#i_then_by").val();
  var time_from = $("#i_time_from").val();
  var time_to = $("#i_time_to").val();
  var count = $("#i_count").val();
  var per = $('#i_per').val();


  if((time_from != "" && isNaN(toDate(time_from))) || (time_to != "" && isNaN(toDate(time_to)))) {
    $("#query_msg").empty().append('time_to or time_from contain invalid input. Please correct them!');
    return;
  }

  if(group_by == "no" && then_by != "no") {
    $("#query_msg").empty().append("Can't not group and then group. Please correct grouping!");
    return;
  }

  if(per == 'no' && (group_by != "no" || then_by != "no")) {
    $("#query_msg").empty().append("Group by/then by specified but nothing for per. The group order must be per -> group by -> then by");
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
    {"path":["ecn","connectivity","super","works"],"id":-1},
    {"path":["ecn","connectivity","super","broken"],"id":-1},
    {"path":["ecn","connectivity","super","offline"],"id":-1},
    {"path":["ecn","connectivity","super","transient"],"id":-1},
    {"path":["ecn","connectivity","super","weird"],"id":-1},
    {"path":["ecn","negotiation_attempt","succeeded"],"id":7},
    {"path":["ecn","negotiation_attempt","failed"],"id":8},
    {"path":["ecn","ect_one","seen"],"id":-1},
    {"path":["ecn","ect_zero","seen"],"id":-1},
    {"path":["ecn","ce","seen"],"id":-1},
    {"path":["ecn","site_dependent","strict"],"id":-1},
    {"path":["ecn","site_dependent","strong"],"id":-1},
    {"path":["ecn","site_dependent","weak"],"id":-1},
    {"path":["ecn","path_dependent","strict"],"id":-1},
    {"path":["ecn","path_dependent","strong"],"id":-1},
    {"path":["ecn","path_dependent","weak"],"id":-1},
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

  var iql_count_parts = [];
  var query = {};

  if(group_by != 'no') {
    iql_count_parts.push('@'+group_by);
  }
  if(then_by != 'no') {
    iql_count_parts.push('@'+then_by);
  }
  if(per != 'no') {
    iql_count_parts.push('@'+per);
  }


  if(count == 'no') { // no distinct counting
    if(group_by == 'no' && then_by == 'no' && per == 'no') { //absolutely no grouping
      query = {"query":{"count":[{"simple":[exp_]}]}};
    }
    else {
      query = {"query":{"count":[iql_count_parts,{"simple":[exp_]},"asc"]}};
    }
  }
  else {
    iql_count_parts.push('@'+count);
    query = {"query":{"count-distinct":[iql_count_parts,{"simple":[exp_]},"asc"]}};
  }
  
  var str_query = JSON.stringify(query);

  var url = api_base + '/query?q=' + encodeURIComponent(str_query);

  console.log('str_query',str_query);

  

  var request = $.ajax({'url': url});
  request.done(process_successful_response);
  request.fail(process_failed_response); 
}
