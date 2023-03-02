import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import joblib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import time
import logging

app = Flask(__name__)

engine = create_engine('mysql+pymysql://vedran99:vedran99@db:3306/bazaTumori')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class RequestLog(Base):
    __tablename__ = 'request_log'
    id = Column(Integer, primary_key=True)
    request_time = Column(DateTime, default=None)
    calculation_time = Column(Integer, default=None)
    prediction_label = Column(String(length=12), default=None)


@app.route('/predictJson', methods=['POST'])
def predict():
    req = request.get_json()
    input_data = req['data']

    input_data_df = pd.DataFrame.from_dict(input_data)

    model = joblib.load('model.pkl')

    scale_obj = joblib.load('scale.pkl')

    input_data_scaled = scale_obj.transform(input_data_df)

    prediction = model.predict(input_data_scaled)

    if prediction[0] == 1:
        cancer_type = 'Malignant'
    else:
        cancer_type = 'Benign'

    return jsonify({'output': {'cancer_type': cancer_type}})


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        dbQuery = session.query(RequestLog).all()
        db = []
        for row in dbQuery:
            d = {}
            for column in row.__table__.columns:
                d[column.name] = str(getattr(row, column.name))
            db.append(d)
        # app.logger.info(db)

        return render_template('index.html', db=db)
    else:
        request_time = datetime.utcnow()
        start_time = time.perf_counter()

        mean_radius = request.form.get('mean radius')
        mean_texture = request.form.get('mean texture')
        mean_perimeter = request.form.get('mean perimeter')
        mean_area = request.form.get('mean area')
        mean_smoothness = request.form.get('mean smoothness')
        mean_compactness = request.form.get('mean compactness')
        mean_concavity = request.form.get('mean concavity')
        mean_concave_points = request.form.get('mean concave points')
        mean_symmetry = request.form.get('mean symmetry')
        mean_fractal_dimension = request.form.get('mean fractal dimension')
        radius_error = request.form.get('radius error')
        texture_error = request.form.get('texture error')
        perimeter_error = request.form.get('perimeter error')
        area_error = request.form.get('area error')
        smoothness_error = request.form.get('smoothness error')
        compactness_error = request.form.get('compactness error')
        concavity_error = request.form.get('concavity error')
        concave_points_error = request.form.get('concave points error')
        symmetry_error = request.form.get('symmetry error')
        fractal_dimension_error = request.form.get('fractal dimension error')
        worst_radius = request.form.get('worst radius')
        worst_texture = request.form.get('worst texture')
        worst_perimeter = request.form.get('worst perimeter')
        worst_area = request.form.get('worst area')
        worst_smoothness = request.form.get('worst smoothness')
        worst_compactness = request.form.get('worst compactness')
        worst_concavity = request.form.get('worst concavity')
        worst_concave_points = request.form.get('worst concave points')
        worst_symmetry = request.form.get('worst symmetry')
        worst_fractal_dimension = request.form.get('worst fractal dimension')

        obj = {
                "data": [
                    {
                        "mean radius": mean_radius,
                        "mean texture": mean_texture,
                        "mean perimeter": mean_perimeter,
                        "mean area": mean_area,
                        "mean smoothness": mean_smoothness,
                        "mean compactness": mean_compactness,
                        "mean concavity": mean_concavity,
                        "mean concave points": mean_concave_points,
                        "mean symmetry": mean_symmetry,
                        "mean fractal dimension": mean_fractal_dimension,
                        "radius error": radius_error,
                        "texture error": texture_error,
                        "perimeter error": perimeter_error,
                        "area error": area_error,
                        "smoothness error": smoothness_error,
                        "compactness error": compactness_error,
                        "concavity error": concavity_error,
                        "concave points error": concave_points_error,
                        "symmetry error": symmetry_error,
                        "fractal dimension error": fractal_dimension_error,
                        "worst radius": worst_radius,
                        "worst texture": worst_texture,
                        "worst perimeter": worst_perimeter,
                        "worst area": worst_area,
                        "worst smoothness": worst_smoothness,
                        "worst compactness": worst_compactness,
                        "worst concavity": worst_concavity,
                        "worst concave points": worst_concave_points,
                        "worst symmetry": worst_symmetry,
                        "worst fractal dimension": worst_fractal_dimension
                    }
                ]
        }

        res = requests.post('http://app:5000/predictJson', json=obj, headers={'Content-Type': 'application/json'})

        cancer = res.json()['output']['cancer_type']

        end_time = time.perf_counter()
        calculation_time = int((end_time - start_time) * 1000000)
        request_log = RequestLog(request_time=request_time, calculation_time=calculation_time, prediction_label=cancer)
        session.add(request_log)
        session.commit()

        return render_template('prediction.html', cancer=cancer)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()
    app.run(host='0.0.0.0', port='5000', debug=True)
