import json

def load_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)

    return json_data

def extract_json(json_data):
    """
    extract synonym from the json file.
    """
    for node in json_data["graphs"][0]["nodes"]:
        try:
            for synonym in node['meta']['synonyms']:
                print(synonym['val'])
        except Exception as e:
            pass

def extract_json2(json_data):
    """
    extract lbl tag from the json file
    """
    for node in json_data['graphs'][0]["nodes"]:
        try:
            print(node['lbl'])
        except:
            pass


if __name__ == '__main__':

    json_data = load_data('./DO_cancer_slim.json')
    extract_json(json_data)

    # json_data = load_data('./DO_cancer_slim.json')
    # extract_json2(json_data)