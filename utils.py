from flask import jsonify

def success_data_jsonify(obj, code=200):
    response = jsonify({
        'success' : True,
        'data' : obj
    })

    response.status_code = code

    return response



def error_response(message, code):
    response = jsonify({'success' : False,
                        'error' : message
    })
    response.status_code = code

    return response
