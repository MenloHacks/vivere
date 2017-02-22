from flask import jsonify

def success_data_jsonify(obj):
    return jsonify({
        'success' : True,
        'data' : obj
    })

def error_response(message, code):
    response = jsonify({'success' : False,
                        'error' : message
    })
    response.status_code = code

    return response
