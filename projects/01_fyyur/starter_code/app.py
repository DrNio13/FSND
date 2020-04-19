# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import func, text, update, or_
import dateutil.parser
import babel
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
print("-----connected to db------")


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = "Show"

    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "Show(%s, %s)" % (self.venue_id, self.artist_id)


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship(
        "Artist",
        secondary=Show.__table__,
        backref="venues",
        single_parent=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return "Venue(%s, %s)" % (self.id, self.name)


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return "Artist(%s, %s)" % (self.id, self.name)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, locale="en_US")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    all_areas = (
        Venue.query.with_entities(Venue.city, Venue.state)
        .group_by(Venue.city, Venue.state)
        .all()
    )
    data = []
    for area in all_areas:
        venues_in_city = (
            Venue.query.filter(Venue.city == area[0])
            .filter(Venue.state == area[1])
            .all()
        )
        data.append({"city": area.city, "state": area.state, "venues": venues_in_city})

    return render_template("pages/venues.html", areas=data)


# Find venue by name, city, state
@app.route("/venues/search", methods=["POST"])
def search_venues():
    searchTerm = request.form.get("search_term", "")
    search = "%{}%".format(searchTerm)
    data = Venue.query.filter(
        or_(
            Venue.name.ilike(search),
            Venue.city.ilike(search),
            Venue.state.ilike(search),
        )
    ).all()
    count = len(data)
    response = {"count": count, "data": data}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

    now = datetime.utcnow()
    venue.upcoming_shows = (
        db.session.query(Show)
        .join(Venue, Show.venue_id == Venue.id)
        .filter(Show.venue_id == venue_id, Show.start_time > now)
        .all()
    )
    venue.upcoming_shows_count = len(venue.upcoming_shows)
    venue.past_shows = (
        db.session.query(Show)
        .join(Venue, Show.venue_id == Venue.id)
        .filter(Show.venue_id == venue_id, Show.start_time < now)
        .all()
    )
    venue.past_shows_count = len(venue.past_shows)

    return render_template("pages/show_venue.html", venue=venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    response = {}
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        facebook_link = request.form.get("facebook_link")
        genres = request.form.getlist("genres")
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
        )
        response["name"] = venue.name
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Venue " + response["name"] + " was successfully listed!")
        else:
            flash(
                "An error occurred. Venue "
                + request.form["name"]
                + " could not be listed."
            )
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            return jsonify({"success": True})
        return jsonify({"success": False})


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = Artist.query.all()

    return render_template("pages/artists.html", artists=artists)


# Find artist by name, city, state
@app.route("/artists/search", methods=["POST"])
def search_artists():
    searchTerm = request.form.get("search_term", "")
    search = "%{}%".format(searchTerm)
    data = Artist.query.filter(
        or_(
            Artist.name.ilike(search),
            Artist.city.ilike(search),
            Artist.state.ilike(search),
        )
    ).all()
    count = len(data)
    response = {"count": count, "data": data}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    now = datetime.utcnow()
    artist.upcoming_shows = (
        db.session.query(Show)
        .join(Artist, Show.artist_id == artist_id)
        .filter(Show.artist_id == artist_id, Show.start_time > now)
        .all()
    )
    if len(artist.upcoming_shows):
        artist.upcoming_shows_count = len(artist.upcoming_shows)
    artist.past_shows = (
        db.session.query(Show)
        .join(Artist, Show.artist_id == Artist.id)
        .filter(Show.artist_id == artist_id, Show.start_time < now)
        .all()
    )
    if len(artist.past_shows):
        artist.past_shows_count = len(artist.past_shows)

    print(artist.genres)

    return render_template("pages/show_artist.html", artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()

    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO check genres to be array in db
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")

        sql = (
            update(Artist)
            .where(Artist.id == artist_id)
            .values(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                facebook_link=facebook_link,
            )
        )
        db.engine.execute(sql)
    except:
        error = True
        flash("Error while updating artist " + request.form.get("name"))
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Artist was updated " + request.form.get("name") + " successfully!")

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")

        sql = (
            update(Venue)
            .where(Venue.id == venue_id)
            .values(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                facebook_link=facebook_link,
            )
        )
        db.engine.execute(sql)
    except:
        error = True
        flash("Error while updating venue " + request.form.get("name"))
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Venue was updated " + request.form.get("name") + " successfully!")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    response = {}
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
        )
        response["name"] = artist.name
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        flash("An error occurred. Artist " + name + " could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Artist " + response["name"] + " was successfully listed!")

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    sql = text(
        """select "Venue".id as venue_id, "Venue".name as venue_name, 
        "Artist".id as artist_id, "Artist".name as artist_name, 
        "Artist".image_link as artist_image_link, 
        "Show".start_time as start_time from "Venue" inner join "Show" on "Venue".id="Show".venue_id 
        inner join "Artist" on "Artist".id="Show".artist_id"""
    )
    results = db.engine.execute(sql)

    data = list()
    for result in results:
        data.append(result)

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    error = False
    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Show was successfully listed!")
        else:
            flash("An error occurred. Show could not be listed.")

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""

