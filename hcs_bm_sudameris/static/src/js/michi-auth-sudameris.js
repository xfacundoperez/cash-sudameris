var deviceId;
var userAccessToken;
var operatorAccessToken;
var userType = "";
var userPassword = "";

// XMLHttpRequest Object
const requestXHR = new XMLHttpRequest();

// definicion de constantes
const clientSecret = "mi-secreto";
const clientType = "SALARIOS-ALT";
const clientVersion = "1.0.0";
const authVersion = "1.0.0";
const XRshkMichiApiKey =
  "c709c1b4fcfaeca543bf@8a86c850-0f32-40a7-9b7f-3dced6fb2459@da1a416a9b050c04f7c0";
const callbackErrorMsg = 'Ocurrió un error inesperado. Favor contactar con nuestro Call Center llamando al teléfono <a href="tel:+595214166000">416-6000</a> o escribanos al correo <a href="mailto:sac@sudameris.com.py">sac@sudameris.com.py</a>.'

// definiciones para controlar las cookies
const deviceIdCookieName = "X-RshkMichi-deviceId";
const accessTokenCookieName = "X-RshkMichi-AccessToken";
const cookieLifetime = 365; // en días

// funciones para controlar la habilitación del botón
function enableLoginButton() {
  const loginButton = document.getElementById("btn-login");
  loginButton.disabled = false;
}

function disableLoginButton() {
  const loginButton = document.getElementById("btn-login");
  loginButton.disabled = true;
}

function modalCover(show) {
  if (show)
    document.getElementById("cover-spin").classList.remove("cover-hide");
  else document.getElementById("cover-spin").classList.add("cover-hide");
}

// funcion utilidad mensaje de error
function errorMessage(message) {
  document.getElementById("api-alert").innerHTML = message;
  document.getElementById("api-alert").style.display = "";
  if (message === null)
    document.getElementById("api-alert").style.display = "none";
}

// funciones de utilidad de cookies
// fuente: https://stackoverflow.com/a/24103596
function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1, c.length);
    }
    if (c.indexOf(nameEQ) == 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
}

function eraseCookie(name) {
  document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
}

// request a la api de Odoo (bm_write_session_data)
function odooWriteSession(user_id, user_password, callback) {
  const body = {
    jsonrpc: 2.0,
    params: {
      user_id: user_id,
      user_password: user_password,
      ApiKey: XRshkMichiApiKey,
      AccessToken: operatorAccessToken,
    },
  };
  var odoo_url = window.location.origin + "/bm_write_session_data";
  var callback_args = {
    error: null,
  };

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");

  requestXHR.onload = function (e) {
    var jsonData = JSON.parse(this.response);
    if (callback_args.error) console.error(callback_args);
    console.log(["Response", { odooWriteSession: jsonData }]);
    callback(callback_args);
  };
  requestXHR.onerror = function (e) {
    callback_args.status = requestXHR.statusText;
    callback_args.error =
      'Error de respuesta (requestXHR.statusText = "' +
      requestXHR.statusText +
      '")';
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { odooWriteSession: body }]);
  requestXHR.send(JSON.stringify(body));
}

function odooGetUser(userValue, callback) {
  const body = {
    jsonrpc: 2.0,
    params: {
      login: userValue,
    },
  };
  var odoo_url = window.location.origin + "/bm_get_user_info";

  var callback_args = {
    status: null,
    user: null,
  };

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");

  requestXHR.onload = function (e) {
    var jsonData = JSON.parse(this.response).result;
    callback_args.status = jsonData.status;
    callback_args.user = jsonData.response;

    console.log(["Response", { odooGetUser: jsonData }]);
    callback(callback_args);
  };

  requestXHR.onerror = function (e) {
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { odooGetUser: body }]);
  requestXHR.send(JSON.stringify(body));
}

function odooCheckUser(loginUser, odooUser, callback) {
  const body = {
    jsonrpc: 2.0,
    params: {
      loginUser: loginUser,
      odooUser: odooUser,
    },
  };
  var odoo_url = window.location.origin + "/bm_check_user_login";

  var callback_args = {
    status: null,
    id: null,
    error: null,
  };

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");

  requestXHR.onload = function (e) {
    var jsonData = JSON.parse(this.response).result;
    callback_args.status = jsonData.success;
    callback_args.id = jsonData.id;
    callback_args.password = jsonData.password;
    if (callback_args.error) console.error(callback_args);
    console.log(["Response", { odooCheckUser: jsonData }]);
    callback(callback_args);
  };
  requestXHR.onerror = function (e) {
    callback_args.status = requestXHR.statusText;
    callback_args.error =
      'Error de respuesta (requestXHR.statusText = "' +
      requestXHR.statusText +
      '")';
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { odooCheckUser: body }]);
  requestXHR.send(JSON.stringify(body));
}

