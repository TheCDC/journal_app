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
            body_text = e.body.replace('\r', '')
            found = db.session.query(
                models.JournalEntry).filter_by(create_date=e.date).first()
            if found:
                print('found', found)
                found.contents = body_text
            else:
                found = models.JournalEntry(
                    create_date=e.date, contents=body_text)
            session.add(found)
        session.flush()
        session.commit()
        # print('file', file.read())
        return flask.redirect(flask.url_for('index'))
    all_entries = list(
        db.session.query(models.JournalEntry).order_by(
            models.JournalEntry.create_date))

    return flask.render_template(
        'index.html', context=dict(form=form, entries=all_entries))


@app.route("/entry/<string:date_str>")
def date(date_str):
    tokens = list(map(int, date_str.split("-")))
    d = datetime.datetime(*(tokens + [0, 0]))
    e = db.session.query(models.JournalEntry).filter_by(create_date=d).first()
    return e.to_html()


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
