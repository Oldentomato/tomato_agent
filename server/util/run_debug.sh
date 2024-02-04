#!/bin/bash

cd /
cd client
npm run start & # & = 두 프로세스를 돌리기 위함

cd ../server
uvicorn main.api.api:app --reload

