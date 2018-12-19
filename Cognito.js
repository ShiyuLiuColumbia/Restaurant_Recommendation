
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
            auth.signOut();
        } else {
            auth.getSession();
        }
    }

    // Operations when signed in.
  function showSignedIn(session) {

        $( '#sign_in_button' ).html("Sign Out");
    }

  // Initialize a cognito auth object.
function initCognitoSDK() {
    var authData = {
        ClientId : '41e4pc12o5emjo6bs44ermme1g', // Your client id here
        AppWebDomain : 'food-for-you.auth.us-east-1.amazoncognito.com',
        TokenScopesArray : ['profile', 'email', 'openid', 'aws.cognito.signin.user.admin', 'phone'], // e.g.['phone', 'email', 'profile','openid', 'aws.cognito.signin.user.admin'],
        RedirectUriSignIn : 'https://s3.amazonaws.com/restaurant-for-you/index.html',
        RedirectUriSignOut : 'https://s3.amazonaws.com/restaurant-for-you/index.html',
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

