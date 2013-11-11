$(function(){
  
  $.longpolling({
    pollURL: './lp.php',
    successFunction: pollSuccess,
    errorFunction: pollError
  });
  
});

function pollSuccess(data, textStatus, jqXHR){
  var json = eval('(' + data + ')');
  //$('body').html(json['data']);
  $('#tripped .value').html( json['data'] );
  /*show the red on wc*/
  console.log('data: ' +json['data']);
  if (parseInt(json['data'])==0) {
    //$("#wc").prop('disabled',true);
    $('#wc').css("background", "none");
    console.log('removing div');
  } else {
    //$("#wc").prop('disabled',false);
    $('#wc').css("background", "rgba(255, 0, 0, 0.7)");
    console.log('enable div');
  }
}

function pollError(jqXHR, textStatus, errorThrown){
  console.log('Long Polling Error: ' + textStatus);
}
