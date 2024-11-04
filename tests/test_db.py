import uuid
import json
import pytest

from flou.database import get_db
from flou.database.models import Error
from .test_ltm import Child


def test_log_retry(session):
    db = get_db(session)

    ltm = Child()
    ltm_id = ltm.start()

    item_id = uuid.uuid4()
    reason = 'Test reason'
    item = {'key': 'value'}

    # Cause an exception and catch it
    try:
        raise ValueError
    except Exception as e:
        db.log_retry(item_id, ltm_id, reason, item, e, retrying=True)

    # Now, check the Error table
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()

    assert error_record is not None
    assert error_record.id == item_id
    assert error_record.ltm_id == ltm_id
    assert error_record.reason == reason
    assert error_record.item == item
    assert error_record.retrying == True
    retries = error_record.retries
    assert len(retries) == 1

    retry = retries[0]
    assert 'time' in retry
    assert 'type' in retry
    assert 'description' in retry
    assert 'details' in retry
    assert retry['type'] == 'ValueError'

    try:
        raise ValueError
    except Exception as e:
        db.log_retry(item_id, ltm_id, reason, item, e, retrying=True)

    # Now, check the Error table
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()
    assert error_record is not None
    assert error_record.id == item_id
    assert error_record.ltm_id == ltm_id
    assert error_record.reason == reason
    assert error_record.item == item
    assert error_record.retrying == True
    retries = error_record.retries
    assert len(retries) == 2

    retry = retries[1]
    assert 'time' in retry
    assert 'type' in retry
    assert 'description' in retry
    assert 'details' in retry
    assert retry['type'] == 'ValueError'

    assert retries[0]['time'] != retries[1]['time']

def test_set_error(session):

    db = get_db(session)
    item_id = uuid.uuid4()

    ltm = Child()
    ltm_id = ltm.start()


    # create an Error
    try:
        raise ValueError
    except Exception as e:
        db.log_retry(item_id, ltm_id, 'execute', {}, e, retrying=True)

    # check the Error table for retrying
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()
    assert error_record.retrying == True

    # set the error
    db.set_stop_retrying(item_id)

    # check the Error table for retrying
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()
    assert error_record.retrying == False

def test_set_success(session):

    db = get_db(session)
    item_id = uuid.uuid4()

    ltm = Child()
    ltm_id = ltm.start()

    # create an Error
    try:
        raise ValueError
    except Exception as e:
        db.log_retry(item_id, ltm_id, 'execute', {}, e, retrying=True)

    db.set_success(item_id)

    # check the Error table for retrying
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()
    assert error_record.retrying == False
    assert error_record.success == True

def test_set_retrying(session):

    db = get_db(session)
    item_id = uuid.uuid4()

    ltm = Child()
    ltm_id = ltm.start()

    # create an Error
    try:
        raise ValueError
    except Exception as e:
        db.log_retry(item_id, ltm_id, 'execute', {}, e, retrying=False)

    db.set_retrying(item_id)

    # check the Error table for retrying
    error_record = session.query(Error).filter_by(id=item_id).one_or_none()
    assert error_record.retrying == True