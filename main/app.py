#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from imports import *
from models import *

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venue = db.session.query(Venue.city, Venue.state, Venue.name, Venue.id)
  for x in venue.all():
    num_upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==x.id).filter(Shows.startingTime>datetime.now()).all()
    data.append({
    'city': x.city,
    'state': x.state,
    'venues': [
    {'id': x.id,
    'name': x.name, 
    'num_upcoming_shows': len(num_upcoming_shows)},
    ]})
    

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  query = request.form.get('search_term', '')
  search = (db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(f"%{query}%")).all())
  rslts = []
  for x in search:
    num_upcoming_shows = num_upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==x.id).filter(Shows.startingTime>datetime.now()).all()
    rslts.append({
              "id": x.id,
              "name": x.name,
              "num_upcoming_shows": len(num_upcoming_shows),
            })

  response = {
  "count": len(search),
  "data": rslts
}
  if not search:
    response = {
    "count": "NOT FOUND",
    "data": [{
      "id": 0,
      "name": "NULL",
      "num_upcoming_shows": "NULL",
    }]
  } 
  return render_template('pages/search_venues.html', results=response, search_term=query)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcmingshows = 0
  pstshows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==venue_id).filter(Shows.startingTime<datetime.now()).all()
  artst_id = None
  upcmingshows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==venue_id).filter(Shows.startingTime>datetime.now()).all()
      
  venue = db.session.query(Venue.name, 
                           Venue.id,
                           Venue.genres,
                           Venue.image_link, 
                           Venue.phone, 
                           Venue.state, 
                           Venue.website,
                           Venue.seeking_talent, 
                           Venue.seeking_description, 
                           Venue.facebook_link, 
                           Venue.city,
                           Venue.address).filter_by(id = venue_id).all()
  for x in venue:
    data = {
            'name': x.name, 
            'id': x.id,
            'genres': x.genres,
            'image_link': x.image_link, 
            'phone': x.phone, 
            'state': x.state, 
            'website': x.website,
            'seeking_talent': x.seeking_talent, 
            'seeking_description': x.seeking_description, 
            'facebook_link': x.facebook_link,
            'address': x.address, 
            'city': x.city,
            'upcoming_shows_count': len(upcmingshows),
            'upcoming_shows': upcmingshows,
            'past_shows_count': len(pstshows),
            'past_shows': pstshows
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    form = VenueForm(request.form)
    if form.seeking_talent.data == "y":
      form.seeking_talent.data = True
    else:
      form.seeking_talent.data = False
    venue = Venue(
                  name=form.name.data, 
                  city=form.city.data, 
                  state=form.state.data, 
                  address=form.address.data, 
                  phone=form.phone.data, 
                  genres=form.genres.data, 
                  facebook_link=form.facebook_link.data, 
                  image_link=form.image_link.data, 
                  website=form.website_link.data, 
                  seeking_talent=form.seeking_talent.data, 
                  seeking_description=form.seeking_description.data
                  )

    db.session.add(venue)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
# on successful db insert, flash success
      if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      else:
        flash('Please try again, ' + venue.name + ' could not be listed')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    delete = Venue.query.get(venue_id)
    db.session.delete(Venue.query.get(venue_id))
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash(delete.name + ' successfuly deleted!')
    else:
      flash('Could not delete the Venue, please try again later.')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name).all()
  data = []
  for x in artists:
    data.append({
      'id': x.id,
      'name': x.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  query = request.form.get('search_term', '')
  search = (db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(f"%{query}%")).all())
  
  rslts = []
  for x in search:
      num_upcoming_shows = num_upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.artist_id==x.id).filter(Shows.startingTime>datetime.now()).all()
      rslts.append({
        'id': x.id,
        'name': x.name,
        'num_upcoming_shows': num_upcoming_shows
      })
  response={
    "count": len(search),
    "data": rslts
  }
  if not search:
    response={
      "count": 'Could not find any match',
      "data": [{
        "id": 'NULL',
        "name": "NULL",
        "num_upcoming_shows": 0,
      }]
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

 # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcmingshows = db.session.query(Shows).join(Artist).filter(Shows.artist_id==artist_id).filter(Shows.startingTime>datetime.now()).all()
  pstshows = db.session.query(Shows).join(Artist).filter(Shows.artist_id==artist_id).filter(Shows.startingTime<datetime.now()).all()
      
  Artists = db.session.query(Artist.name, 
                           Artist.id,
                           Artist.genres,
                           Artist.image_link, 
                           Artist.phone, 
                           Artist.state, 
                           Artist.website,
                           Artist.seeking_venue, 
                           Artist.seeking_description, 
                           Artist.facebook_link, 
                           Artist.city).filter_by(id = artist_id).all()
  for x in Artists:
    data = {
            'name': x.name, 
            'id': x.id,
            'genres': x.genres,
            'image_link': x.image_link, 
            'phone': x.phone, 
            'state': x.state, 
            'website': x.website,
            'seeking_talent': x.seeking_venue, 
            'seeking_description': x.seeking_description, 
            'facebook_link': x.facebook_link, 
            'city': x.city,
            'upcoming_shows_count': len(upcmingshows),
            'upcoming_shows': upcmingshows,
            'past_shows_count': len(pstshows),
            'past_shows': pstshows
          }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artists = Artist.query.get(artist_id)
  form = ArtistForm(obj=artists)
  if request.method == 'GET' and form.validate():
    form.populate_obj(artists)
    # TODO: populate form with fields from artist with ID <artist_id>
  
  return render_template('forms/edit_artist.html', form=form, artist=artists)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  genresList = []
  error = False
  try:
    form = ArtistForm(request.form)
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    if form.seeking_venue.data == 'y':
      artist.seeking_venue = True
      artist.seeking_description = form.seeking_description.data
    else:
      artist.seeking_venue = False
      artist.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash("Artist page edited sucessfully!")
    else:
      flash("There was an error, please try again!")
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  genresList = []
  error = False
  try:
    form = ArtistForm(request.form)
    if form.seeking_venue.data == 'y':
      form.seeking_venue.data = True
    else:
      form.seeking_venue.data = False

    artist = Artist(
                   name=form.name.data, 
                   city=form.city.data, 
                   state=form.state.data, 
                   phone=form.phone.data, 
                   genres=form.genres.data, 
                   facebook_link=form.facebook_link.data, 
                   image_link=form.image_link.data, 
                   website=form.website_link.data, 
                   seeking_venue=form.seeking_venue.data, 
                   seeking_description=form.seeking_description.data
                   )
    db.session.add(artist)
    db.session.commit()
  except:
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occured, '+ request.form['name'] + ' could not be listed, try again later.')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  zipped = zip(db.session.query(Shows.startingTime, Shows.venue_id, Shows.artist_id).all(), db.session.query(Artist.image_link).all())
  for x, t in zipped:
    if not (x.startingTime is None and x.artist_id is None):
      data.append({
      "venue_id": x.venue_id,
      "venue_name": db.session.query(Venue.name).filter_by(id = x.venue_id).all(),
      "artist_id": x.artist_id,
      "artist_name": db.session.query(Artist.name).filter_by(id = x.artist_id).all(),
      "artist_image_link": t.image_link,
      "start_time": str(x.startingTime)
    })
    else:
      data.append({
      "venue_id": x.venue_id,
      "venue_name": db.session.query(Venue.name).filter_by(id = x.venue_id).all(),
      "artist_id": 5,
      "artist_name": db.session.query(Artist.name).filter_by(id = 5).all(),
      "artist_image_link": t.image_link,
      "start_time": str(datetime.utcnow())
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    form = ShowForm(request.form)
    shows = Shows(
                  artist_id=form.artist_id.data, 
                  venue_id=form.venue_id.data, 
                  startingTime=format_datetime(form.start_time.data, format='medium')
                  )
    db.session.add(shows)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash('Show was successfully listed!')
    else:
      flash('Show could not be listed, please try again')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)
  

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
