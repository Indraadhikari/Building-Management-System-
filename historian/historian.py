import os
import asyncio
import pandas
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from graphene import ObjectType, String, Float, List, Field, Schema
from influxdb_client import InfluxDBClient

# influxdb variables
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("ORG")
BUCKET = os.getenv("BUCKET")

# Initialize InfluxDB client
try:
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = influx_client.query_api()
except Exception as e:
    print(f"InfluxDB client initialization failed: {e}")
    exit(1)

# Graphene Object Types
class DataPoint(ObjectType):
    time = String()
    sensor_id = String()
    temperature = Float()
    humidity = Float()
    energy_kwh = Float()

class AggregatedDataPoint(ObjectType):
    time = String()
    sensor_id = String()
    temperature_f = Float()

# Graphene Query Type
class Query(ObjectType):
    raw_data = List(DataPoint, sensor_id=String(required=True))
    aggregated_data = List(AggregatedDataPoint, sensor_id=String(required=True))

    def resolve_raw_data(self, info, sensor_id):
        flux_query = f'''
            from(bucket: "{BUCKET}")
              |> range(start: -5h)
              |> filter(fn: (r) => r._measurement == "raw_data" and r.sensor_id == "{sensor_id}")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> keep(columns: ["_time", "sensor_id", "temperature", "humidity", "energy_kwh"])
        '''
        try:
            result_df = query_api.query_data_frame(query=flux_query)
            return [
                DataPoint(
                    time=str(row["_time"]),
                    sensor_id=row.get("sensor_id"),
                    temperature=row.get("temperature"),
                    humidity=row.get("humidity"),
                    energy_kwh=row.get("energy_kwh")
                ) for _, row in result_df.iterrows()
            ] if not result_df.empty else []
        except Exception as e:
            print(f"Error in resolve_raw_data: {e}")
            return []

    def resolve_aggregated_data(self, info, sensor_id):
        flux_query = f'''
            from(bucket: "{BUCKET}")
              |> range(start: -5h)
              |> filter(fn: (r) => r._measurement == "aggregated_data" and r.sensor_id == "{sensor_id}")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> keep(columns: ["_time", "sensor_id", "temperature_f"])
        '''
        try:
            result_df = query_api.query_data_frame(query=flux_query)
            return [
                AggregatedDataPoint(
                    time=str(row["_time"]),
                    sensor_id=row.get("sensor_id"),
                    temperature_f=row.get("temperature_f")
                ) for _, row in result_df.iterrows()
            ] if not result_df.empty else []
        except Exception as e:
            print(f"Error in resolve_aggregated_data: {e}")
            return []

schema = Schema(query=Query)

# FastAPI Application
app = FastAPI(title="Building Automation GraphQL API")

@app.post("/graphql")
async def graphql_endpoint(request: Request):
    payload = await request.json()
    query_str = payload.get("query")
    if not query_str:
        return JSONResponse(content={"errors": [{"message": "Query not provided"}]}, status_code=400)
    result = await asyncio.to_thread(schema.execute, query_str)
    return JSONResponse(content={"data": result.data} if result.data else {"errors": [err.formatted for err in result.errors]}, status_code=200)

@app.get("/health")
async def health_check():
    try:
        if influx_client.ping():
            return {"status": "ok", "influxdb_connection": "healthy"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 503

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("historian:app", host="0.0.0.0", port=8088, reload=True)