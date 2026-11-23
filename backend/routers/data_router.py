from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Parcel, Sensor, SensorData
from ..schemas import ParcelOut, SensorOut, SensorDataOut
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["Datos Agrícolas"])

@router.get("/parcels", response_model=List[ParcelOut])
def get_user_parcels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return db.query(Parcel).all()
    return db.query(Parcel).filter(Parcel.user_id == current_user.id).all()

@router.get("/sensors/{sensor_id}/data", response_model=List[SensorDataOut])
def get_sensor_readings(
    sensor_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

    if current_user.role != "admin" and sensor.parcel.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este sensor")

    readings = (
        db.query(SensorData)
        .filter(SensorData.sensor_id == sensor_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(readings))


@router.get("/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parcels = (
        db.query(Parcel).all()
        if current_user.role == "admin"
        else db.query(Parcel).filter(Parcel.user_id == current_user.id).all()
    )

    result = {"fincas": [], "sistema": {}}

    for parcel in parcels:
        is_system = parcel.name.upper() in ("SISTEMA", "EXTERIOR")
        sensors_payload = {}

        for sensor in parcel.sensors:
            # Últimas 15 lecturas para tendencia y valor actual
            readings = (
                db.query(SensorData)
                .filter(SensorData.sensor_id == sensor.id)
                .order_by(SensorData.timestamp.desc())
                .limit(15)
                .all()
            )
            readings = list(reversed(readings))
            latest_val = readings[-1].value if readings else 0.0

            sensors_payload[sensor.type] = {
                "id": sensor.id,
                "type": sensor.type,
                "unit": sensor.unit,
                "description": sensor.description,
                "threshold_low": sensor.threshold_low,
                "threshold_high": sensor.threshold_high,
                "value": latest_val,
                "history": [
                    {"time": r.timestamp[11:19] if len(r.timestamp) >= 19 else r.timestamp, "value": r.value}
                    for r in readings
                ],
            }

        if is_system:
            result["sistema"] = sensors_payload
        else:
            result["fincas"].append({
                "id": parcel.id,
                "name": parcel.name,
                "location": parcel.location,
                "sensors": sensors_payload,
            })

    return result