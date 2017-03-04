from flask import jsonify

def success_data_jsonify(obj={}, code=200):
    response = jsonify({
        'success' : True,
        'data' : obj
    })

    response.status_code = code

    return response



def error_response(title, message, code):

    error_dictionary = {'message' : message,
                        'title' : title}
    response = jsonify({'success' : False,
                        'error' : error_dictionary
    })
    response.status_code = code

    return response


def invalid_format():
    return error_response(title="Invalid request body",
                          message="You must provide the parameters in the form of a JSON object and set the Content-Type Header",
                          code=400)

def unauthorized_response():
    return error_response('Invalid authentication token', code=403)

