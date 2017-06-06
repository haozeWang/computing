%include('views/header.tpl')
<head>
<style type="text/css">
	h1.title{
		position: relative;
		left: 100px
	}
	p.detail{
		position: relative;
		left: 100px
	}
	a.back{
		position: relative;
		left: 100px
	}
</style>
<script type="text/javascript">
	function rmtime(a){
		if(a=="0"){
			var element = document.getElementById("time");
			element.innerHTML = "";
		}
	}
	function rmview(a){
		if(a == "0"){
			var element = document.getElementById("view");
			element.innerHTML = "";
		}
	}
	function rmdown(a,b){
		var element = document.getElementById("down");
		if(b == "glacier"){
			element.innerHTML = 'upgrade to Premium for donwload'
			element.setAttribute('href', "/subscribe")
		}
		if(a == "0"){
			element.innerHTML = "";
		}

	}
</script>

</head>




<h1 class="title">Annotation Details</h1>
<p></p>
<p></p>
<p class = "detail">
	<b>Request ID:</b><font>"{{request_id}}"</font><br>
	<b>Request Time:</b><font>"{{request_time}}"</font><br>
	<b>VCF Input File:</b><font>"{{input_file}}"</font><br>
	<b>Status:</b><font>"{{status}}"</font><br>
	<b>Complete Time:</b><font id = "time">"{{compelte_time}}"</font><br>
	<script type="text/javascript">rmtime("{{compelte_time}}")</script>
	<b>Annotated Results File: </b><a id = "down" href="{{url}}">download</a><br>
	<b>Annotation Log File: </b><a id = "view" href="/annotations/{{job_id}}/log">view</a>
	<script type="text/javascript">rmdown("{{compelte_time}}","{{file_local}}")</script>
	<script type="text/javascript">rmview("{{compelte_time}}")</script>
</p>
<p></p>
<p></p>

<a class = "back" href="/annotations">&#8592 back to annotations list</a>
%rebase('views/base', title='GAS - Annotate')
