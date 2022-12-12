$(function() {

	'use strict';

	// Form

	var createAppForm = function() {

		if ($('#contactForm').length > 0 ) {
			$( "#contactForm" ).validate( {
				rules: {
					name: "required",
					platform: {
						required: true,
					},
					platform_branch: {
						required: true,
					},
					platform_version: {
						required: true,
					},
					code: {
						required: true,
						minlength: 5
					}
				},
				messages: {
					name: "Please enter the application name",
					platform: "Please select a platform",
					platform_branch: "Please select platform branch",
					platform_version: "Please select platform version",
					code: "Please enter the code repo link"
				},
				/* submit via ajax */
				submitHandler: function(form) {		
					var $submit = $('.submitting'),
						waitText = 'Creating...';

					$.ajax({   	
				      type: "POST",
				      url: "{% url 'create_app' %}",
				      data: $(form).serialize(),

				      beforeSend: function() { 
				      	$submit.css('display', 'block').text(waitText);
				      },
				      success: function(msg) {
						  console.log(msg)
		               if (msg.success) {
		               	$('#form-message-warning').hide();
				            setTimeout(function(){
		               		$('#contactForm').fadeOut();
		               	}, 1000);
				            setTimeout(function(){
				               $('#form-message-success').fadeIn();   
		               	}, 1400);
			               
			            } else {
			               $('#form-message-warning').html(msg);
				            $('#form-message-warning').fadeIn();
				            $submit.css('display', 'none');
			            }
				      },
				      error: function() {
				      	$('#form-message-warning').html("Something went wrong. Please try again.");
				         $('#form-message-warning').fadeIn();
				         $submit.css('display', 'none');
				      }
			      });    		
		  		}
				
			} );
		}
	};
	createAppForm();

});