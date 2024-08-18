from datetime import datetime, timedelta
import pytz
import json

def recursive_city_search(areas, city_name):
    for area in areas:
        if area['name'] == city_name:
            return area['id']
        if 'areas' in area and area['areas']:
            found_id = recursive_city_search(area['areas'], city_name)
            if found_id:
                return found_id
    return None

def get_datetime() -> str:
    timezone = pytz.timezone("UTC")
    two_days_ago = datetime.now(timezone) - timedelta(days=2)
    formatted_date = two_days_ago.isoformat()

    return formatted_date

def recursive_role_search(categories, role_name):
    for category in categories.get("categories", []):
        for role in category.get('roles', []):
            if role['name'] == role_name:
                return role['id']
    return None

# def sort_vacancies(vacancies):
#
#     def get_salary_from(vacancy):
#         salary = vacancy.get("salary")
#         if isinstance(salary, dict):
#             return salary.get("from") or float("inf")
#         return float("inf")
#
#     sorted_vacancies = sorted(vacancies.get("items", []), key=get_salary_from)
#     return json.dumps(sorted_vacancies, indent=4, ensure_ascii=False)