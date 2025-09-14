from utils.config_reader import config

groups = [
    {"name": "Balakshin_enjoyers", "id": -100, "sheets_per_day": 2, "password": config.balakshin_pass.get_secret_value()},
    {"name": "VT_pint_team", "id": -101, "sheets_per_day": 5, "password": config.vt_pass.get_secret_value()},
    {"name": "Prodmatbratva", "id": -102, "sheets_per_day": 10, "password": config.prodmat_pass.get_secret_value()},
    {"name": "Elite_group", "id": -103, "sheets_per_day": 50, "password": config.elite_pass.get_secret_value()},
    {"name": "Admin", "id": -104, "sheets_per_day": 1000000, "password": config.admin_pass.get_secret_value()},
]