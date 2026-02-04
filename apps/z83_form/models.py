from common.extensions import db
from datetime import datetime

class Z83Form(db.Model):
    # This magic line puts it in 'z83.db' instead of 'shared_users.db'
    __bind_key__ = 'z83'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_name = db.Column(db.String(100))
    
    # We store the entire form submission as a JSON blob
    # This allows flexible schema (if the government adds a field, we don't need a migration)
    form_data = db.Column(db.JSON)