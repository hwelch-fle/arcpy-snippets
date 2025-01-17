import functools
from typing import Callable, Any
import inspect

class ArgAdaptor:
    __args__ = {}
    
    @classmethod
    def maskargs(adaptor: 'ArgAdaptor', masked_function: Callable) -> Callable:
        masked_function_signature = inspect.signature(masked_function)
        function_parameters = masked_function_signature.parameters
        adaptors = adaptor.__args__
        
        @functools.wraps(masked_function)
        def adapted_arguments(*args, **kwargs):
            # Map the arguments to the function parameters
            adapted_arguments: dict[inspect.Parameter, Any] = \
            {
                parameter: value 
                for parameter, value in zip(function_parameters.values(), args) # zip the positional arguments
                if parameter.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,       # positional arguments
                    inspect.Parameter.POSITIONAL_OR_KEYWORD, # possibly positional arguments
                    inspect.Parameter.VAR_POSITIONAL         # *args
                )
            }
            
            # Add the keyword arguments to the mapping
            # This will shadow any optional positional arguments
            # If they were provided as keyword arguments
            adapted_arguments.update(kwargs)
            
            for argument, arg_value in adapted_arguments.items():
                # Skip non-adapted arguments
                if argument.name not in adaptors:
                    continue
                
                # Uppercase string values
                if isinstance(arg_value, str):
                    arg_value = arg_value.upper()
                
                # Update the argument value if it is in the adaptor   
                if arg_value in adaptors[argument.name]:
                    adapted_arguments[argument] = adaptors[argument.name][arg_value]
                    continue
                
                # Raise an error if the argument is not in the adaptor
                raise ValueError(f'Argument {argument.name} is not in the adaptor')
            
            # Pass the adapted arguments to the masked function
            return masked_function(**adapted_arguments)
        
        # Rebuild docs
        if not adapted_arguments.__doc__:
            adapted_arguments.__doc__ = masked_function.__doc__
        
        # Rebuild annotations  
        if not adapted_arguments.__annotations__:
            adapted_arguments.__annotations__ = masked_function.__annotations__
        
        # Rebuild esri_toolinfo
        if hasattr(masked_function, '__esri_toolinfo__'):
            adapted_arguments.__esri_toolinfo__ = masked_function.__esri_toolinfo__
        
        # Build default esri_toolinfo
        else:
            adapted_arguments.__esri_toolinfo__ = [
                f"String::{'|'.join(adaptors[argument].keys())}:"
                for argument in function_parameters.keys()
            ]
        return adapted_arguments
    
    @classmethod
    def maskmethods(mask: 'ArgAdaptor', other: type):
        # Grab all non dunder/private methods
        methods = {
            method_name: method
            for method_name in dir(other)
            if callable(method := getattr(other, method_name)) and not method_name.startswith("_")
        }
        
        # Mask the methods usinf the specified adaptor
        for method_name, method in methods.items():
            setattr(other, method_name, mask.maskargs(method))