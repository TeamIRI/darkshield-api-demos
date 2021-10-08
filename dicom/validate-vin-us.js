/**
 * Validation for Vehicle Identification number (VIN)
 * Pattern: \b([A-HJ-NPR-Z\d]{3})([A-HJ-NPR-Z\d]{5})([\dX])(([A-HJ-NPR-Z\d])([A-HJ-NPR-Z\d])([A-HJ-NPR-Z\d]{6}))\b
 * Examples:
 * - Valid: JHMAP21239S043176, 1HD1EGL34PY174717, JHBFF1954L2T35291
 * - Invalid: JHMAP212S043176e , jhmAP21239S043176
 *
 * @see https://en.wikipedia.org/wiki/Vehicle_identification_number
 * @param {String} value of the VIN
 * @returns {Boolean}
 */

function validate(value) {

  //Clean Input of non-Alphanumeric characters
  var temp = sanitize(value);

  //return false if the length is not 17
  if (temp.length != 17) {
    return false;
  }

  return isValidCheckDigit(temp);
}

var sanitize = function (str) {

  var cleaned = str.trim().split(/[^A-Za-z0-9]/).join("").toUpperCase();
  return cleaned;
}

var isValidCheckDigit = function (str) {

  return (calculateCheckDigit(str) === charAsInt(str[8]));
}



/*
    Implementation of the Luhn Algorithm for check sums using mod11 
    Modified for alphanumeric characters
*/

var calculateCheckDigit = function (str) {

  var sum = 0;
  var multiplier;
  var checkDigit;
  var weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2];
  var transliterations = {
    A: 1,
    B: 2,
    C: 3,
    D: 4,
    E: 5,
    F: 6,
    G: 7,
    H: 8,
    J: 1,
    K: 2,
    L: 3,
    M: 4,
    N: 5,
    P: 7,
    R: 9,
    S: 2,
    T: 3,
    U: 4,
    V: 5,
    W: 6,
    X: 7,
    Y: 8,
    Z: 9
  };

  for (var i = 0; i < str.length; i++) {
    if (isNumericCharacter(str[i])) {
      multiplier = charAsInt(str[i]);
    } else {
      multiplier = transliterations[str[i]]
    }

    sum += multiplier * weights[i];
  }

  checkDigit = sum % 11;

  return checkDigit === 10 ? "X" : checkDigit;
}

var isNumericCharacter = function (character) {

  return !isNaN(charAsInt(character));
}

var charAsInt = function (character) {

  return parseInt(character, 10);
}