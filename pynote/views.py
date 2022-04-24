from flask import Blueprint, render_template, request, flash, jsonify, url_for, make_response
from flask_login import login_required, current_user, login_user
from werkzeug.utils import redirect

from .models import Note
from .models import User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Заметка слишком кароткая', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, user_id_2=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Заметка добавлена', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        first_name = request.form.get('firstName')

        user = User.query.filter_by(first_name=first_name).first()
        if user:
            return render_template("blog.html", user=user)
        else:
            flash('Такого пользователя не существует', category='error')
    return render_template("search.html", user=current_user)


@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@views.route('/avatar')
@login_required
def avatar():
    img = current_user.avatar
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@views.route('/avatar_not_current')
@login_required
def avatar_not_current(k):
    user = User.query.filter_by(first_name=k).first()
    img = user.avatar
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                img = file.read()
                my_id = current_user.id
                my_name = current_user.first_name
                my_email = current_user.email
                my_password = current_user.password
                user1 = User.query.filter_by(first_name=current_user.first_name).first()
                db.session.delete(user1)
                new_user = User(id=my_id, email=my_email, first_name=my_name, password=my_password, avatar=img)
                db.session.add(new_user)
                db.session.commit()
                db.session.query(Note).filter(Note.user_id_2 == my_id). \
                    update({Note.user_id: my_id}, synchronize_session=False)
                db.session.commit()
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('views.profile'))

