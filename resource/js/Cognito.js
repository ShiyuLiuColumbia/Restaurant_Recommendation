
$( document ).ready(function(){
    var auth = initCognitoSDK();
    $( "#sign_in_button" ).on('click', function(){
        userButton(auth);
    });
    var curUrl = window.location.href;
    auth.parseCognitoWebResponse(curUrl);

});


  // Perform user operations.
    function userButton(auth) {
        var state = $( '#sign_in_button' ).html();
        if (state === "Sign Out") {
            $( '#sign_in_button' ).html("Sign In");
            $( ' .navbar-text ' ).html('');
            auth.signOut();
        } else {
            auth.getSession();
        }
    }

    // Operations when signed in.
    function showSignedIn(session) {
        $( '#sign_in_button' ).html("Sign Out");
        if (session) {
            var accToken = session.getAccessToken().getJwtToken();
            if (accToken) {
                var payload = accToken.split('.')[1];
                var tokenobj = JSON.parse(atob(payload));
                var formatted = JSON.stringify(tokenobj, undefined, 2);
                $( ' .navbar-text ' ).html("Sign in as ,"+ tokenobj.username) 
            }

        }
    }


    // Initialize a cognito auth object.
    function initCognitoSDK() {
        var authData = {
            ClientId : '###', // Your client id here
            AppWebDomain : 'food-for-you.auth.us-east-1.amazoncognito.com',
            TokenScopesArray : ['profile', 'email', 'openid', 'aws.cognito.signin.user.admin', 'phone'], // e.g.['phone', 'email', 'profile','openid', 'aws.cognito.signin.user.admin'],
            RedirectUriSignIn : 'https://s3.amazonaws.com/restaurant-for-you/landing.html',
            RedirectUriSignOut : 'https://s3.amazonaws.com/restaurant-for-you/landing.html',
            IdentityProvider : 'Cognito User Pool', // e.g. 'Facebook',
            UserPoolId : 'us-east-1_iEAKWT4f3', // Your user pool id here
            AdvancedSecurityDataCollectionFlag : 'true', // e.g. true
            Storage: '' // OPTIONAL e.g. new CookieStorage(), to use the specified storage provided
        };
        var auth = new AmazonCognitoIdentity.CognitoAuth(authData);
        // You can also set state parameter 
        // auth.setState(<state parameter>);  
        auth.userhandler = {
        //  onSuccess: <TODO: your onSuccess callback here>,
        //  onFailure: <TODO: your onFailure callback here>
        //  * E.g.
            onSuccess: function(result) {
                // alert("Sign in success");
                showSignedIn(result);
            },
            onFailure: function(err) {
                alert("Error!" + err);
            }
        };
        // The default response_type is "token", uncomment the next line will make it be "code".
        // auth.useCodeGrantFlow();
        return auth;
    }

