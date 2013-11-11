<?php
try
{
    $m = new Mongo(); // connect
    $db = $m->selectDB("veradb");
    //db = $m->admin;
}
catch ( MongoConnectionException $e )
{
    echo '<p>Couldn\'t connect to mongodb, is the "mongo" process running?</p>';
    exit();
}
//$mongodb_info = $db->command(array('buildinfo'=>true));
//print_r($mongodb_info);

$collection = $db->sd;
$ch = $collection->find(array('type'=> '1'),array('value'=> 1, 'time'=> 1));
$ct = $collection->find(array('type'=> '0'),array('value'=> 1, 'time'=> 1));

function print_jsvalues($c) {
$first=true;
foreach($c as $d) {
if ($first == true){
  print '{ x: new Date('.($d['time']->sec*1000). '),y:'. $d['value'].'}' . PHP_EOL;
  $lasttime = $d['time']->sec;
  $lastvalue =$d['value'];
  $first = false;
} else {
  $less = true;
  while ($less) {
    if ( $d['time']->sec > $lasttime + 300 ) {
      print ',{ x: new Date('.(($lasttime + 300)*1000).'),y:'. $lastvalue.'}' . PHP_EOL;
      $lasttime = $lasttime+300;
    } else {
      print ',{ x: new Date('.($d['time']->sec*1000).'),y:'. $d['value'].'}' . PHP_EOL;
      $lasttime = $d['time']->sec;
      $lastvalue =$d['value'];
      $less=false;
    }
  }
}
}
}
?>

<html>
<head>
<style>
.image { 
   position: relative; 
   width: 100%; /* for IE 6 */
}

/*.image h2{ 
   position: absolute; 
   top: 200px; 
   left: 0; 
   width: 100%; 
}
*/
.image h2 span { 
   color: white; 
   font: bold 24px/45px Helvetica, Sans-Serif; 
   letter-spacing: -1px;  
   background: rgb(0, 0, 0); /* fallback color */
   background: rgba(0, 0, 0, 0.7);
   padding: 10px; 
}
.image h2 span.spacer {
   padding:0 5px;
}
.image #car h2 {
   position: absolute;
   left: 62px;
   top: 363px;
}
.image #br1 h2 {
   position: absolute;
   left: 116px;
   top: 123px;
}
.image #wc {
   position: absolute;
   left: 243px;
   top: 85px;
   width: 71px;
   height: 49px;
   background: rgba(255, 0, 0, 0.7);
}


</style>

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
<script src="js/jQuery.longpolling.js"></script>
<script src="js/application.js"></script>
<script>
function serverResponded( data ) {
/*
log the event data, so you can see what's going on.
Shows up in the console on your browser. (Chrome: Tools > Developer Tools > Console)
*/
console.log( data );
// check the server status, and report it on the screen
if ( data.server === true ) {
$('#status .value').html("OK");
}
else {
$('#status .value').html("NOT OK");
}
// add the last serial to the div on the screen
$('#serial .value').html( data.mostRecentSerial );
$('#history .value').html( data.serialHistory.replace(/\n/g, '<br />') );
}
$(document).ready( function() {
/* handle the click event on the get server status */
$('#getstatus').click( function() {
params = { op: "checkup" };
$.getJSON( 'http://10.10.11.126:8000/com' , params, serverResponded );
});
$('#getversion').click( function() {
params = { cmd: "0;0;33;Get Version\n" };
$.getJSON( 'http://10.10.11.126:8000/com' , params, serverResponded );
});
});

</script>>  
  <script type="text/javascript">
  window.onload = function () {
    var chart = new CanvasJS.Chart("chartContainer",
    {      
      title:{
        text: "Humidity and Temperature Sensor 10"
      },
      axisY :{
        includeZero: false
      },
      axisX : {
        valueFormatString: "MMM-DD" ,
        labelAngle: -50
      },
      toolTip: {
        shared: "true"
      },
      data: [
      {        
        type: "spline", 
        showInLegend: true,
        name: "Temperature",
        markerSize: 0,        
        dataPoints: [
<?php print_jsvalues($ct); ?>
        ]
      },      
      {        
        type: "spline", 
        showInLegend: true,
        name: "Humidity",
        markerSize: 0,        
        dataPoints: [
<?php print_jsvalues($ch); ?>
        ]
      }      
      ]
    });

chart.render();
}
/* fixing text over image */
$(function() {
    
    $("h2")
        .wrapInner("<span>")

    $("h2 br")
        .before("<span class='spacer'>")
        .after("<span class='spacer'>");

});

</script>
<script type="text/javascript" src="/js/canvasjs.min.js"></script>
</head>
<body>
  <div id="chartContainer" style="height: 300px; width: 800px;">
  </div>
<hr>
<div id="getstatus" style="cursor: pointer;">GET SERVER STATUS</div>
<div id="getversion" style="cursor: pointer;">GET VERAGATEWAY VERSION</div>
<br>
<div id="tripped">
<b>Tripped:</b> <span class="value">?</span>
</div>
<br>
<div id="status">
<b>Server Status:</b> <span class="value">?</span>
</div>
<div id="serial">
<b>Last Serial Input:</b> <span class="value"></span>
</div>
<div id="history">
<b>Last Serial History:</b> <br><span class="value"></span>
</div>
<hr>
<div class="image">
  <img src="fp.jpg">
<div id="car">
  <h2>42</h2>
</div>
<div id="br1">
  <h2>20</h2>
</div>
<div id="wc">
</div>


</div>
</body>
</html>



