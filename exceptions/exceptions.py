class DuplicateVideoError(Exception):
    """Raised when an existing video is added to a user again"""
    
class MissingVideoError(Exception):
    """Raised when trying to update (not access) a missing video"""

class MissingUserError(Exception):
    """Raised when trying to access player that does not exist"""