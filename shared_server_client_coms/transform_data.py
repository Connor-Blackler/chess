"""A module that converts a command and a digestable to transferable data"""
import pickle
import json
import base64
from shared_python.shared_hmac.hmac import Digestable
from .commands import Command

def get_transfer_data(this_command: Command, this_digestable: Digestable) -> str:
    """pickle the command, hmac and covert to a json string with:

    {
        digest:str
        digest_len:int
        data:str        
    }
    """
    pickled_data = pickle.dumps(this_command)
    digested_data = this_digestable.make_digest(pickled_data)

    return json.dumps({"digest":digested_data,
                       "digest_len":str(len(digested_data)),
                       "data":base64.b64encode(pickled_data).decode('ascii')})

def validate_data(data: dict, this_digestable: Digestable) -> bool:
    """Validate the data, ensuring the data has not been tampered with"""
    digest_data = data["digest"]
    pickled_data = base64.b64decode(data["data"])

    return this_digestable.make_digest(pickled_data) == digest_data
