from flask import jsonify

def success_data_jsonify(obj):
    return jsonify({
        'success' : True,
        'data' : obj
    })
