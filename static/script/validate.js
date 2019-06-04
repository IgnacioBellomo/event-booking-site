// The submit button
const SUBMIT = $( "#submit" );

// Each of the fields and error message divs

const FNAME = $( "#fName" );
const FNAME_MSG = $( "#fName-msg" );
var validFName = false;

const LNAME = $( "#lName" );
const LNAME_MSG = $( "#lName-msg" );
var validLName = false;

const EMAIL = $( "#email" );
const EMAIL_MSG = $( "#email-msg" );
var validEmail = false;

const PASSWORD = $( "#password" );
const PASSWORD_MSG = $( "#password-msg" );
var validPassword = false;

const CONFIRM = $( "#confirmPassword" );
const CONFIRM_MSG = $( "#confirm-password-msg" );
var validConfirm = false;

/**
 * Validates the first name information in the register form so that
 * the server is not required to check this information.
 */
function validateFName ()
{
    if ( !FNAME.val() )
    {
        FNAME_MSG.html( "First name must have a value!" );
        FNAME_MSG.show();
        console.log( "Bad first name" );
        validFName = false;
    }
    else
    {
        FNAME_MSG.html("");
        FNAME_MSG.hide();
        validFName = true;
    }
    validateSubmission ();
}
FNAME.change ( validateFName );

/**
 * Validates the last name information in the register form so that
 * the server is not required to check this information.
 */
function validateLName ()
{
    if ( !LNAME.val() )
    {
        LNAME_MSG.html( "Last name must have a value!" );
        LNAME_MSG.show();
        console.log( "Bad last name" );
        validLName = false;
    }
    else
    {
        LNAME_MSG.html("");
        LNAME_MSG.hide();
        validLName = true;
    }
    validateSubmission ();
}
LNAME.change ( validateLName );


/**
 * Validates the email information in the register form so that
 * the server is not required to check this information.
 */
function validateEmail ()
{
    if ( !EMAIL.val() )
    {
        EMAIL.html( "Email must have a value!" );
        EMAIL.show();
        console.log( "No email" );
        validEmail = false;
    }
    else if
    ($.getJSON("/checkReg", { "email" : EMAIL.val() }),
        function (data)
        {
            if (data["exists"])
            {
                EMAIL_MSG.html( "Email is taken!");
                EMAIL_MSG.show();
                console.log("Email taken");
                validEmail = false;
            }
            else
            {
                EMAIL_MSG.html("");
                UEMAIL_MSG.hide();
                console.log("Good email");
                validUEmail = true;
            }
        });
    else
    {
        EMAIL.html("");
        EMAIL.hide();
        validEmail = true;
    }
    validateSubmission ();
}
EMAIL.change ( validateEmail );


/**
 * Validates the password information in the register form so that
 * the server is not required to check this information.
 */
function validatePassword ( )
{
{
    if ( !PASSWORD.val() )
    {
        PASSWORD_MSG.html( "Password must have a value!" );
        PASSWORD_MSG.show();
        console.log( "Bad password" );
        validPassword = false;
    }
    else
    {
        PASSWORD_MSG.html("");
        PASSWORD_MSG.hide();
        validPassword = true;
    }

    validateSubmission ();
}
PASSWORD.change ( validatePassword );
CONFIRM.change ( validatePassword );

/**
 * Checks to see if the given password is valid:
 * * must have at least 1 letter
 * * must have at least 1 number
 * * must have at least 1 special character
 */
function isValidPassword ( password )
{
    let hasLetter = false;
    let hasNumber = false;

    for ( let i = 0; i < password.length; i++ )
    {
        let letter = password.toLowerCase().charAt(i) ;
        if ( letter >= 'a' && letter <= 'z' )
        {
            hasLetter = true;
        }
        // number >= "0" && number <= "9"
        else if ( !isNaN( letter ) )
        {
            hasNumber = true;
        }
    }

    return hasLetter && hasNumber && hasSpecial;
}







/**
 * If the form has been validated, then this makes the submit
 * button visible. Otherwise hides it.
 */
function validateSubmission () {
    if ( validPassword && validConfirm &&
         validLName && validFName && validEmail )
    {
        SUBMIT.show();
    }
    else
    {
        SUBMIT.hide();
    }
}

/**
 * When the page loads, peform an initial validation of the
 * entered information in the form. Should result in lots
 * of invalid entries.
 */
$(document).ready ( function ()
{
    validateUsername();
    validatePassword();
    validateFName();
    validateLName();
    validateEmail();
    validateSubmission();
} );