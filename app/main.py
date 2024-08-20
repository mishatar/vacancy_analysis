import json
from typing import List

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models import Vacancy
from app.services import recursive_city_search, get_datetime, recursive_role_search, upload_to_sheet
from aiohttp import ClientSession, ClientResponseError
from fastapi import FastAPI, HTTPException, Depends

from app.schemas import RequestModel, JobCreate, VacancyFilter, VacancyResponse

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


async def load_to_db(item: dict, session: AsyncSession):
    job_data = JobCreate(
        name=item["name"],
        alternate_url=item["alternate_url"],
        area_name=item["area"]["name"],
        professional_roles=item["professional_roles"][0]["name"],
        salary_from=(item.get("salary") or {}).get("from"),
        salary_to=(item.get("salary") or {}).get("to"),
    )

    db_job = Vacancy(**job_data.dict())
    session.add(db_job)
    await session.commit()
    await session.refresh(db_job)


@app.post("/upload_data")
async def send_data(request: RequestModel, session: AsyncSession = Depends(get_async_session)):
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
        for item in vacancies_response_data["items"]:
            await load_to_db(item, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data into Postgres: {str(e)}")

    try:
        upload_to_sheet(vacancies_response_data)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load data into table")

    return vacancies_response_data


@app.get("/get_vacancies_by_filter", response_model=List[VacancyResponse])
async def get_vacancies_by_filter(
    filter: VacancyFilter = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Vacancy)

    conditions = []
    if filter.name:
        conditions.append(Vacancy.name.ilike(f"%{filter.name}%"))
    if filter.area_name:
        conditions.append(Vacancy.area_name.ilike(f"%{filter.area_name}%"))
    if filter.professional_roles:
        conditions.append(Vacancy.professional_roles.ilike(f"%{filter.professional_roles}%"))
    if filter.min_salary is not None:
        conditions.append(Vacancy.salary_from >= filter.min_salary)
    if filter.max_salary is not None:
        conditions.append(Vacancy.salary_to <= filter.max_salary)

    if conditions:
        query = query.where(and_(*conditions))

    result = await session.execute(query)
    vacancies = result.scalars().all()
    return vacancies
