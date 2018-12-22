
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
    var params_user = {
        user_name : $( ".navbar-text" ).html().slice(12)
        // user_name : 'Yi zhi zhu'
    };

   // history get start
    apigClient.historyGet(params_user).then(function(result){
        console.log(result);
        result.data.body.forEach(function(history, i){
            console.log(history.url);
            $(' .show_hostory ').append('<div style="width:30%;" class="card" id="review'+ i + '">\
                                            <img style="width:30%;"  class="card-img-top" src="'+ history.img +'" alt="Card image cap">\
                                            <div class="card-body ">\
                                                <h5 class="card-title">Restrant Name: ' + history.restaurant_name + '</h5>\
                                                <p class="card-text">Adress: ' + history.location + '</p>\
                                                <p class="card-text dining_time">Dinging Time: ' + history.dining_date +' '+ history.dining_time+ '</p>\
                                            </div>\
                                        </div>') ;
            if(history.comment == undefined){
                $( ' #review' + i ).append('\
                       <div>\
                            <button class="btn btn-primary " type="button" data-toggle="collapse" data-target="#collapseExample'+ i + '"\
                            aria-expanded="false" aria-controls="collapseExample">\
                                Write Review\
                            </button>\
                        </div>\
                        <div class="collapse" id="collapseExample'+ i + '">\
                            <form class="commentAndStar" action="#">\
                                <select class="form-control selector" id="exampleFormControlSelect1">\
                                    <option>1</option>\
                                    <option>2</option>\
                                    <option>3</option>\
                                    <option>4</option>\
                                    <option>5</option>\
                                </select>\
                                <label for="comment">Comment:</label>\
                                <textarea class="form-control comment_content" rows="5" id="comment"></textarea>\
                                <button class="btn btn-primary write_comment">submit</button>\
                            </form>\
                        </div>\
                ');
            }
            else{
               $( ' #review' + i ).children(".card-body").append('\
                <p class="card-text">Score:' + history.score + '</p>\
                <p class="card-text">Comment:' + history.comment + '</p>\
               '); 
            }

        });

        // post review and score to database
        $( ".write_comment" ).on('click', function(){
            var comment = {
                user_name: $( ".navbar-text" ).html().slice(12),
                restaurant_name: $( this ).parent().parent().parent().children(".card-body").children(".card-title").html().slice(15),
                dining_time: $( this ).parent().parent().parent().children(".card-body").children(".dining_time").html().slice(14),
                score: $( this ).parent().children(".selector").val(),
                review: $( this ).parent().children(".comment_content").val()

            };
            console.log(comment);

            var comment_body = {
                "comment_info" : comment
            };
            apigClient.commentsPost(params, comment_body).then(function(result){
                console.log(result);
            }).catch( function(error){
            //This is where you would put an error callback
            console.log("error happens somewhere");
            console.log(error);
            });
            
        });

    }).catch( function(error){
        //This is where you would put an error callback
        console.log("error happens somewhere");
        console.log(error);
    });
    // history get end


    // recommendation start
    var directionsService = new google.maps.DirectionsService();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    }

    function showPosition(position) {
        var geocoder = new google.maps.Geocoder;
        latlng = {lat: position.coords.latitude, lng: position.coords.longitude};
        geocoder.geocode({'location': latlng}, function(results, status) {
            if(status === 'OK') {
                var address = results[0].formatted_address;
                console.log(results[0].formatted_address);


                        // recommedation
                apigClient.recommendationGet(params_user).then(function(result){
                    console.log(result);
                    //distance judgemment
                    restaurants = result.data.body;
                    console.log(address);
                    restaurants.forEach((restaurant)=>{
                        directionsService.route({
                            // origin : '116th St & Broadway, New York',
                            origin: address,
                            destination : restaurant.address + ', New York',
                            travelMode : google.maps.DirectionsTravelMode.DRIVING
                        }, function(response, status) {
                            if ( status == google.maps.DirectionsStatus.OK ) {
                                if(response.routes[0].legs[0].distance.value > 20000) {
                                    console.log(restaurant.business_name + "   Too far!!")
                                } 
                                else {
                                    console.log(restaurant.business_name + "distance is : " + response.routes[0].legs[0].distance.value ); // the distance in metres
                                    $( '#recommendation' ).append('<div class="card col-sm-4" style="width: 18rem;">\
                                                                        <a class = "link" href="'+ restaurant.url +'">\
                                                                            <img class="card-img-top" src="'+ restaurant.img +'" alt="Card image cap">\
                                                                        </a>\
                                                                        <div class="card-body ">\
                                                                            <h5 class="card-title">' + restaurant.business_name + '</h5>\
                                                                            <p class="card-text">' + restaurant.address + '</p>\
                                                                            <a href="#" class="order btn btn-primary">Order it!</a>\
                                                                        </div>\
                                                                    </div>'
                                    );


                                    $( ".order" ).removeClass("order_visibility");//re-show order button
                                    $( ".order" ).on('click', function(){
                                        var bodyMes = {"business_name": $(this).parent().children(" .card-title ").html(),
                                                        "address": $(this).parent().children(" .card-text ").html(),
                                                        "url": $(this).parent().parent().children(" .link").attr("href"),
                                                        "user_name": $( ".navbar-text" ).html().slice(12),
                                                        "img": $(this).parent().parent().children(" .link").children(" .card-img-top").attr("src")
                                        };
                                        console.log(bodyMes);

                                        apigClient.orderPost(params, bodyMes).then(function(result){
                                            $( ".order" ).toggleClass("order_visibility");//invisiable button
                                            console.log(result)
                                            
                                        }).catch( function(result){
                                            //This is where you would put an error callback
                                            console.log("error happens somewhere");
                                            console.log(result);
                                        });
                                    
                                    });



                                }
                            }    
                        })
                    })
                }).catch( function(error){
                    console.log("error happens somewhere");
                    console.log(error);
                });
                // recommendation end


            }else{
                console.log('error');
            }
        });
    }


    var chose_restaurant;
    $( '.msg_send_btn' ).on('click', function(){
        var msg = $( ".write_msg" ).val();
        if(msg!=''){
            $( '.msg_history' ).append(
                '<div class="outgoing_msg"><div class="sent_msg"><p>' + msg + '</p><span class="time_date">' + new Date().toLocaleString() + '</span> </div></div>'
            ); 
            
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

            apigClient.chatbotPost(params, body).then(function(result){
                console.log(result)
                $( '.msg_history' ).append( '<div class="incoming_msg">\
                  <div class="incoming_msg_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>\
                  <div class="received_msg">\
                    <div class="received_withd_msg">\
                      <p>' + result["data"]["body"] + '</p>\
                      <span class="time_date">' + new Date().toLocaleString() + '</span></div>\
                  </div></div>' );
                //This is where you would put a success callback

                $('.msg_history').scrollTop($('.msg_history')[0].scrollHeight);

                // restaurant_list is a list sent by lex, it is an array in JS.
                console.log(typeof(result["data"]["fullfilled"]))
                if(result["data"]["fullfilled"]==true){

                    var restaurant_list= result["data"]["restaurant_list"];
                    console.log(typeof(restaurant_list))
                    
                    var myplace,infowindow,marker;
                    var myLatlng=new google.maps.LatLng(30, 120);
                    var mapOptions = {
                      center: myLatlng,
                      zoom: 13,
                      mapTypeId: google.maps.MapTypeId.ROADMAP
                    };
                    var map = new google.maps.Map(document.getElementById("map_canvas"),mapOptions);         
                    var geocoder = new google.maps.Geocoder();


                    restaurant_list.forEach(function(restaurant){
                        console.log(restaurant)
                        $( '#restaurant_show' ).append('<div class="card col-sm-4" style="width: 18rem;">\
                                                            <a class = "link" href="'+ restaurant.url +'">\
                                                                <img class="card-img-top" src="'+ restaurant.img +'" alt="Card image cap">\
                                                            </a>\
                                                            <div class="card-body ">\
                                                                <h5 class="card-title">' + restaurant.business_name + '</h5>\
                                                                <p class="card-text">' + restaurant.address + '</p>\
                                                                <a href="#" class="order btn btn-primary">Order it!</a>\
                                                            </div>\
                                                        </div>'
                        );



                            // start of google map
                        geocoder.geocode( { 'address': restaurant.address}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            map.setCenter(results[0].geometry.location);
                            marker = new google.maps.Marker({
                                map: map,
                                position: results[0].geometry.location,
                            });
                            results[0].name = restaurant.business_name;
                            google.maps.event.addListener(marker, 'click', function() {
                              infowindow.setContent('<div><strong>' + results[0].name + '</strong><br><br>' +
                                results[0].formatted_address + '</div>');
                              infowindow.open(map, this);
                            });
                            infowindow = new google.maps.InfoWindow({
                                content: results[0].geometry.location.lat()+' , '+results[0].geometry.location.lng(),
                                maxWidth: 200
                            });
                        } else {
                            alert('Geocode was not successful for the following reason: ' + status);
                        }
                        })
                            // end of google map
                    });

                    $(" .link ").on('click',function(event){
                        event.preventDefault();
                        window.open($(this).attr("href"));
                    });


                    // start order

                    $( ".order" ).removeClass("order_visibility");//re-show order button
                    $( ".order" ).on('click', function(){
                        var bodyMes = {"business_name": $(this).parent().children(" .card-title ").html(),
                                        "address": $(this).parent().children(" .card-text ").html(),
                                        "url": $(this).parent().parent().children(" .link").attr("href"),
                                        "user_name": $( ".navbar-text" ).html().slice(12),
                                        "img": $(this).parent().parent().children(" .link").children(" .card-img-top").attr("src")
                        };
                        console.log(bodyMes);

                        apigClient.orderPost(params, bodyMes).then(function(result){
                            $( ".order" ).toggleClass("order_visibility");//invisiable button
                            console.log(result)
                            
                        }).catch( function(result){
                            //This is where you would put an error callback
                            console.log("error happens somewhere");
                            console.log(result);
                        });
                        
                    });
                    // end of order
                };
            }).catch( function(result){
                //This is where you would put an error callback
                console.log("error happens somewhere");
                console.log(result);
            });

            $( ".write_msg" ).val('')
        }
    });//end of: $( '.msg_send_btn' ).on('click', function()
});
