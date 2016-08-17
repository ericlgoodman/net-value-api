/**
 * @author Eric Goodman
 */

//Return base URL for search API
function getSearchApiUrl() {
  return "http://127.0.0.1:5000/api/search/";
}

//Return base URL for player API
function getPlayerApiUrl() {
  return "http://127.0.0.1:5000/api/player";
}

//Make the spinning wheel at target_id, with desired radius
function makeSpinner(target_id, rad) {
  var opts = {
  lines: 7 // The number of lines to draw
, length: 0 // The length of each line
, width: 6 // The line thickness
, radius: rad // The radius of the inner circle
, scale: 1 // Scales overall size of the spinner
, corners: 1 // Corner roundness (0..1)
, color: '#000' // #rgb or #rrggbb or array of colors
, opacity: 0 // Opacity of the lines
, rotate: 0 // The rotation offset
, direction: 1 // 1: clockwise, -1: counterclockwise
, speed: 1.5 // Rounds per second
, trail: 80 // Afterglow percentage
, fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
, zIndex: 2e9 // The z-index (defaults to 2000000000)
, className: 'spinner' // The CSS class to assign to the spinner
, top: '50%' // Top position relative to parent
, left: '50%' // Left position relative to parent
, shadow: false // Whether to render a shadow
, hwaccel: false // Whether to use hardware acceleration
, position: 'absolute' // Element positioning
  };
  var target = document.getElementById(target_id);
  var spinner = new Spinner(opts).spin(target);
}


//Function to clean up players' names in case there are duplicate names
function cleanPlayerName(name) {
  if (name.includes("|")) {
    name = name.split("|")[0];
  }
  return name;
}

//Function to normalize the display of players' values
//Returns the string repr. of the float value of a player
function valueDisplay(float) {
  var display = "";
  //if millions of euros
  if (float === 0) {
    display = "Free Transfer";
  }
  else if (float>=1) {
    display = "€" + float.toString() + " M";
  }
  else {
    float*=1000;
    display = "€" + float.toString() + " K";
  }
  return display;
}

//Create the HTML for displaying a player page
function loadPlayer(data, name, team) {
  //Parse JSON
  data = data.query_results;

  //Store local data
  var value = valueDisplay(data[0]);
  var nationality = data[1];
  var position = data[2];
  var age = data[3];
  var image_link = data[4];
  var transfers = data[5];

  //Remove the spinner
  var load = document.getElementById("load");
  load.parentNode.removeChild(load);

  //Append simple UI
  $('#container').append("<nav class='navbar navbar-default'><div" +
    "class='container'><div class='navbar-header'><button id='back'" +
    "type='button' class='btn btn-default navbar-btn center-block'>" + "Back" +
    "</button></div></div></nav>" + "<h2 id='playername' class='navbar-text" +
    " text-center'>" + name + "</h2>" + "<img id='playerimage'" +
    "class='img-rounded img-responsive center-block' src=" + image_link +
    " alt=" + name + ">" + "<h1 class='text-center'>Value: " + value + "</h1>");

  //Functionality for back button
  $("#back").click(function(e) {
    var searchNode = document.getElementById('container');
    while (searchNode.firstChild) {
      searchNode.removeChild(searchNode.firstChild);
    }
    //Animate the return to smaller container size
    $("#container").animate({width: "200px"}, 500);

    //Append the old HTML
    $("#container").append("<div id='search' class='form-group'>" +
    "<h3 id='header'>Transfer Val</h3><input id='searchbox'" +
    "class='form-control' aria-describedby='sizing-addon1'" +
    "placeholder='Type a player name...' type='text' name='searchbox'" +
    "value=''><input type='hidden' id='playerid'><p id='playerval'></p></div>");

    //Restore autocomplete functionality
    addAutoComplete();
  });

  //Player Info Panel
  $("#container").append("<div id='playerInfo' class='panel panel-info'>" +
  "<div id='panel-heading-info' class='panel-heading'>Player Info</div>" +
  "<div class='panel-body></div></div>");

  //Create the table, fill with apprpriate data
  $("#playerInfo").append("<table class='table table-bordered" +
  "table-condensed'><tbody><tr><th>" + "Team" + "</th><td>" + team +
  "</td></tr>" + "<tr><th>"+
  "Nationality" + "</th><td>" + nationality + "</td></tr>" + "<tr><th>" +
  "Position" + "</th><td>" + position + "</td></tr>" + "<tr><th>" +
  "Age" + "</th><td>" + age + "</td></tr></tbody></table>");

  var len = transfers.length; //number of transfer
  if (len>0) {
    //If they've been transferred, make the transfer table

    var table = document.createElement('table');
    table.className = "table-striped table table-bordered table-condensed";
    var table_head = document.createElement("thead");
    var th = document.createElement('tr');

    var th1 = document.createElement('th');
    var th2 = document.createElement('th');
    var th3 = document.createElement('th');
    var th4 = document.createElement('th');

    var t1 = document.createTextNode('Date');
    var t2 = document.createTextNode('Origin');
    var t3 = document.createTextNode('Destination');
    var t4 = document.createTextNode('Fee');

    th1.appendChild(t1);
    th2.appendChild(t2);
    th3.appendChild(t3);
    th4.appendChild(t4);

    th.appendChild(th1);
    th.appendChild(th2);
    th.appendChild(th3);
    th.appendChild(th4);

    table_head.appendChild(th);
    table.appendChild(table_head);
    tb = document.createElement("tbody");
    table.appendChild(tb);
    for (var i = 0; i<len; i++) {
      //Iterate over transfer array, append appropriate information to table

      var tr = document.createElement('tr');
      var td1 = document.createElement('td');
      var td2 = document.createElement('td');
      var td3 = document.createElement('td');
      var td4 = document.createElement('td');
      td4.id = "fee";

      var date = document.createTextNode(transfers[i][0]);
      var origin = document.createTextNode(transfers[i][1]);
      var destination = document.createTextNode(transfers[i][2]);
      var fee = document.createTextNode(valueDisplay(transfers[i][3]));

      td1.appendChild(date);
      td2.appendChild(origin);
      td3.appendChild(destination);
      td4.appendChild(fee);

      tr.appendChild(td1);
      tr.appendChild(td2);
      tr.appendChild(td3);
      tr.appendChild(td4);

      tb.appendChild(tr);
    }
    //Create the Transfer History Panel
    $("#container").append("<div id='history' class='panel panel-info'>" +
    "<div id='panel-heading' class='panel-heading'>Transfer History</div>" +
    "<div class='panel-body></div></div>");

    //Add the table to the panel
    $("#history").append(table);
  }
  else {
    //Player has never been transferred.

    $("#container").append("<div class='center-block'><h4 class='text-center'>"+
    "No transfers to show for " + name + "</h4></div>");
  }


}

