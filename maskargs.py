import functools
from typing import Callable, Sequence, Any, TypeAlias, Literal
import inspect

class ArgAdapter:
    ValueMap: TypeAlias = dict[str, str | int]
    ArgumentMap: TypeAlias = dict[str, ValueMap]
    HintMap: TypeAlias = dict[str, TypeAlias]
    
    __args__: ArgumentMap = {}
    
    def __init_subclass__(cls, **kwargs):
        """ Build Literals for the subclass and formats the __args__ dictionary to lowercase """
        # Build the literals for the subclass
        cls.__hints__: ArgAdapter.HintMap = {
            parameter: Literal[*list(options.keys())]
            for parameter, options in cls.__args__.items()
        }
        
        # Lowercase the keys for case insensitivity
        cls.__args__ = {k.lower(): v for k, v in cls.__args__.items()}
    
    @classmethod
    def maskargs(adapter: 'ArgAdapter', masked_function: Callable) -> Callable:
        
        # Grab signature from the masked function
        masked_function_signature = inspect.signature(masked_function)
        
        # Grab the parameters from the masked function
        function_parameters = masked_function_signature.parameters
        
        # Alias the adapters for clearer code
        adapters = adapter.__args__
        
        @functools.wraps(masked_function)
        def adapt_arguments(*args, **kwargs):
            """Convert a function call with named string arguments to a function call with named arguments from the adapter"""
            # Map the arguments to the function parameters
            adapted_arguments: dict[str, Any] = {
                parameter.name: value
                
                # zip the positional arguments (not strict, so optional args are dropped if they are in kwargs)
                for parameter, value in zip(function_parameters.values(), args)
                if parameter.kind in (
                    # strict positional arguments
                    inspect.Parameter.POSITIONAL_ONLY,
                    # optional positional arguments
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                     # *args
                    inspect.Parameter.VAR_POSITIONAL
                )
            }
            
            # Add the keyword arguments to the mapping
            # This will shadow any optional positional arguments
            # If they were provided as keyword arguments
            adapted_arguments.update(kwargs)
            
            invalid_args: list[Exception] = []
            for argument, arg_value in adapted_arguments.items():
                # Skip non-adapted arguments
                if argument not in adapters:
                    continue
                
                # Handle string arguments
                if isinstance(arg_value, str):
                    # Lowercase the argument value for case insensitivity
                    arg_value = arg_value.lower()
                    
                    # Raise an error if the argument is not in the adapter
                    if arg_value not in adapters[argument]:
                        invalid_args.append(
                            f'Invalid value for `{argument}`: ' 
                            f"'{arg_value}' "
                            f'(choices are {list(adapters[argument].keys())})'
                        )
                        continue
                    
                    # Update the argument value if it is in the adapter
                    adapted_arguments[argument] = adapters[argument][arg_value]
                
                # Handle sequence arguments
                elif isinstance(arg_value, Sequence):
                    # Change variable name for clarity
                    arg_values = arg_value
                    
                    # Get invalid arguments in argument sequence
                    invalid_values = [
                        arg_val 
                        for arg_val in arg_values 
                        if arg_val not in adapters[argument]
                    ]
                    
                    # Raise an error if there are invalid arguments in the sequence
                    if invalid_values:
                        invalid_args.append(
                            f'Invalid value{"s"*(len(invalid_values)>1)} for {argument}:'
                            f'{", ".join(map(str, invalid_values))}'
                            f'(choices are {list(adapters[argument].keys())})'
                        )
                        continue
                        
                    # Update the argument value if it is in the adapter 
                    adapted_arguments[argument] = [
                        adapters[argument][arg_val]
                        for arg_val in arg_values
                    ]
            
            if invalid_args:
                raise ValueError('\n'.join(invalid_args))
                
            # Pass the adapted arguments to the masked function
            return masked_function(**adapted_arguments)
        
        # Rebuild attribtues for the adapted function using the masked function
        for att in ('__doc__', '__annotations__', '__esri_toolinfo__'):
            setattr(
                adapt_arguments,
                att,
                (
                    # Get attribute from the adapted function first
                    getattr(adapt_arguments, att, None) or

                    # Get attribute from the masked function if it is not in the adapted function
                    getattr(masked_function, att, None) or

                    # Build __esri_toolinfo__ if it is in neither the adapted or masked function
                    [
                        f"String::"
                        f"{'|'.join(adapters[argument].keys())}:"
                        for argument in function_parameters.keys()
                        if argument in adapters
                    ]
                    if att == '__esri_toolinfo__'

                    # Default to None
                    else None
                )
            )
        
        # Apply literal type hints to the adapted function
        adapt_arguments.__annotations__.update(adapter.__hints__)
        
        # Allow manual annotations to override the literal type hints
        adapt_arguments.__annotations__.update(masked_function.__annotations__)
        
        return adapt_arguments
    
    @classmethod
    def maskmethods(adapter: 'ArgAdapter', other: type) -> None:
        # Grab all non dunder/private methods
        methods_to_mask = {
            method_name: method_object
            for method_name in dir(other)
            
            # Check if the method is callable and not private
            # Use the walrus operator to store the method object
            if callable(method_object := getattr(other, method_name))
            and not method_name.startswith("_")
        }
        
        # Mask the methods using the specified adapter
        for method_name, method_object in methods_to_mask.items():
            setattr(other, method_name, adapter.maskargs(method_object))
            

if __name__ == "__main__":
    # Test the ArgAdapter class
    class TestAdapter(ArgAdapter):
        __args__ = {
            "format": {"pdf": 1, "svg": 2, "eps": 3},
            "mode": {"read": 1, "write": 2, "execute": 4},
        }
        
    class Test:
        @TestAdapter.maskargs
        def testMasking(self, filename: str, format, mode):
            """Export a vector file to a specified format"""
            print(f"Exporting {filename} to {format} in {mode} mode")
            pass
    
    # Check annotations
    for annotation in Test.testMasking.__annotations__.items():
        print(annotation)
    t = Test()
    
    # Test the masking
    t.testMasking("test.pdf", format="pdf", mode="read")
    t.testMasking("test.pdf", format="pdf", mode="write")
    
    # Test that the exception gives you expected values
    try:
        t.testMasking("test.pdf", format="pdf", mode="update")
    except ValueError as e:
        print('\n-------Error-------')
        print(e)
        
    # Test that multiple incorrect values are caught
    try:
        t.testMasking("test.pdf", format="geojson", mode="update")
    except ValueError as e:
        print('\n-------Error-------')
        print(e)