// request a la api de deviceId (add-device)
function michiAuthRequestDeviceId(callback) {
  // definición del cuerpo del request
  const requestedDeviceId = uuid.v4();
  const tstamp = new Date().toISOString();
  var hash = CryptoJS.SHA256(
    requestedDeviceId + "##" + tstamp + "##" + clientSecret
  );
  var ssign = CryptoJS.enc.Base64.stringify(hash);
  var body = {
    jsonrpc: 2.0,
    params: {
      clientType: clientType,
      clientVersion: clientVersion,
      ssign: ssign,
      tstamp: tstamp,
      userAgent: navigator.userAgent,
      deviceId: requestedDeviceId,
    },
  };

  var odoo_url = window.location.origin + "/michi_auth_request_device_id";

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");
  requestXHR.setRequestHeader("X-RshkMichi-ApiKey", XRshkMichiApiKey);

  var callback_args = {
    error: null,
  };

  requestXHR.onload = function (e) {
    jsonData = JSON.parse(this.response).result.response;
    if (jsonData) {
      if (jsonData.message === undefined) {
        deviceId = jsonData.deviceId;
        // Guardo la cookie: deviceId
        setCookie(deviceIdCookieName, deviceId, cookieLifetime);
        console.log(["Response", { "add-device": jsonData }]);
      } else {
        callback_args.error = jsonData.message + " (" + jsonData.code + ")";
      }
    } else {
      callback_args.error = callbackErrorMsg;
    }
    if (callback_args.error) console.error(callback_args);
    callback(callback_args);
  };

  requestXHR.onerror = function (e) {
    callback_args.error =
      'Error de respuesta (requestXHR.statusText = "' +
      requestXHR.statusText +
      '")';
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { "add-device": body }]);
  requestXHR.send(JSON.stringify(body));
}

// request a la api de login (Login de Operador)
function michiAuthOperatorLogin(operator, callback) {
  var body = {
    jsonrpc: 2.0,
    params: {
      operator: operator.externalId,
    },
  };
  var odoo_url = window.location.origin + "/michi_auth_operator_login";

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");
  requestXHR.setRequestHeader("X-RshkMichi-ApiKey", XRshkMichiApiKey);
  requestXHR.setRequestHeader("X-RshkMichi-AccessToken", userAccessToken);

  var callback_args = {
    userInfo: null,
    error: null,
  };

  requestXHR.onload = function (e) {
    jsonData = JSON.parse(this.response).result.response;
    if (jsonData) {
      if (jsonData.message === undefined) {
        // Si la sesión es VALID y obtengo userAccessToken
        if (jsonData.session.status == "VALID" && jsonData.accessToken != "") {
          // Guardo el access token de operador
          operatorAccessToken = jsonData.accessToken;
          callback_args.userInfo = jsonData.session.userInfo;
          console.log(["Response", { "Login Operador": jsonData }]);
        } else {
          callback_args.error =
            'La sesión no es valida o no se obtuvo el access token (jsonData.session.status = "' +
            jsonData.session.status +
            '", operatorAccessToken = "' +
            operatorAccessToken +
            '")';
        }
      } else {
        callback_args.error = jsonData.message + " (" + jsonData.code + ")";
      }
    } else {
      callback_args.error = callbackErrorMsg;
    }
    if (callback_args.error) console.error(callback_args);
    callback(callback_args);
  };

  requestXHR.onerror = function (e) {
    callback_args.status = requestXHR.statusText;
    callback_args.error =
      'Error de respuesta (requestXHR.statusText = "' +
      requestXHR.statusText +
      '")';
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { "Login Operador": body }]);
  requestXHR.send(JSON.stringify(body));
}

// request a la api de login (Login de Usuario)
function michiAuthUserLogin(userValue, password, callback) {
  // definición del payload
  const authType = "SALARIOS_AUTH";
  const tstamp = new Date().toISOString();
  var hash = CryptoJS.SHA256(
    deviceId +
      "##" +
      userType +
      "##" +
      userValue +
      "##" +
      password +
      "##" +
      clientSecret
  );
  var ssign = CryptoJS.enc.Base64.stringify(hash);
  var body = {
    jsonrpc: 2.0,
    params: {
      authType: authType,
      authVersion: authVersion,
      clientType: clientType,
      clientVersion: clientVersion,
      deviceId: deviceId,
      ssign: ssign,
      tstamp: tstamp,
      userType: userType,
      userValue: userValue,
      password: password,
      userAgent: navigator.userAgent,
    },
  };
  var odoo_url = window.location.origin + "/michi_auth_user_login";

  requestXHR.open("POST", odoo_url, true);
  requestXHR.setRequestHeader("Content-Type", "application/json");
  requestXHR.setRequestHeader("X-RshkMichi-ApiKey", XRshkMichiApiKey);

  var callback_args = {
    status: null,
    operator: null,
    error: null,
  };

  requestXHR.onload = function (e) {
    jsonData = JSON.parse(this.response).result.response;
    if (jsonData) {
      if (jsonData.message === undefined) {
        // Si la sesión es VALID y obtengo userAccessToken
        if (jsonData.session.status == "VALID" && jsonData.accessToken != "") {
          userAccessToken = jsonData.accessToken;
          // Guardo la cookie
          setCookie(accessTokenCookieName, userAccessToken, cookieLifetime);

          UserOperators =
            jsonData.session.userInfo.additionalInfo.UserOperators;
          // Si trae datos dentro de UserOperators
          console.log({ UserOperators });
          if (Object.keys(UserOperators).length > 0) {
            if (
              jsonData.session.userInfo.additionalInfo.UserOperators[0]
                .externalId != null
            ) {
              callback_args.operator =
                jsonData.session.userInfo.additionalInfo.UserOperators[0]; // Obtengo solo el operador en la posición 0
            }
          } else {
            callback_args.error =
              "No se obtuvo ningún operador para el usuario";
          }
          console.log(["Response", { "Login Usuario": jsonData }]);
        } else {
          callback_args.error =
            'La sesión no es valida o no se obtuvo el access token (jsonData.session.status = "' +
            jsonData.session.status +
            '", userAccessToken = "' +
            userAccessToken +
            '")';
        }
      } else {
        callback_args.error = jsonData.message + " (" + jsonData.code + ")";
      }
    } else {
      callback_args.error = callbackErrorMsg;
    }
    if (callback_args.error) console.error(callback_args);
    callback(callback_args);
  };

  requestXHR.onerror = function (e) {
    callback_args.status = requestXHR.statusText;
    callback_args.error =
      'Error de respuesta (requestXHR.statusText = "' +
      requestXHR.statusText +
      '")';
    console.error(callback_args);
    callback(callback_args);
  };

  // ejecución del request
  console.log(["Request", { "Login Usuario": body }]);
  requestXHR.send(JSON.stringify(body));
}

