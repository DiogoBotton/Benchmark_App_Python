from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base, engine

class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)

    results = relationship('BenchmarkResult', back_populates='benchmark', cascade="all, delete")

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    id = Column(Integer, primary_key=True, index=True)
    request_name = Column(String, index=True)
    benchmark_id = Column(Integer, ForeignKey('benchmarks.id'), nullable=False)

    benchmark = relationship('Benchmark', back_populates='results')
    times = relationship('BenchmarkTime', back_populates='benchmark_result', cascade="all, delete")

class BenchmarkTime(Base):
    __tablename__ = "benchmark_times"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(Integer)
    benchmark_result_id = Column(Integer, ForeignKey('benchmark_results.id'), nullable=False)

    benchmark_result = relationship('BenchmarkResult', back_populates='times')

def init_db():
    Base.metadata.create_all(bind=engine)