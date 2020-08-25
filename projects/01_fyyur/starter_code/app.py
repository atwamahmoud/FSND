# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from common import GENRES
import psycopg2
import re
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.relationship('VGenres', backref="venue")
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref="venue")


class VGenres(db.Model):
    __tablename__ = 'VGenres'

    genre = db.Column(db.Enum(GENRES), primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False, primary_key=True)

class AGenres(db.Model):
    __tablename__ = 'AGenres'

    agenre = db.Column(db.Enum(GENRES), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False, primary_key=True)
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    aid = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.TIMESTAMP, nullable=False)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref="artist")
    genres = db.relationship("AGenres", backref="artist")

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format_type='medium'):
    date = dateutil.parser.parse(value)
    if format_type == 'full':
        format_type = "EEEE MMMM, d, y 'at' h:mma"
    elif format_type == 'medium':
        format_type = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format_type)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def get_idx(data, city, _state):
    for i in range(0, len(data)):
        if data[i].get('city') == city and data[i].get('state') == _state:
            return i

    return -1

@app.route('/venues')
def venues():
    v = Venue.query.all()
    data = []
    for i in range(0, len(v)):
        idx = get_idx(data, v[i].city, v[i].state)
        v_dict = {
            "id": v[i].id,
            "name": v[i].name,
            "num_upcoming_shows": len(v[i].shows)
        }
        if idx != -1:
            data[idx].get('venues').append(v_dict)
        else:
            data.append({
                "city": v[i].city,
                "state": v[i].state,
                "venues": [v_dict]
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    term = request.form.get('search_term')
    raw = Venue.query.filter(Venue.name.ilike("%" + term + "%")).all()
    data = list(map(lambda v: {
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(list(filter(filter_upcoming_shows, v.shows)))
    }, raw))
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


def filter_past_shows(show):
    if(show.start_time > datetime.today()):
        return False
    else:
        return True
def filter_upcoming_shows(show):
    if(show.start_time < datetime.today()):
        return False
    else:
        return True
def map_show(show):
    return {
        "artist_id": show.aid,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
    }
def map_show_artist(show):
    return {
        "venue_id": show.vid,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
    }
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    v = Venue.query.get(venue_id)
    if v is None:
        flash("Can't find such venue!")
        return redirect("/")
    else:
        past_shows = list(filter(filter_past_shows, v.shows))
        upcoming_shows = list(filter(filter_upcoming_shows, v.shows))
        data = {
            "id": v.id,
            "past_shows": list(map(map_show, past_shows)),
            "upcoming_shows": list(map(map_show, upcoming_shows)),
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
            "name": v.name,
            "city": v.city,
            "state": v.state,
            "address": v.address,
            "phone": v.phone,
            "image_link": v.image_link,
            "facebook_link": v.facebook_link,
            "genres": map(lambda x: x.genre.value, VGenres.query.filter_by(vid=venue_id).all()),
            "website": v.website,
            "seeking_talent": v.seeking_talent,
            "seeking_description": v.seeking_description
        }
        return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    get = request.form.get

    if not form.validate():
        flash(form.errors)
        return render_template('forms/new_venue.html', form=form)
    venue = Venue(
        address=get("address"),
        name=get("name"),
        city=get("city"),
        state=get("state"),
        phone=get("phone"),
        facebook_link=get("facebook_link"),
        image_link=get("image_link"),
        website=get("website"),
        seeking_description=get("seeking_description"),
        seeking_talent=get("seeking_talent") == 'YES'
    )
    db.session.add(venue)
    db.session.commit()
    _genres = request.form.getlist("genres")
    for i in range(0, len(_genres)):
        _genre = VGenres(genre=_genres[i], vid=venue.id)
        db.session.add(_genre)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect("/venues/" + str(venue.id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        v = Venue.query.get(int(venue_id))
        name = v.name
        _genres = VGenres.query.filter_by(vid=venue_id).all()
        for i in range(0, len(_genres)):
            db.session.delete(_genres[i])
        db.session.delete(v)
        db.session.commit()
        flash("Deleted " + name + " Successfully")
    except Exception as e:
        flash(str(e))
    finally:
        return redirect('/')
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    _artists = Artist.query.all()
    data = list(map(lambda artist: {
        "id": artist.id,
        "name": artist.name
    }, _artists))

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term')
    raw = Artist.query.filter(Artist.name.ilike("%" + term + "%")).all()
    data = list(map(lambda a: {
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": len(list(filter(filter_upcoming_shows, a.shows)))
    }, raw))
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    a = Artist.query.get(artist_id)
    if a is None:
        flash("Can't find such Artist!")
        return redirect("/")
    else:
        past = list(filter(filter_past_shows, a.shows))
        upcoming = list(filter(filter_upcoming_shows, a.shows))
        data = {
            "id": a.id,
            "past_shows": list(map(map_show_artist, past)),
            "upcoming_shows": list(map(map_show_artist, upcoming)),
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming),
            "name": a.name,
            "city": a.city,
            "state": a.state,
            "phone": a.phone,
            "image_link": a.image_link,
            "facebook_link": a.facebook_link,
            "genres": map(lambda x: x.agenre.value, AGenres.query.filter_by(aid=artist_id).all()),
            "website": a.website,
            "seeking_venue": a.seeking_venue,
            "seeking_description": a.seeking_description,
        }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = EditArtistForm()
    a = Artist.query.get(artist_id)
    artist = {
        "id": a.id,
        "name": a.name,
        "genres": list(map(lambda x: x.agenre.value, AGenres.query.filter_by(aid=artist_id).all())),
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # called upon submitting the new artist listing form
    form = EditArtistForm(request.form)
    get = request.form.get

    if not form.validate():
        flash(form.errors)
        return redirect('/artists/' + str(artist_id) + '/edit')

    is_seeking = get("seeking_venue") == 'YES'
    artist = Artist.query.get(artist_id)
    artist.city = get('city')
    artist.state = get('state')
    artist.phone = get('phone')
    artist.facebook_link = get('facebook_link')
    artist.image_link = get('image_link')
    artist.website = get('website')
    artist.seeking_venue = is_seeking
    artist.seeking_description = get('seeking_description')
    # db.session.commit()
    _old_genres = list(map(lambda x: x.agenre.name, artist.genres))
    # delete all _old_genres...
    for i in range(0, len(artist.genres)):
        db.session.delete(artist.genres[i])

    db.session.commit()
    # add new genre..
    _genres = request.form.getlist("genres")
    for i in range(0, len(_genres)):
        _genre = AGenres(agenre=_genres[i], aid=artist_id)
        db.session.add(_genre)
    db.session.commit()


    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully Updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    v = Venue.query.get(venue_id)
    venue = {
        "id": venue_id,
        "name": v.name,
        "genres": list(map(lambda x: x.genre.value, VGenres.query.filter_by(vid=venue_id).all())),
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = EditVenueForm(request.form)
    get = request.form.get

    if not form.validate():
        flash(form.errors)
        return redirect('/venues/' + str(venue_id) + '/edit')

    try:
        is_seeking = get("seeking_talent") == 'YES'
        venue = Venue.query.get(venue_id)
        venue.city = get('city')
        venue.state = get('state')
        venue.phone = get('phone')
        venue.facebook_link = get('facebook_link')
        venue.image_link = get('image_link')
        venue.website = get('website')
        venue.seeking_talent = is_seeking
        venue.seeking_description = get('seeking_description')
        _old_genres = list(map(lambda x: x.genre.name, venue.genres))
        # delete all _old_genres...
        for i in range(0, len(venue.genres)):
            db.session.delete(venue.genres[i])
        db.session.commit()

        # add new genre..
        _genres = request.form.getlist("genres")
        for i in range(0, len(_genres)):
            _genre = VGenres(genre=_genres[i], vid=venue_id)
            db.session.add(_genre)
        db.session.commit()
    except Exception as e:
        flash(str(e))
        return redirect('/venues/' + str(venue_id) + '/edit')
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully Updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
    get = request.form.get

    if not form.validate():
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)

    is_seeking = get("seeking_venue") == 'YES'
    artist = Artist(
        name=get("name"),
        city=get("city"),
        state=get("state"),
        phone=get("phone"),
        facebook_link=get("facebook_link"),
        image_link=get("image_link"),
        website=get("website"),
        seeking_venue=is_seeking,
        seeking_description=get("seeking_description") if is_seeking else ""
    )
    db.session.add(artist)
    db.session.commit()
    _genres = request.form.getlist("genres")
    for i in range(0, len(_genres)):
        _genre = AGenres(agenre=_genres[i], aid=artist.id)
        db.session.add(_genre)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect("/artists/" + str(artist.id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    _shows = Show.query.all()
    data = list(map(lambda show: {
        "venue_id": show.vid,
        "venue_name": show.venue.name,
        "artist_id": show.aid,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
    }, _shows))
    # displays list of shows at /shows
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    get = request.form.get

    if not form.validate():
        flash(form.errors)
        return render_template('forms/new_show.html', form=form)
    try:
        show = Show(
            aid=get("artist_id"),
            vid=get("venue_id"),
            start_time=get("start_time")
        )
        db.session.add(show)
        db.session.commit()
    except psycopg2.errors.ForeignKeyViolation:
        flash("Didn't find either an artist or venue with such id...")
        return render_template('forms/new_show.html', form=form)
    except Exception as e:
        flash(e)
        return render_template('forms/new_show.html', form=form)
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return redirect("/shows")


@app.route('/shows/search', methods=['POST'])
def search_shows():
    term = request.form.get('search_term')
    raw = Show.query.all()
    data = list(map(lambda show: {
        "artist_name": show.artist.name,
        "venue_name": show.venue.name,
        "start_time": str(show.start_time),
        "artist_id": show.aid,
        "venue_id": show.vid
    }, list(filter(
        lambda show: re.search(term, show.artist.name + " " + show.venue.name, re.IGNORECASE)
        , raw))))
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_shows.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
