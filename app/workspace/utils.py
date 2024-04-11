def format_errors(errors):
    """ format serializer ErrorDetail errors"""
    formatted_errors = {}
    for field, error_details in errors.items():
        formatted_errors[field] = [str(error_detail) for error_detail in error_details]
    return formatted_errors