//Make API call for a player
function makeRequest(url, name, team) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      //Parse response JSON, prepare to load player info

      var response = JSON.parse(xhr.responseText);
      loadPlayer(response, name, team);
    }
  };
  //Send request
  xhr.send();
}

//Clear the search, make request to player API
function changeToPlayerView(link, name, team) {
  //Clear contents of DOM
  var searchNode = document.getElementById('container');
  while (searchNode.firstChild) {
    searchNode.removeChild(searchNode.firstChild);
  }

  //Animate
  $("#container").animate({width: "400px"}, 500);

  //Create spinner
  $('#container').append("<div id='load'></div>");
  makeSpinner("load", 10);

  //Using the player's "link", make request to Player API to retrieve player
  //data and information
  var first = link.split("/", 2)[1];
  var second = link.split(first)[1];
  second = second.replace(/\//g, '|');
  var queryString = "/" + first + second;
  var q = getPlayerApiUrl();
  q+=queryString;
  makeRequest(q, name, team);
}

//Function to add autocomplete to the search box
function addAutoComplete() {
  $("#searchbox").autocomplete({
    appendTo: "#container", //where to place
    delay: 100, //delay to make ajax request
    minLength: 2, //min characters before request is made
    messages: {
      //This gets rid of default text saying no search results were found
      noResults: '',
      results: function() {}
    },
    //Make ajax request
    source: function(request, response) {
      var str = document.getElementById("searchbox").value;
      var newQuery = getSearchApiUrl();
      newQuery+=str;
      $.ajax({
        url: newQuery,
        type: "GET",
        dataType: "json",
        success: function (res) {
          //Create array using data from JSON
          var items = Object.keys(res.results).map(function(key) {
            return [key, res.results[key][2], res.results[key][3],
            res.results[key][1]];
          });

          //Sort the array by player's value, so top result is most valuable
          //player
          items.sort(function(first, second) {
            return second[1] - first[1];
          });

          response($.map(items, function (item) {
            //Associate data with callable indices
            return {
              label: item[0],
              value: valueDisplay(item[1]),
              link: item[2],
              team: item[3]
            };
          }));
        }
      });
    },

    select: function (event, ui) {
      //When a player is selected, append his name to the searchbox
      $("#searchbox").val(cleanPlayerName(ui.item.label));

      //Begin change to view player info
      changeToPlayerView(ui.item.link, ui.item.label, ui.item.team);
      return false;
    },

    response: function( event, ui ) {
      //When we get a response, remove the loading spinner
      var load = document.getElementById("load-results");
      load.parentNode.removeChild(load);
    },


    focus: function( event, ui ) {
      //Called when the user traverses the list of players
      $("#searchbox").val(cleanPlayerName(ui.item.label));
      var nodes = event.currentTarget.childNodes;
      for (var i = 0; i<nodes.length; i++) {
        $(nodes[i]).addClass("row-select");
        if (nodes[i].id != ui.item.link) {
          $(nodes[i]).removeClass("row-select");
        }
      }
      $("#playerid").html(cleanPlayerName(ui.item.label));
      return false;
    },

    search: function(event, ui) {
      //Display spinning wheel while searching
      $('#search').append("<div id='load-results'></div>");
      makeSpinner("load-results", 8);
    }
  })
  //Render the list results
  .autocomplete().data("uiAutocomplete")._renderItem = function(ul, item) {
    ul.addClass("the-list");
    var text = String(cleanPlayerName(item.label)).replace(
      new RegExp(this.term, "gi"),
      "<span class='ui-highlight'>$&</span>");
      return $("<li id = " + item.link + "></li>")
      .data("item.autocomplete", item)
      .append("<a>" + text + "<br>" + item.value + "</a>")
      .appendTo(ul);
    };

}

//Bind listener
document.addEventListener('DOMContentLoaded', function() {
  addAutoComplete();
});

//Code to get rid of fuzzy behavior when clicking outside the extension window
document.addEventListener("focus",function() {
    windowFocus = true;
})
document.addEventListener("blur",function() {
    windowFocus = false;
})
