from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# # Define the path to the JSON file
# json_file_path = os.path.join(os.path.dirname(__file__), 'q-vercel-python.json')

# print(json_file_path)
# # Load student marks from the JSON file
# def load_student_marks():
#     try:
#         with open(json_file_path, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return [{"name": "Default", "marks": 0}] 

STUDENT_DATA = [{"name":"mGtnrgW","marks":37},{"name":"pTRJKlmua","marks":90},{"name":"u","marks":44},{"name":"n3yP83W","marks":95},{"name":"iCLK1UBz3E","marks":58},{"name":"IB69T","marks":15},{"name":"66yv58","marks":93},{"name":"GlXD13","marks":51},{"name":"XeV","marks":35},{"name":"AzNNt5q","marks":28},{"name":"AQLHcS","marks":49},{"name":"yE9j","marks":71},{"name":"92","marks":57},{"name":"MMIXcq","marks":54},{"name":"tCkOmyz2iG","marks":52},{"name":"Ku1kl","marks":91},{"name":"RdwBMdvvE","marks":65},{"name":"WoZ18HMgh6","marks":69},{"name":"FqwrDzTp","marks":45},{"name":"pbrFuzIl","marks":90},{"name":"g","marks":53},{"name":"lhucj","marks":45},{"name":"lbRZ","marks":18},{"name":"NyuahLv","marks":72},{"name":"o82Zlg6V","marks":91},{"name":"cjxPlb","marks":47},{"name":"Bj5r11","marks":98},{"name":"d8240e","marks":23},{"name":"5oXsRl","marks":90},{"name":"Yv9SVAV","marks":73},{"name":"xR","marks":2},{"name":"mJ4uowcZp","marks":52},{"name":"sOGyFAj","marks":30},{"name":"m","marks":87},{"name":"UbuOSAs1g1","marks":64},{"name":"lYFQfkJI","marks":29},{"name":"ALn24RjE","marks":91},{"name":"5cLwfGe4","marks":31},{"name":"0BF","marks":51},{"name":"d","marks":65},{"name":"vpAASJwb","marks":20},{"name":"Va2Hb","marks":71},{"name":"gpbv1","marks":21},{"name":"Jn4Sne2WJw","marks":44},{"name":"03H6H2wXJ","marks":53},{"name":"W","marks":92},{"name":"eDlb","marks":25},{"name":"iWTRGF","marks":74},{"name":"c4dDpSb","marks":92},{"name":"WxH4syG2F","marks":89},{"name":"0iCmV","marks":75},{"name":"f","marks":0},{"name":"9I3","marks":38},{"name":"2xZyNj","marks":44},{"name":"zf5HWfA","marks":97},{"name":"0bTWng2uA","marks":59},{"name":"0ISpnr5JF","marks":35},{"name":"LBjOlpBsk","marks":33},{"name":"BpmmJlUUBg","marks":82},{"name":"DVcBjv","marks":86},{"name":"s1GtR6","marks":17},{"name":"n28","marks":88},{"name":"1HZHHWCN","marks":19},{"name":"iJUWAahnW","marks":64},{"name":"qRIuc","marks":58},{"name":"XTLR5Y","marks":52},{"name":"Ofl","marks":31},{"name":"jVe7D","marks":55},{"name":"4os","marks":15},{"name":"GPb2f","marks":76},{"name":"pt","marks":52},{"name":"T2POlk9B","marks":21},{"name":"jO4Y","marks":90},{"name":"rPASTXMFTS","marks":61},{"name":"e","marks":19},{"name":"Q","marks":99},{"name":"ty09mUeC0","marks":58},{"name":"GM6D","marks":55},{"name":"l5pN","marks":83},{"name":"z3N","marks":45},{"name":"jf6c","marks":38},{"name":"bm3oI3fq","marks":1},{"name":"X","marks":89},{"name":"0pAf4","marks":22},{"name":"7orll","marks":23},{"name":"zX","marks":41},{"name":"klvLipBmQa","marks":1},{"name":"vQHWg7DF","marks":72},{"name":"ejBCk","marks":59},{"name":"x","marks":65},{"name":"w96uIbDs","marks":98},{"name":"8yFmcUdH","marks":28},{"name":"uGAwIIoE","marks":22},{"name":"ZgdlsoWc","marks":45},{"name":"tbCNJYw","marks":52},{"name":"OPAh","marks":27},{"name":"PDscMU3SFJ","marks":32},{"name":"VMQ","marks":85},{"name":"Xhr6Vm","marks":96},{"name":"ya0EExGMwx","marks":62}]
def load_student_marks():
    return STUDENT_DATA
@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def get_marks():
    # Get the list of names from the query string
    names = request.args.getlist('name')
    student_marks = load_student_marks()

    # Look for the student marks in the list of dictionaries
    marks = []
    for name in names:
        # Search for the student's mark based on the name
        student = next((item for item in student_marks if item["name"] == name), None)
        
        if student:
            marks.append(student["marks"])
        else:
            marks.append(0)

    return jsonify({"marks": marks})

# if __name__ == '__main__':
#     app.run(debug=True)