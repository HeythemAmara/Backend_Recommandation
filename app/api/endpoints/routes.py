from fastapi import APIRouter, HTTPException, Request, Body

from app.services.primini_service import get_primini_data, get_specific_range_primini_data
from app.services.product_service import get_180_csv_data
from app.services.filter_service import api_filters, api_primini_filters, update_counts_with_filters
from app.services.csv_service import read_scrapping_csv_data, read_primini_csv_data
from app.services.filter_service import api_filters_update, api_filters_primini_update
from pydantic import BaseModel
from typing import List

router = APIRouter()


class FilterRequest(BaseModel):
    priceRange: List[int]
    status: List[str]
    offer: List[str]
    ram: List[str]
    stockage: List[str]
    shop: List[str]
    marque: List[str]
    color: List[str]


@router.get("/read-csv")
async def read_csv():
    try:
        data = get_180_csv_data(read_scrapping_csv_data())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PriminiDataRequest(BaseModel):
    start: int


@router.post("/read-primini")
async def read_primini(request: PriminiDataRequest = Body(...)):
    try:
        data = get_specific_range_primini_data(request.start, read_primini_csv_data())
        print(len(read_primini_csv_data()))
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter-csv")
async def filter_csv():
    try:
        data = api_filters(read_scrapping_csv_data())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter-primini-csv")
async def filter_csv():
    try:
        data = api_primini_filters(get_primini_data(read_primini_csv_data()))
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filter-primini-update")
async def filter_primini_update(request: Request):
    try:
        filters = await request.json()
        selected_filter_value = filters[0]
        old_filter_value = filters[1]
        rawdata = get_primini_data(read_primini_csv_data())
        filtered_data = api_filters_primini_update(rawdata, selected_filter_value)
        exif = api_primini_filters(get_primini_data(read_primini_csv_data()))
        newfilters = update_counts_with_filters(rawdata, selected_filter_value, old_filter_value, exif)
        print("HERE old_filter_value\t", old_filter_value)
        print("HERE newfilters      \t", newfilters)
        result = {
            'filtered_data': filtered_data,
            'newfilters': newfilters
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filter-update")
async def filter_update(request: Request):
    try:
        filters = await request.json()
        df = read_scrapping_csv_data()
        filtered_data = api_filters_update(df, filters)
        data = get_180_csv_data(filtered_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def filter_csv():
    try:
        data =get_primini_data(read_primini_csv_data())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
