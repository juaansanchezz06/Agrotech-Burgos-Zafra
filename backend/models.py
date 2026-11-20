from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="cliente")

    # Relación: Un usuario tiene muchas parcelas
    parcels = relationship("Parcel", back_populates="owner")

class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    user_id = Column(Integer, ForeignKey("users.id")) # Enlace al dueño

    owner = relationship("User", back_populates="parcels")
    sensors = relationship("Sensor", back_populates="parcel")

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, index=True) # ej. "t001"
    parcel_id = Column(Integer, ForeignKey("parcels.id"))
    type = Column(String) # temperatura_aire, humedad_suelo...
    unit = Column(String)
    description = Column(String)
    threshold_low = Column(Float, nullable=True)
    threshold_high = Column(Float, nullable=True)

    parcel = relationship("Parcel", back_populates="sensors")
    data = relationship("SensorData", back_populates="sensor")

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    timestamp = Column(String) # ISO 8601 ej: "2026-11-11T10:00:00Z"
    value = Column(Float)

    sensor = relationship("Sensor", back_populates="data")