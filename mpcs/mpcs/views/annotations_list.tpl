%include('views/header.tpl')
<head>
<style type="text/css">
h1.title
{
	position: relative;
	left: 100px
}	
</style>
<style type="text/css">
span.lead
{
	position: relative;
	left: 10px
}
a.btn{
	position: relative;
	left: 100px
}	
a.btn-large{
	position: relative;
	left: 100px
}
a.bth-default{
	position: relative;
	left: 100px
}
table.tb{
	position: relative;
	left: 100px
}
</style>
<script type="text/javascript">
	function insrow(a, b){
		var items = JSON.parse(a.replace(/&quot;/g,'"'));
		for (var i = 0; i < b; i++) {
			var table = document.getElementById("tb");
			var row = table.insertRow(-1);
			var cell1 = row.insertCell(0);
			var cell2 = row.insertCell(1);
			var cell3 = row.insertCell(2);
			var cell4 = row.insertCell(3);
			cell1.href = "/annotations/"+ items[i].job_id;
			cell1.style.width = 700;
			cell1.innerHTML = '<a href="/annotations/'+ items[i].job_id+'">'+items[i].job_id+'</a>'
			cell2.style.width = 200;
			cell2.innerHTML = items[i].submit_time;
			cell3.style.width = 200;
			cell3.innerHTML = items[i].input_file_name;
			cell4.style.width = 200;
			cell4.innerHTML = items[i].job_status;
			
			
		}
	}
</script>
</head>
<h1 class = "title">My Annotations</h1>
<p></p>
<a class="btn btn-large btn-default" href="/annotate"><span class="lead"><strong>Request New Annotation</strong></span></a>
<p></p>
<table class = "tb" id = "tb">
<th width="500" align="left">Request ID</th>
<th width="200">Request Time</th>
<th width="200">VCF File Name</th>
<th width="200">Status</th>
<script type="text/javascript">insrow("{{items}}","{{num}}");</script>
	
</table>

%rebase('views/base', title='GAS - Login')
