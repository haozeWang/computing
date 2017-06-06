<!--
subscribe.tpl - Get user's credit card details to send to Stripe service
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->


%include('views/header.tpl')
<!-- Captures the user's credit card information and uses Javascript to send to Stripe -->

<div class="container">
        <div class="page-header">
                <h2>Subscribe</h2>
        </div>

        <p>You are subscribing to the GAS Premium plan. Please enter your credit card details to complete your subscription.</p><br />

	    <div class="form-wrapper">

		    <form role="form" action="{{get_url('subscribe')}}" method="post" id="subscribe_form" name="subscribe_submit">

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="name">Card hodler's Name</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="name" placeholder="Enter your full Name" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="number">Card Number</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="number"
		                   placeholder="Enter your card number" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-4">
			            <label for="cvc">Verification Code</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="cvc" 
		                   placeholder="Enter verification code" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-4">
			            <label for="exp-month">Expiration month</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="exp-month" placeholder="Enter Expiration month" />
		            </div>
		        </div>		     

		        <div class="row">
			        <div class="form-group col-md-4">
			            <label for="exp-year">Expiration year</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="exp-year"  placeholder="Enter Expiration year" />
		            </div>
		        </div>	   		        

		        <br />
		        <div class="form-actions">
		            <input id="bill-me" class="btn btn-lg btn-primary" type="submit" value="Subscribe" />
		        </div>        
		    </form>
	    </div>
		%end

</div> <!-- container -->

%rebase('views/base', title='GAS - Register')
