from app import *

#----------------------------------------------------------------------------#
# Add dummy data to database from data file EXECUTE ON FIRST RUN ONLY
#----------------------------------------------------------------------------#

# Adding dummy data to Venue

db.session.add(Venue(**venue_1)) 
db.session.add(Venue(**venue_2))
db.session.add(Venue(**venue_3))

# Adding dummy data to Artist

db.session.add(Artist(**Artist_1))
db.session.add(Artist(**Artist_2))
db.session.add(Artist(**Artist_3))

# Adding dummy data to Shows

db.session.add(Shows(**shows_1)) 
db.session.add(Shows(**shows_2))
db.session.add(Shows(**shows_3_1))
db.session.add(Shows(**shows_3_2))

# Commiting changes

db.session.commit()

# Closing Session

db.session.close()