from utils import get_status_from_code


def test_get_status_from_code():
    current_update_status = get_status_from_code(3)
    print(f"status received: {current_update_status.name}")
