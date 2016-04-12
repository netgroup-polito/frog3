'''
Created on May 16, 2014

@author: fmignini
'''


from sqlalchemy import func

from keystone.common import config
from keystone.common import sql
from keystone.contrib import user_profile
from keystone.openstack.common import log

from keystone import exception



CONF = config.CONF
LOG = log.getLogger(__name__)


class UserProfile(sql.ModelBase, sql.ModelDictMixin):
    __tablename__ = 'user_profile'
    attributes = ['user_id', 'timestamp', 'graph']
    
    user_id = sql.Column(sql.String(64), primary_key=True, nullable=False)
    timestamp = sql.Column(sql.TimeStamp, primary_key=True, nullable=False)
    graph = sql.Column(sql.JsonBlob(), nullable=False)
   

class User_Profile(user_profile.Driver):
    
    @sql.handle_conflicts(conflict_type='user_profile')
    def create_user_profile(self,context, user_id, profile):
        
        """
        id_user = uuid.uuid4().hex
        """
        LOG.info("Create user profile")                
       
        session = sql.get_session()
        
        user_profile_ref = session.query(UserProfile).order_by(UserProfile.timestamp.desc())
        query = user_profile_ref.filter_by(user_id=user_id)
        last_user_profile_ref = query.first()
        trans = session.begin()
        try:
            # Delete previous profile
            user_profile_ref = session.query(UserProfile).order_by(UserProfile.timestamp.desc())
            query = user_profile_ref.filter_by(user_id=user_id)
            last_user_profile_ref = query.first()
            if last_user_profile_ref is not None:
                session.delete(last_user_profile_ref)
                LOG.info("User profile of "+user_id+" deleted:")
                LOG.info(last_user_profile_ref.to_dict())
            
            # Create new profile
            ref = {}
            ref['user_id'] = user_id
            ref['graph'] = { 'profile' : profile }
            profile_ref = UserProfile.from_dict(ref)
            session.add(profile_ref)
            LOG.info("Profile of "+user_id+" created:")
            LOG.info(profile_ref.to_dict())  
            trans.commit()
        except:
            trans.rollback()
            LOG.info("User profile of "+user_id+" ROLLBACK")
            raise
        return profile_ref.to_dict()
    
    """
    @sql.handle_conflicts(conflict_type='user_profile')
    def update_last_user_profile(self , user_id, profile):
        session = sql.get_session()
        if 'user_id' in profile and user_id != profile['user_id']:
            raise exception.ValidationError(_('Cannot change user_id'))
        try:
            ref = session.query(func.max(UserProfile.timestamp)).filter_by(user_id=user_id).one()
            LOG.info("update")
            LOG.info(ref)
            ref = session.query(UserProfile).filter_by(timestamp=ref[0]).filter_by(user_id=user_id).update({"graph":{"profile" : profile}}, synchronize_session = False)
            LOG.info("valore di ritorno update")
            LOG.info(ref)
            LOG.info("tipo ref")
            LOG.info(type(ref))
        except:
            raise
        return profile 
    """    
    
    def _delete_last_user_profile(self, user_id, session):
        pass
        
    
    def delete_last_user_profile(self, user_id):
        LOG.info("DELETE user profile")
        session = sql.get_session()
        user_profile_ref = session.query(UserProfile).order_by(UserProfile.timestamp.desc())
        query = user_profile_ref.filter_by(user_id=user_id)
        last_user_profile_ref = query.first()
        if last_user_profile_ref is None:
            raise exception.NotFound(_('User profile not found'))
        with session.begin():
            session.delete(last_user_profile_ref)
            LOG.info("User profile of "+user_id+" deleted:")
            LOG.info(last_user_profile_ref.to_dict())

    
    def get_last_user_profile(self, user_id):
        LOG.info("GET user profile")
        session = sql.get_session()
        user_profile_ref = session.query(UserProfile).order_by(UserProfile.timestamp.desc())
        if user_profile_ref is None:
            LOG.info("User profile of "+user_id+" not found")
            raise exception.NotFound(_('User profile not found'))
        
        query = user_profile_ref.filter_by(user_id=user_id)
        
        refs = query.all() 
        if len(refs) == 0 :
            LOG.info("User profile of "+user_id+" not found")
            raise exception.NotFound(message = "User profile not found")  
        
        return refs[0].to_dict()