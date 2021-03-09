# https://maelfabien.github.io/project/Streamlit/#requirements
FROM python:3.8
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run src/app.py --server.port $PORT

# new container on google cloud:
# gcloud builds submit --tag gcr.io/PROJECT-ID/CONTAINER-NAME
# gcloud run deploy --image gcr.io/PROJECT-ID/helloworld --platform managed