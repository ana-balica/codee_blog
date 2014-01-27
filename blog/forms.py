from wtforms import Form, TextField, TextAreaField, SubmitField, validators


class ContactForm(Form):
    '''
    Simple contact form on the contact page
    '''
    name = TextField('name', [validators.Length(min=4, max=25)])
    email = TextField('email',
                      [validators.Length(min=6, max=35), validators.Email()])
    message = TextAreaField('message', [validators.Length(min=15, max=500)])
    submit = SubmitField('submit')