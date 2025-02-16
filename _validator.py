class _validator:
    def check_null_values(*args):
        # Function to check for null values in provided arguments
        # Return True if any value is None, else False
        return any(value is None for value in args)
    
    def check_int_type(*values):
        # Initialize a list to store values that are not int/float
        false_type = []
        for variable in values:
            try:
                # Try to convert the variable to a float
                float_variable = float(variable)
                # If successful, check if it's an integer or float
                if not isinstance(float_variable, (int, float)):
                    false_type.append(variable)
            except ValueError:
                # If conversion fails, append the original variable
                false_type.append(variable)
        
        # If there are non-int/float values, return them
        if false_type:
            return False
        
        # If all values are int/float, return True
        return True

    def check_string_type(variable):
        # Return True if the variable is a string, else False
        return True if isinstance(variable, str) else False
    
    def convert_type(status):
        # Convert status strings to corresponding integer codes
        if status == "DENIED":
            return 0
        elif status == "APPROVED":
            return 1
        elif status == "PENDING":
            return 2
        else:
            return "Unknown value"
