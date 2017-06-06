%include('views/header.tpl')
<style type="text/css">
	h1.title{
		position: relative;
		left: 100px;
	}
	div.information{
		position: relative;
		left: 100px;
	}
</style>
<script type="text/javascript">
	function sub(a){
		if(a == free_user){
			var element = document.getElementById("sub");
			sub.innerHTML = ""
		}
	}
</script>

<h1 class="title">Account information</h1>
<p></p>
<p></p>
<div class = "information">
<font>User name: {{username}}</font>
<P></P>
<font>Full name: {{fullname}}</font>
<P></P>
<font>Subscription level: {{subscription}}      </font><a href="/subscribe" class = "sub">  Upgrade to Premium</a>
<script type="text/javascript">sub("{{subscription}}")</script>
</div>
%rebase('views/base', title='GAS - Annotate')
