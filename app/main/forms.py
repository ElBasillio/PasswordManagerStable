from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, BooleanField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional
from zxcvbn import zxcvbn

class PasswordForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=64)])
    username = StringField('Username', validators=[Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    url = StringField('URL', validators=[Optional(), URL(), Length(max=256)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')

    def validate_password(self, password):
        result = zxcvbn(password.data)
        if result['score'] < 3:
            suggestions = ' '.join(result['feedback']['suggestions'])
            raise ValidationError(f'Password is too weak. {suggestions}')

class VaultForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    description = TextAreaField('Description')
    icon = StringField('Icon URL')

class AccountForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=64)])
    username = StringField('Username', validators=[Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    url = URLField('URL', validators=[Optional(), URL()])
    notes = TextAreaField('Notes')
    icon = StringField('Icon URL')
    is_favorite = BooleanField('Favorite')
    vault_id = SelectField('Vault', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int)
    password_expires_at = DateTimeField('Password Expiration Date', validators=[Optional()])
    tags = StringField('Tags (comma separated)')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    icon = StringField('Icon URL')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    vault = SelectField('Vault', coerce=int)
    category = SelectField('Category', coerce=int)
    favorites_only = BooleanField('Favorites Only')

class CustomFieldForm(FlaskForm):
    field_name = StringField('Field Name', validators=[DataRequired(), Length(min=1, max=64)])
    field_value = StringField('Field Value', validators=[DataRequired()]) 