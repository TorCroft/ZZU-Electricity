from ZZU_API.utils import load_data_from_json


MD_TEMPLATE = '''
## Balance Record
| **Record Time** | **Balance** |
| --------------- | ----------- |
| {time}  |    {balance}    |
'''

if __name__ == "__main__":
    latest_record = load_data_from_json("./page/data/last_30_records.json")[-1]
    time = latest_record["time"]
    balance = latest_record["balance"]
    print(MD_TEMPLATE.format(**latest_record))
