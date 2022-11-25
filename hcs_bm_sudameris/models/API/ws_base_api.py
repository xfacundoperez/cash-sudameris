class BM_ApiBase:
    """# API Exclusiva para Sudameris Bank"""

    def __init__(self, config_parameter):
        self.config_parameter = config_parameter
        self.base_url = "http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?"
        self.authenticate = {
            "Btinreq": {
                "Device": "10.103.103.31",
                "Usuario": "GEIER",
                "Requerimiento": "1",
                "Canal": "BTINTERNO",
                "Token": ""
            },
            "UserId": "GEIER",
            "UserPassword": "Albuquerque2021"
        }
        # Obtengo las credenciales de autenticación
        self.ws_authenticate()

    def ws_authenticate(self, *args, **kwargs):
        """# API Authenticate"""
        from .ws_authenticate import ApiWsAuthenticate
        _api = ApiWsAuthenticate(
            self.base_url, self.authenticate, self.config_parameter)
        token = _api.get_token()
        self.authenticate['Btinreq']['Token'] = token

    def ws_valida_base_confiable(self, official, *args, **kwargs):
        """# API Valida Base Confiable"""
        from .ws_valida_base_confiable import ApiWsValidaBaseConfiable
        _api = ApiWsValidaBaseConfiable(self.base_url, self.authenticate)
        return _api.ws_valida_base_confiable(official)

    def ws_cliente_posee_cuenta(self, official, *args, **kwargs):
        """# API Cliente posee cuenta"""
        from .ws_cliente_posee_cuenta import ApiWsClientePoseeCuenta
        _api = ApiWsClientePoseeCuenta(self.base_url, self.authenticate)
        return _api.ws_cliente_posee_cuenta(official)

    def ws_consulta_cuenta_servicio(self, cuenta, *args, **kwargs):
        """# API Valida Base Confiable"""
        from .ws_consulta_cuenta_servicio import ApiWsConsultaCuentaServicio
        _api = ApiWsConsultaCuentaServicio(self.base_url, self.authenticate)
        return _api.ws_consulta_cuenta_servicio(cuenta)

    def ws_control_cliente_payroll(self, official, *args, **kwargs):
        """# API Control Cliente Payroll (35 días)"""
        from .ws_control_cliente_payroll import ApiWsControlClientePayroll
        _api = ApiWsControlClientePayroll(self.base_url, self.authenticate)
        return _api.ws_control_cliente_payroll(official)

    def ws_alta_cuenta(self, official, *args, **kwargs):
        """# API Alta de Cuenta"""
        from .ws_alta_cuenta import ApiWsAltaCuenta
        _api = ApiWsAltaCuenta(self.base_url, self.authenticate)
        return _api.ws_alta_cuenta(official)

    def ws_alta_ca(self, official, *args, **kwargs):
        """# API Estado de Caja de Ahorro"""
        from .ws_alta_ca import ApiWsAltaCA
        _api = ApiWsAltaCA(self.base_url, self.authenticate)
        return _api.ws_alta_ca(official)

    def ws_estado_ca(self, official, *args, **kwargs):
        """# API Estado de Caja de Ahorro"""
        from .ws_estado_ca import ApiWsEstadoCA
        _api = ApiWsEstadoCA(self.base_url, self.authenticate)
        return _api.ws_estado_ca(official)

    def ws_alta_td(self, official, *args, **kwargs):
        """# API Alta de la Tarjeta de Debito"""
        from .ws_alta_td import ApiWsAltaTD
        _api = ApiWsAltaTD(self.base_url, self.authenticate)
        return _api.ws_alta_td(official)

    def ws_estado_td(self, official, *args, **kwargs):
        """# API Estado de la Tarjeta de Debito"""
        from .ws_estado_td import ApiWsEstadoTD
        _api = ApiWsEstadoTD(self.base_url, self.authenticate)
        return _api.ws_estado_td(official)
