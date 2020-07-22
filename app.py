#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from sqlalchemy.orm import aliased

import sys
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.order_by(Venue.state, Venue.city).all()
  data=[]
  # venues=Venue.query.all()
  area={}
  city=None
  state=None
  for venue in venues:
    
    shows=len(Show.query.filter(Show.venue_id==venue.id,Show.start_time >= datetime.today()).all())
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': shows
    }
    if venue.city == city and venue.state == state:
      area['venues'].append(venue_data)
    else:
      data.append(area)
      area['city'] = venue.city
      area['state'] = venue.state
      area['venues'] = [venue_data]
    city = venue.city
    state = venue.state

    data.append(area)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
      res = {}
      res['id'] = venue.id
      res['name'] = venue.name
      res['num_upcoming_shows'] = len(venue.shows)
      data.append(res)

  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  past_shows = Artist.query.join(Show,Artist.id==Show.artist_id).\
    add_columns(Show.start_time,Artist.name,Artist.image_link).\
    filter(Show.venue_id==venue_id,Show.start_time<datetime.today()).all()
  upcoming_shows = Artist.query.join(Show,Artist.id==Show.artist_id).\
    add_columns(Show.start_time,Artist.name,Artist.image_link).\
    filter(Show.venue_id==venue_id,Show.start_time>=datetime.today()).all()

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website":venue.website_link,
    "facebook_link":venue.facebook_link,
    "seek_out":venue.seek_out,
    "image_link": venue.image_link,
  }
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
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

  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website_link = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seek_out = form.seek_out.data,
    image_link = form.image_link.data,
  )
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

# Delete venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

# Edit venue
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.filter_by(id=venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  venue=Venue.query.filter_by(id=venue_id).first()
  venue.name = form.name.data
  venue.genres = form.genres.data
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.website_link = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.seek_out = form.seek_out.data
  venue.image_link = form.image_link.data
  try:
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for artist in artists:
      res = {}
      res['id'] = artist.id
      res['name'] = artist.name
      res['num_upcoming_shows'] = len(artist.shows)
      data.append(res)

  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  past_shows = Artist.query.join(Show,Artist.id==Show.artist_id).\
    add_columns(Show.start_time,Artist.name,Artist.image_link).\
    filter(Show.artist_id==artist_id,Show.start_time<datetime.today()).all()
  upcoming_shows = Artist.query.join(Show,Artist.id==Show.artist_id).\
    add_columns(Show.start_time,Artist.name,Artist.image_link).\
    filter(Show.artist_id==artist_id,Show.start_time>=datetime.today()).all()

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website_link,
    "facebook_link":artist.facebook_link,
    "seek_out":artist.seek_out,
    "image_link": artist.image_link,
  }
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.filter_by(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist=Artist.query.filter_by(id=artist_id).first()
  artist.name = form.name.data
  artist.genres = form.genres.data
  artist.address = form.address.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.website_link = form.website_link.data
  artist.facebook_link = form.facebook_link.data
  artist.seek_out = form.seek_out.data
  artist.image_link = form.image_link.data
  try:
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  artist = Artist(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website_link = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seek_out = form.seek_out.data,
    image_link = form.image_link.data,
  )
  try:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
      flash('An error occurred. Artist ' + form.name.data + ' could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
      show = {
          "venue_id": show.venue_id,
          "venue_name": db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0],
          "artist_id": show.artist_id,
          "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0],
          "start_time": str(show.start_time)
      }
      data.append(show)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form=ShowForm(request.form)
  show = Show(
    artist_id=form.artist_id.data,
    venue_id=form.venue_id.data,
    start_time=form.start_time.data
  )
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show  was successfully listed!')
  except:
      flash('An error occurred. Show could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
