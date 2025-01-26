#!/usr/bin/python3
# -*- coding: utf-8 -*-
# coding: utf8

"""
Copyright: © 2024-2025, Siarhei Straltsou
init release 2024-12-31
Simple API for synchronization weight and body data (calculated)
  from Xiaomi Mi Body Composition Scale 2 to Garmin Connect
"""
import copy
import logging
import uvicorn
import httpx
import json
import xiaomi_scale_body_metrics

from datetime import datetime, date

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from settings import settings


class User:
    def __init__(self, sex, height, birthdate, email, max_weight, min_weight):
        self.sex = sex
        self.height = height
        self.birthdate = birthdate
        self.email = email
        self.max_weight = max_weight
        self.min_weight = min_weight

    # Calculating age
    @property
    def age(self):
        today = date.today()
        calc_date = datetime.strptime(self.birthdate, '%d-%m-%Y')
        return today.year - calc_date.year


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get('/docs', include_in_schema=False)
async def get_swagger_documentation():
    return get_swagger_ui_html(openapi_url='/openapi.json', title='docs')


@app.get('/redoc', include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(openapi_url='/openapi.json', title='redoc')


@app.get('/openapi.json', include_in_schema=False)
async def openapi():
    return get_openapi(title=app.title, version=app.version, routes=app.routes)

@app.get('/update/')
async def update_weight_in_gc(weight: float = 0, impedance: int = 0):
    if settings.min_weight < weight < settings.max_weight:
        current_user = User(sex=settings.sex, height=settings.height, birthdate=settings.birth_date,
                            email=settings.gc_user, max_weight=settings.max_weight,
                            min_weight=settings.min_weight)
        data = {
            'weight': weight,
            'unix-timestamp': int(datetime.timestamp(datetime.now())*1000),
            'email': settings.gc_user,
            'password': settings.gc_pass
            }
        if impedance:
            lib = xiaomi_scale_body_metrics.bodyMetrics(weight, current_user.height, current_user.age, current_user.sex,
                                                        int(impedance))
            data['percentFat'] = lib.getFatPercentage()
            data['percentHydration'] = lib.getWaterPercentage()
            data['bonemass'] = lib.getBoneMass()
            data['muscleMass'] = lib.getMuscleMass()
            data['visceralFatRating'] = lib.getVisceralFat()
            data['physiqueRating'] = lib.getBodyType()
            data['metabolicAge'] = lib.getMetabolicAge()
            data['bodyMassIndex'] = lib.getBMI()

        logging.info(f'{current_user.email}, height: {current_user.height}, age: {current_user.age}')
        display_data = copy.deepcopy(data)
        try:
            display_data['password'] = '*' * len(display_data['password'])
        except Exception as e:
            display_data['password'] = '*' * 10
        try:
            display_data['datetime'] = datetime.fromtimestamp(display_data['unix-timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            display_data['datetime'] = '*' * 10
        logging.info(json.dumps(display_data, indent=2))

        async with httpx.AsyncClient() as client:
            try:
                rsp = await client.post(settings.gc_api, json=data,
                                        headers={'Content-Type': 'application/json'}, timeout=60)
                status_code = rsp.status_code
                logging.info(status_code)
                # rsp.raise_for_status()
            except httpx.HTTPError as e:
                logging.error(f'Error while requesting {e.request.url!r} - {e!r}')
    else:
        logging.warning(f'Unknown user with weight: {settings.min_weight} > {weight} > {settings.max_weight}')


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=settings.api_port, log_level='debug', reload=True,
                log_config='log.ini')
