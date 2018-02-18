import os
import flask
from webapp.app_init import app, db
from webapp import forms
import webapp.models as models
from webapp import parsing
import datetime
journal_file = os.path.join('..', 'Oh_Life_You_So_Funny.txt')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.UploadForm(flask.request.form)

    if flask.request.method == 'POST':
        form = forms.UploadForm(flask.request.form)
        print('vars(form.file)', vars(form.file))
        if form.validate():
            print('Validated!')
        print('files', flask.request.files)
        file = flask.request.files[form.file.name]
        # print('file', vars(file))
        session = db.session()
        for e in parsing.identify_entries(file.read().decode().split('\n')):
            j = models.JournalEntry(
                create_date=e.date, contents=e.body.replace('\r', ''))
            session.add(j)
        session.flush()
        session.commit()
        # print('file', file.read())
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('index.html', context=dict(form=form))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
