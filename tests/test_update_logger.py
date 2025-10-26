from unittest.mock import Mock

from bot.dispatcher import Dispatcher
from bot.handlers.update_database_logger import UpdateDatabaseLogger
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger

from tests.mock import Mock


def test_update_database_logger_execution():
    """Test that UpdateDatabaseLogger handler executes and calls persist_update with correct update."""

    # 1. Create JSON with telegram update with simple text message
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 12345,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1640995200,
            "text": "Hello, this is a test message",
        },
    }

    # 2. Init mock storage and stub necessary methods
    mock_storage = Mock(spec=Storage)
    mock_storage.get_user.return_value = {"state": "idle", "data": "{}"}
    mock_storage.persist_update = Mock()

    # 3. Init mock messenger
    mock_messenger = Mock(spec=Messenger)

    # 4. Init dispatcher and add UpdateDatabaseLogger handler
    dispatcher = Dispatcher(mock_storage, mock_messenger)
    update_logger = UpdateDatabaseLogger()
    dispatcher.add_handlers(update_logger)

    # 5. Dispatch the test message
    dispatcher.dispatch(test_update)

    # 6. Assert that UpdateDatabaseLogger was executed and persist_update was called with correct update
    mock_storage.persist_update.assert_called_once_with(test_update)

    # Additional assertions to verify handler behavior
    assert (
        update_logger.can_handle(test_update, "idle", {}, mock_storage, mock_messenger)
        is True
    ), "UpdateDatabaseLogger should always return True for can_handle"
