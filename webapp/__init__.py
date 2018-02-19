import flask
from webapp.app_init import app, db
from webapp import forms
import webapp.models as models
from webapp import parsing
import datetime


def link_for_entry(entry):
    return flask.url_for('date', date_str=entry.date_string)


def get_latest_entry():
    return db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()


def get_all_years():
    start_year = db.session.query(models.JournalEntry).first().create_date.year
    end_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first().create_date.year
    for y in range(start_year, end_year + 1):
        yield datetime.datetime(y, 1, 1, 0, 0)


app.jinja_env.globals.update(
    link_for_entry=link_for_entry,
    get_latest_entry=get_latest_entry,
    get_all_years=get_all_years)


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

    next_entry = db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date > e.create_date).first()
    prev_entry = db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date < e.create_date).order_by(
            models.JournalEntry.create_date.desc()).first()
    return flask.render_template(
        'entry.html',
        context=dict(entry=e, next_entry=next_entry, prev_entry=prev_entry))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
