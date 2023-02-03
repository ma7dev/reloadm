import importlib
import types


def reload(module, verbose=False):
    if verbose:
        print(module)
        print(type(module))

    module_list = None

    if module and isinstance(module, types.ModuleType):
        module_list = module.__name__.split(".")
    elif module and (
        isinstance(module, types.FunctionType)
        or module
        and isinstance(module, types.BuiltinMethodType)
    ):
        module_list = module.__module__.split(".")
    else:
        raise NotImplementedError("didn't implement this yet...")

    for order in range(1, len(module_list) + 1):
        current_module_str = ".".join(module_list[:order])
        if verbose:
            print(current_module_str)
        current_module = importlib.import_module(current_module_str)
        if current_module or isinstance(current_module, types.ModuleType):
            importlib.reload(current_module)
