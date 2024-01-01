import json
from os import environ, makedirs, path, listdir
from onepush import notify
from ZZU_API.logger import logger
from ZZU_API.api import ZZU_API
from ZZU_API.utils import get_today_date_str

THRESHOLD = 5.0

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


def record_data(data: dict | list):
    filepath = f"./page/data/{get_today_date_str('%Y-%m')}.json"
    result = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            result = json.load(file)
            if result[-1]["balance"] == data["balance"]:
                return
    except FileNotFoundError:
        makedirs(path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump([data], file, ensure_ascii=False, indent=4)
        return
    result.append(data)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

def update_time_list():
    folder_path = "./page/data"
    if not path.exists(folder_path):
        raise FileNotFoundError(f"The specified folder path '{folder_path}' does not exist.")
    all_files = listdir(folder_path)
    json_files = [path.splitext(file)[0] for file in all_files if file.endswith('.json')]
    json_files.reverse()
    with open("./page/time.json", "w", encoding="utf-8") as file:
        json.dump(json_files, file)

if __name__ == "__main__":
    balance = get_energy_balance_with_api()
    if balance <= THRESHOLD:
        notify_admin(title="⚠️宿舍电量预警⚠️", content=f"当前宿舍剩余电量低，为{balance}度。")
    record_data({"time": get_today_date_str("%Y-%m-%d %H:%M:%S"), "balance": balance})
    update_time_list()
