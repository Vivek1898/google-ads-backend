from fastapi import HTTPException
from fastapi.responses import JSONResponse

def handle_google_ads_exception(exception):
    print("Exception occurred: %s" % exception)
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    errors = []
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        errors.append(error.message)
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")


    return JSONResponse(status_code=500, content={
        "message": "An error occurred",
        "error": errors
                     })
