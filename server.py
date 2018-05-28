import requests
from flask import Flask, request
from flask_restful import Resource, Api
from flask import Response
from flask import send_file

app = Flask(__name__)
api = Api(app)


def getFromIndex( index, indexes ):
    for e in indexes:
        if indexes[e] == index:
            return e
        
def predsToDict( preds, indexes ):
    final_preds = {}
    for i in range (len( preds )):
        final_preds[getFromIndex(i, indexes)] = preds[i]
    return final_preds

def getPrediction( steps, city ):
    url = 'http://samples.openweathermap.org/data/2.5/forecast?q={}&appid=b6907d289e10d714a6e88b30761fae22'.format(city)
    a = eval(requests.get(url).text)
    current = a['list'][len(a['list'])-1]['weather'][0]['main']
    states = {}
    for e in a['list']:
        state = e['weather'][0]['main']
        states[state] = 1
    transitions = {}
    totals_per_state = {}
    sample_size = len(a['list']) - 1
    count = 0
    prev = None
    for e in a['list']:
        state = e['weather'][0]['main']
        
        if prev not in transitions: 
            transitions[prev] = {}
            transitions[prev][state] = 1
        else:
            if state not in transitions[prev]: transitions[prev][state] = 1
            else: transitions[prev][state] += 1
        
        if prev not in totals_per_state:
            totals_per_state[prev] = 1
        else:
            totals_per_state[prev] += 1
        
        prev = state
        

    for e in transitions:
        if e is None: 
            transitions.pop(e)
            totals_per_state.pop(e)
            break

    probabilities = {}
    for prev in transitions:
        for current in transitions[prev]:
            probabilities[(prev,current)] = round(transitions[prev][current]/totals_per_state[prev],2)

    ###### clear cloud
    #clear    x    x
    #cloud    x    x
    import numpy
    m_transitions = numpy.zeros(shape=(len(states), len(states)))

    indexes = {}
    count = 0
    for e in states:
        indexes[e] = count
        count+=1

    for p, n in probabilities:
        m_transitions[indexes[p],indexes[n]] = probabilities[(p,n)]
    

    
    return {
        'current': current,
        'predictions': [predsToDict( list(numpy.linalg.matrix_power(m_transitions,step+1)[indexes[current]]), indexes ) for step in range(1, steps+1)]
    }

class Predictions(Resource):
    def get(self):
        steps = int(request.args['steps'])
        city = request.args['city']
		
        return getPrediction(steps,city)

api.add_resource(Predictions, '/predictions')

if __name__ == '__main__':
	app.run(port=5002, host='0.0.0.0') #uiaf