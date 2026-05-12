-- TimescaleDB 확장 활성화
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- market_data 하이퍼테이블
CREATE TABLE IF NOT EXISTS market_data (
    timestamp   TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(30) NOT NULL,
    price       DOUBLE PRECISION,
    bid         DOUBLE PRECISION,
    ask         DOUBLE PRECISION,
    volume      BIGINT,
    PRIMARY KEY (timestamp, symbol)
);
SELECT create_hypertable('market_data', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data (symbol, timestamp DESC);

-- greeks_snapshots 하이퍼테이블
CREATE TABLE IF NOT EXISTS greeks_snapshots (
    timestamp    TIMESTAMPTZ NOT NULL,
    position_id  INTEGER NOT NULL,
    delta        DOUBLE PRECISION,
    gamma        DOUBLE PRECISION,
    vega         DOUBLE PRECISION,
    theta        DOUBLE PRECISION,
    rho          DOUBLE PRECISION,
    option_price DOUBLE PRECISION,
    implied_vol  DOUBLE PRECISION,
    PRIMARY KEY (timestamp, position_id)
);
SELECT create_hypertable('greeks_snapshots', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_greeks_position ON greeks_snapshots (position_id, timestamp DESC);

-- 압축 정책: 7일 이상 데이터 자동 압축
SELECT add_compression_policy('market_data', INTERVAL '7 days');
SELECT add_compression_policy('greeks_snapshots', INTERVAL '7 days');

-- 데이터 보존 정책: 2년 초과 데이터 자동 삭제
SELECT add_retention_policy('market_data', INTERVAL '2 years');
SELECT add_retention_policy('greeks_snapshots', INTERVAL '2 years');
