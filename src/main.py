import json
from src.services import recursive_city_search, get_datetime, recursive_role_search, upload_to_sheet
from aiohttp import ClientSession, ClientResponseError
from fastapi import FastAPI, HTTPException


from src.schemas import RequestModel

base_url = 'https://api.hh.ru'

app = FastAPI(title='Анализ вакансий')


async def fetch_data(url: str, params: dict = None) -> dict:
    async with ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as e:
            raise HTTPException(status_code=502, detail=f"Error while fetching data from {url}: {str(e)}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=502, detail=f"Error decoding JSON from {url}")

@app.post("/")
async def send_data(request: RequestModel):
    areas_response_data = await fetch_data(f'{base_url}/areas')
    role_response_data = await fetch_data(f'{base_url}/professional_roles')

    city_id = recursive_city_search(areas_response_data, request.city)
    if city_id is None:
        raise HTTPException(status_code=404, detail="City not found")

    role_id = recursive_role_search(role_response_data, request.professional_role)
    if role_id is None:
        raise HTTPException(status_code=404, detail="Professional role not found")

    cur_param = {
        "area": int(city_id),
        "professional_role": int(role_id),
        "date_from": get_datetime(),
        "order_by": "salary_asc",
        "currency": "RUR"
    }
    vacancies_response_data = await fetch_data(f'{base_url}/vacancies', cur_param)

    try:
        upload_to_sheet(vacancies_response_data)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load data into table")
    return vacancies_response_data
