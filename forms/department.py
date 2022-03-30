from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class DepartmentForm(FlaskForm):
    chief = StringField('Шеф', validators=[DataRequired()])
    title = TextAreaField("Описание отдела")
    members = StringField("Члены отдела")
    email = StringField("Почта")
    submit = SubmitField('Добавить')
