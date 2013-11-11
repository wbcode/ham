;(function($){
  
  $.longpolling = function(options){
    
    var settings = $.extend({}, $.longpolling.defaults, options);
    
    var Poll = {
      
      longpolling: function(){
        
        var pollURL = settings.pollURL + '?' + settings.timestampURLVar + '=' + settings.timestamp;
        
        $.ajax({
          type: 'GET',
          url: pollURL,
          async: true,
          cache: false,
          success: function(data, textStatus, jqXHR){

            try {
                json = $.parseJSON(data);
            } catch (e) {
                setTimeout(Poll.longpolling(), settings.pollErrorTime);
                return false;
            }

            var json = eval('(' + data + ')');

            settings.timestamp = json['timestamp'];
            if(settings.successFunction != null) settings.successFunction(data, textStatus, jqXHR);
            setTimeout(Poll.longpolling(), settings.pollTime);
          },
          error: function(jqXHR, textStatus, errorThrown){
            if(settings.errorFunction != null) settings.errorFunction(jqXHR, textStatus, errorThrown);
            setTimeout(Poll.longpolling(), settings.pollErrorTime);
          }
        });
        
      }
      
    };
    
    Poll.longpolling();
    
  }
  
  $.longpolling.defaults = {
    pollURL: '',
    pollTime: 1000,
    pollErrorTime: 5000,
    successFunction: null,
    errorFunction: null,
    timestamp: null,
    timestampURLVar: 'timestamp'
  }
  
})(jQuery);
