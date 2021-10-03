from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from ortools.linear_solver import pywraplp
import json

app = Flask(__name__)
api = Api(app)


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class search_nextpage(Resource):
    def post(self):
        print(request.get_data())

        esgvalue = request.json['esgvalue']
        stockpricepredicted = request.json['stockpricepredicted']

        print(float(esgvalue))
        print(float(stockpricepredicted))

        esgvalueint = int(float(esgvalue))
        stockpricepredictedint = int(float(stockpricepredicted))

        # Create the linear solver with the GLOP backend.
        solver = pywraplp.Solver.CreateSolver('GLOP')

        # Create the variables alpha and beta.
        alpha = solver.NumVar(0, 1, 'alpha')
        beta = solver.NumVar(0, 2, 'beta')

        print('Number of variables =', solver.NumVariables())

        # Create a linear constraint, 0 <= alpha + beta <= 1.
        ct = solver.Constraint(0, 1, 'ct')
        ct.SetCoefficient(alpha, 1)
        ct.SetCoefficient(beta, 1)

        print('Number of constraints =', solver.NumConstraints())

        # Create the objective function, alpha*esg_value + beta* stock_price_predicted.
        objective = solver.Objective()
        objective.SetCoefficient(alpha, esgvalueint)
        objective.SetCoefficient(beta, stockpricepredictedint)
        objective.SetMaximization()

        solver.Solve()

        print('Solution:')
        print('Objective value =', objective.Value())
        print('alpha =', alpha.solution_value())
        print('beta =', beta.solution_value())

        me = Object()
        me.alpha = alpha.solution_value()
        me.beta = beta.solution_value()

        return me.toJSON()


api.add_resource(search_nextpage, '/evaluate')

if __name__ == '__main__':
    app.run()
