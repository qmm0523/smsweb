$(document).ready(function() {
	hacksms.getUSB();
});

var hacksms = {
	getUSB:function(){
		$.post('/getUSB', {}, function(data, textStatus, xhr) {
			$('#devCount').text(data.total);
			$('#devList').empty();
			for(var dev = 0;dev < data.total;dev++){
				$('#devList').append('<li><button class="btn btn-success">ttyUSB0</button></li>');
			}

			if(data.total < 1){
				$('#devList').html('<li><font color=red>未发现可用设备</font></li>');
			}
		},"json");
	}
}