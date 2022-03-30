from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    team_leader = StringField('Тим лидер', validators=[DataRequired()])
    job = TextAreaField("Описание работы")
    work_size = IntegerField("Объем работы")
    collaborators = StringField("Сотрудники(example: 'surname1 name1, surname2 name2, surname3 name2' and etc.)")
    is_finished = BooleanField("Работа закончена?")
    submit = SubmitField('Добавить')
