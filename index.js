
$( document ).ready(function(){

	$( '.time_date' ).html(new Date().toLocaleString());
	$( '.write_msg' ).keypress(function(e){
  	if(e.which == 13) {
    // enter pressed
    $( '.msg_send_btn' ).click()
  }
});
	var apigClient = apigClientFactory.newClient({
    apiKey: 'LEX4Wft4ZNaCF3yFeEb1caGD1Ha9o6ZxcrlqY8gf'
	});

	var params = {

	};

	var additionalParams = {
	    //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here

	};

	$( '.msg_send_btn' ).on('click', function(){
		var msg = $( ".write_msg" ).val();
		if(msg!=''){
			$( '.msg_history' ).append(
				'<div class="outgoing_msg"><div class="sent_msg"><p>' + msg + '</p><span class="time_date">' + new Date().toLocaleString() + '</span> </div></div>'  );	
			
			var body = {
			"messages": [
			{
				"type": "string",
				"unstructured": {
				"id": "0",
				"text": msg,
				"timestamp": "12/20/2018"
						}
					}
				]
			};

			apigClient.chatbotPost(params, body)
			    .then(function(result){
			    	console.log(result["data"]["body"]);
			    	$( '.msg_history' ).append( '<div class="incoming_msg">\
		              <div class="incoming_msg_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>\
		              <div class="received_msg">\
		                <div class="received_withd_msg">\
		                  <p>' + result["data"]["body"].slice(1,-1) + '</p>\
		                  <span class="time_date">' + new Date().toLocaleString() + '</span></div>\
		              </div></div>' );
			        //This is where you would put a success callback

			        $('.msg_history').scrollTop($('.msg_history')[0].scrollHeight);
			    }).catch( function(result){
			        //This is where you would put an error callback
			        console.log("error happens somewhere");
			        console.log(result);
			    });
			$( ".write_msg" ).val('')
			// var elem = document.querySelector('.msg_history');
  	// 		elem.scrollTop = elem.scrollHeight;
			

		}
	});






});
