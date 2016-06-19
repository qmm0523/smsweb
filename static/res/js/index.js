$(document).ready(function() {
	hacksms.getUSB();
});

var hacksms = {
	getUSB:function(){
		$.post('/getUSB', {}, function(data, textStatus, xhr) {
			$('#devCount').text(data.total);
			$('#devList').empty();
			for(var dev = 0;dev < data.total;dev++){
				$('#devList').append('<li><button class="btn btn-success">'+ data.rows[dev] +'</button></li>');
			}

			if(data.total < 2){
				$('#devList').html('<li><font color=red>未发现可用设备</font></li>');
			}
		},"json");
	},
	killdev:function(){
		$.post('/killdev', {}, function(data, textStatus, xhr) {
			if(data.res == 0){
				alert('操作成功!');
			}else{
				alert('发生异常:'+data.msg);
			}
		},"json");
	},
	download:function(){
		$.post('/download', {}, function(data, textStatus, xhr) {
			if(data.res == 0){
				alert('操作成功!');
			}else{
				alert('发生异常:'+data.msg);
			}
		},"json");
	},
	readARFCN:function(){
		$.post('/readARFCN', {}, function(data, textStatus, xhr) {
			if(data.res == 0){
				$('#arfcnList').find('tbody').empty();
				for(var arfcn = 0;arfcn < data.rows.length;arfcn++){
					$('#arfcnList').find('tbody').append(
						'<tr>'+
                            '<td>'+ arfcn +'</td>'+
                            '<td>'+ data.rows[arfcn] +'</td>'+
                            '<td>'+ data.date +'</td>'+
                            '<td><button class="btn btn-primary" onclick="hacksms.sniff('+ data.rows[arfcn].split(' ')[0].split('=')[1] +')">嗅探</button></td>'+
                        '</tr>'
					);
				}
			}else{
				alert('发生异常:'+data.msg);
			}
		},"json");
	},
	scanARFCN:function(type){
		$.post(type == 1?'/getARFCN':'/smartARFCN', {}, function(data, textStatus, xhr) {
			if(data.res == 0){
				alert(JSON.stringify(data));
			}else{
				alert('发生异常:'+data.msg);
			}
		},"json");
	},
	sniff:function(arfcn){
		$.post('/doSniffer', {"arfcnId":arfcn}, function(data, textStatus, xhr) {
			if(data.res == 0){
				alert('操作成功! PID: '+data.pid);
			}else{
				alert('发生异常:'+data.msg);
			}
		},"json");
	}
}