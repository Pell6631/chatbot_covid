from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from joblib import load
import pandas as pd

modele = load('data/decision_tree.joblib')
data = pd.read_csv('data/Covid Dataset.csv')
data = data.drop(['Abroad travel','Wearing Masks','Sanitization from Market'], axis=1)

app = Flask(__name__)
CORS(app)

questionsDict = {
    "Sore throat": "Avez-vous mal à la gorge ?",
    "Breathing Problem": "Avez-vous un problème respiratoire ?",
    "Fever": "Avez-vous de la fièvre ?",
    "Dry Cough": "Avez-vous une toux sèche ?",
    "Running Nose": "Avez-vous le nez qui coule ?",
    "Asthma": "Avez-vous de l'asthme ?",
    "Chronic Lung Disease": "Avez-vous une maladie pulmonaire chronique ?",
    "Headache": "Avez-vous mal à la tête ?",
    "Heart Disease": "Avez-vous une maladie cardiaque ?",
    "Diabetes": "Avez-vous du diabète ?",
    "Hyper Tension": "Avez-vous de l'hypertension ?",
    "Fatigue ": "Êtes-vous fatigué ?",
    "Gastrointestinal ": "Avez-vous des problèmes gastro-intestinaux ?",
    "Contact with COVID Patient": "Avez-vous été en contact avec un patient atteint de la COVID ?",
    "Attended Large Gathering": "Avez-vous participé à un rassemblement public ?",
    "Visited Public Exposed Places": "Avez-vous visité des lieux publics exposés (école, restaurant, ...) ?",
    "Family working in Public Exposed Places": "Votre famille travaille-t-elle dans des lieux publics exposés (école, restaurant, ...) ?"
}
answersDict = {
    "Sore throat": [0],
    "Breathing Problem": [0],
    "Fever": [0],
    "Dry Cough": [0],
    "Running Nose": [0],
    "Asthma": [0],
    "Chronic Lung Disease": [0],
    "Headache": [0],
    "Heart Disease": [0],
    "Diabetes": [0],
    "Hyper Tension": [0],
    "Fatigue ": [0],
    "Gastrointestinal ": [0],
    "Contact with COVID Patient": [0],
    "Attended Large Gathering": [0],
    "Visited Public Exposed Places": [0],
    "Family working in Public Exposed Places": [0]
}

def make_tree_dict(clf):
    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    feature = clf.tree_.feature
    feature_names=data.columns.to_list()[:-1]
    values = clf.tree_.value
    

    node_dict = {}
    for i in range(n_nodes):
        if children_left[i] != children_right[i]:  # if not a leaf node
            node_dict[i] = {"feature": feature_names[feature[i]], "children": [children_left[i], children_right[i]], "result": None}
        else:  # if a leaf node
            node_dict[i] = {"feature": "Result", "children": [None, None], "result": values[i].argmax()}
    return node_dict


@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    response_data = request.get_json()

    node_dict = make_tree_dict(modele)
    node = node_dict[0]
    while node['feature'] != 'Result':
        answer = int(response_data['answer'])
        answersDict[node['feature']] = [answer]
        node = node_dict[node['children'][answer]]
        return jsonify(questionsDict[node['feature']])

    prediction = node['result']

    resultat = "Vous êtes potentiellement atteint du COVID-19" if prediction else "Vous n'êtes potentiellement pas atteint du COVID-19"

    return jsonify({"resultat": resultat})

@app.route('/')
def main():
    return render_template('/chatbot.html')


if __name__ == '__main__':
    app.run(debug=True)