from rest import db, Link

db.session.query(Link).delete()
db.session.commit()