// setup al cargarse la página
window.onload = function () {
  // Si se cerró sesión, limpio la cookie de sesión
  if (window.location.href.indexOf("clean") >= 0)
    eraseCookie(accessTokenCookieName);

  // tomo el deviceId si está guardado, o lo pido, y luego habilito el login
  deviceId = getCookie(deviceIdCookieName);
  if (!deviceId)
    michiAuthRequestDeviceId((result) => {
      // Muestro el login
      document
        .getElementsByClassName("container py-5")[0]
        .classList.add("container-show");
      if (!deviceId)
        errorMessage(callbackErrorMsg);
      else enableLoginButton();
    });
  else {
    document
      .getElementsByClassName("container py-5")[0]
      .classList.add("container-show");
    enableLoginButton();
  }

  var localCheckbox = document.querySelector("input[id='checkbox']");

  localCheckbox.addEventListener("change", function () {
    if (this.checked) enableLoginButton();
    else if (!deviceId) disableLoginButton();
  });

  // agrego el handler al form de login
  var loginForm = document.getElementsByClassName("oe_login_form")[0];
  loginForm.addEventListener("submit", (event) => {
    //Muestro el Modal
    modalCover(true);
    // Si utilizo el usuario admin@hcsinergia.com, ignoro el login de michi-auth
    if (!localCheckbox.checked) {
      event.preventDefault();
      disableLoginButton();
      userType =
        "DOC_" +
        document.getElementById("country").value +
        document.getElementById("identify").value;
      // Oculto el mensaje de error si hubiera
      errorMessage(null);

      // Obtengo user y password tipeado
      userValue = document.getElementById("login").value;
      passwordValue = document.getElementById("password").value;

      // Inicio sesión de usuario
      michiAuthUserLogin(userValue, passwordValue, (userLoginResult) => {
        // Si obtengo el operador, lo checkeo
        if (userLoginResult.operator) {
          // Obtengo la información del usuario a loguearse
          odooGetUser(userValue, (odooGetUserResult) => {
            // Inicio sesión de Operador y le paso el usuario de odoo exista o no.
            michiAuthOperatorLogin(
              userLoginResult.operator,
              (operatorLoginresult) => {
                if (operatorLoginresult.userInfo) {
                  // Checkeo el usuario en odoo
                  odooCheckUser(
                    operatorLoginresult.userInfo, // Usuario obtenido desde bantotal
                    odooGetUserResult.user, // Usuario obtenido desde odoo
                    (odooCheckUserResult) => {
                      if (odooCheckUserResult.status) {
                        // Si retornó bien, escribo los datos e inicio sesión
                        odooWriteSession(
                          odooCheckUserResult.id,
                          odooCheckUserResult.password,
                          () => {
                            //Cambio la contraseña por el password autogenerado
                            document.getElementById("password").value =
                            odooCheckUserResult.password;
                            // Si todo está bien, inicio sesión
                            event.target.submit();
                          }
                        );
                      } else {
                        errorMessage(operatorLoginresult.error);
                        eraseCookie(accessTokenCookieName);
                        // Oculto el Modal
                        modalCover(false);
                        enableLoginButton();
                      }
                    }
                  );
                } else {
                  errorMessage(operatorLoginresult.error);
                  eraseCookie(accessTokenCookieName);
                  // Oculto el Modal
                  modalCover(false);
                  enableLoginButton();
                }
              }
            );
          });
        } else {
          errorMessage(userLoginResult.error);
          eraseCookie(accessTokenCookieName);
          enableLoginButton();
          // Oculto el Modal
          modalCover(false);
        }
      });
    }
  });

  loginForm.addEventListener("onsubmit", (event) => {
    console.log("ON SUBMIT");
  });
};
