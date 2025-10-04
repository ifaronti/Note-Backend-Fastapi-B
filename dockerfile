FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# COPY prisma ${LAMBDA_TASK_ROOT}/prisma
# RUN prisma generate

COPY app ${LAMBDA_TASK_ROOT}/app
COPY .venv ${LAMBDA_TASK_ROOT}/.venv
COPY .env ${LAMBDA_TASK_ROOT}
COPY main.py ${LAMBDA_TASK_ROOT}
CMD ["main.handler"]