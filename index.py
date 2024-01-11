import json
from os import environ, makedirs, path, listdir
from onepush import notify
from ZZU_API.logger import logger
from ZZU_API.api import ZZU_API
from ZZU_API.utils import get_today_date_str

THRESHOLD = 5.0
JSON_FOLDER_PATH = "./page/data"

def notify_admin(title, content):
    if "ZZU_NOTIFIER" not in environ:
        return
    notifier, key = environ["ZZU_NOTIFIER"].split("#")
    if not notifier or not key:
        logger.info("No notification method configured ...")
        return
    logger.info("Preparing to send notification ...")
    result: dict = json.loads(notify(notifier, key=key, title=title, content=content).text)
    if result.get("code") == 200:
        logger.info(f"Message delivered to user ...")

def get_energy_balance_with_api() -> float:
    api = ZZU_API()
    api.token_check(refresh_all=False)
    return float(api.get_energy_balance())

def load_data_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def dump_data_into_json(data, file_path, **kwargs):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, **kwargs)

def record_data(data: dict | list) -> list[dict] | None:
    file_path = f"{JSON_FOLDER_PATH}/{get_today_date_str('%Y-%m')}.json"
    result = []

    try:
        result = load_data_from_json(file_path)
        if result[-1]["balance"] == data["balance"]:
            return result
    except FileNotFoundError:
        makedirs(path.dirname(file_path), exist_ok=True)
        result = [data]
        dump_data_into_json(result, file_path, indent=4)
        return result
    
    result.append(data)
    dump_data_into_json(result, file_path, indent=4)
    return result

def update_time_list() -> list[str]:
    if not path.exists(JSON_FOLDER_PATH):
        raise FileNotFoundError(f"The specified folder path '{JSON_FOLDER_PATH}' does not exist.")
    
    all_files = listdir(JSON_FOLDER_PATH)
    json_files = [path.splitext(file)[0] for file in all_files if not file.startswith("l")]
    json_files.reverse()

    with open("./page/time.json", "w", encoding="utf-8") as file:
        json.dump(json_files, file)

    return json_files

def parse_and_update_data(existing_data):
    MAX_DISPLAY_NUM = 30
    time_file_list = update_time_list()
    existing_data_length = len(existing_data)

    if existing_data_length < MAX_DISPLAY_NUM: 
        if len(time_file_list) > 1:
            records_to_retrieve = MAX_DISPLAY_NUM - existing_data_length
            last_month_data = load_data_from_json(file_path=f"{JSON_FOLDER_PATH}/{time_file_list[1]}.json")
            if records_to_retrieve > len(last_month_data):
                records_to_retrieve = len(last_month_data)
            existing_data = last_month_data[:records_to_retrieve] + existing_data
    else:
        existing_data = existing_data[-MAX_DISPLAY_NUM:]

    dump_data_into_json(existing_data, file_path=f"{JSON_FOLDER_PATH}/last_30_records.json")


if __name__ == "__main__":
    balance = get_energy_balance_with_api()

    if balance <= THRESHOLD:
        notify_admin(title="⚠️宿舍电量预警⚠️", content=f"当前宿舍剩余电量低，为{balance}度。")
    
    data = record_data({"time": get_today_date_str("%m-%d %H:%M:%S"), "balance": balance})
    parse_and_update_data(data)
