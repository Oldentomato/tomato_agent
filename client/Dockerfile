FROM node:18.11.0-alpine
WORKDIR /app
ARG REACT_APP_DPR_ENDPOINT
ARG REACT_APP_SUMMARY_ENDPOINT

COPY . ./
RUN echo "REACT_APP_DPR_ENDPOINT=${REACT_APP_DPR_ENDPOINT}" >> .env
RUN echo "REACT_APP_SUMMARY_ENDPOINT=${REACT_APP_SUMMARY_ENDPOINT}" >> .env

RUN npm install 
RUN npm run build

RUN rm .env

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

