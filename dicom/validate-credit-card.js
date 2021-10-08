/**
 * Validator for credit card numbers
 * Pattern: \b((4\d{12}(\d{3})?))|(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}|(3[47]\d{13})|(3(0[0-5]|[68]\d)\d{11})|(6(011|5\d{2})\d{12})|((2131|1800|35\d{3})\d{11})|(8\d{15})\b
 * 
 * @see https://developer.paypal.com/docs/classic/payflow/payflow-pro/payflow-pro-testing/#credit-card-numbers-for-testing for samples
 * @param {String} value The ID
 * @returns {Boolean}
 */

function validate(value) {

    //Clean Input of non-Alphanumeric characters
    var temp = sanitize(value);

    if (!isValidCheckDigit(temp)) {
        return false;
    }
    return true;
}

var sanitize = function (str) {

    var cleaned = str.toString().trim().split(/[^A-Za-z0-9]/).join("");
    return cleaned;
}

//Implementation of the Luhn Algorithm for check sums using mod10
var isValidCheckDigit = function (val) {

    var nCheck = 0
    var bEven = false;

    for (var n = val.length - 1; n >= 0; n--) {
        var cDigit = val.charAt(n);
        var nDigit = parseInt(cDigit, 10);

        if (bEven && (nDigit *= 2) > 9) {
            nDigit -= 9;
        }
        nCheck += nDigit;

        //Switches between the Even and Odd Flag every loop
        bEven = !bEven;
    }

    //Returns True if the check digit is valid
    return (nCheck % 10) == 0;
}