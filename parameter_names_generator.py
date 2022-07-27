import biodivine_aeon as ba

KNOCKOUT_PREFIX = "knck"
OVER_EXPRESSION_PREFIX = "overex"
FUNCTION_PREFIX = "updt"


def get_knockout_from_var(bn: ba.BooleanNetwork, var_id: ba.VariableId):
    var_name = bn.get_variable_name(var_id)
    return get_knockout_from_name(var_name)


def get_knockout_from_name(var_name: str):
    return f"{KNOCKOUT_PREFIX}_{var_name}"


def get_over_expression_from_var(bn: ba.BooleanNetwork, var_id: ba.VariableId):
    var_name = bn.get_variable_name(var_id)
    return get_over_expression_from_name(var_name)


def get_over_expression_from_name(var_name: str):
    return f"{OVER_EXPRESSION_PREFIX}_{var_name}"


def get_explicit_update_function_parameter_from_var(bn: ba.BooleanNetwork, var_id: ba.VariableId):
    var_name = bn.get_variable_name(var_id)
    return get_explicit_update_function_parameter_from_name(var_name)


def get_explicit_update_function_parameter_from_name(var_name: str):
    return f"{FUNCTION_PREFIX}_var_name"
