"""DB 초기화 스크립트 - TimescaleDB 확장 활성화 및 테이블 생성"""

from __future__ import annotations

import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    import psycopg2
    from sqlalchemy.ext.asyncio import create_async_engine

    from hdesk.data.database import Base, init_db
    from hdesk.utils.config import get_settings

    settings = get_settings()
    logger.info("DB 초기화 시작: %s", settings.database_url_sync.split("@")[1])

    # TimescaleDB 확장 확인
    try:
        conn = psycopg2.connect(settings.database_url_sync)
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("TimescaleDB 확장 활성화 완료")
    except Exception as e:
        logger.error("TimescaleDB 확장 실패: %s", e)
        sys.exit(1)

    # SQLAlchemy 관리 테이블 생성
    await init_db()
    logger.info("SQLAlchemy 테이블 생성 완료")

    # 하이퍼테이블 DDL (init.sql과 동일)
    ddl = """
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
    """

    try:
        conn = psycopg2.connect(settings.database_url_sync)
        cursor = conn.cursor()
        cursor.execute(ddl)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("하이퍼테이블 생성 완료")
    except Exception as e:
        logger.warning("하이퍼테이블 DDL 실행 중 오류 (이미 존재할 수 있음): %s", e)

    logger.info("DB 초기화 완료")


if __name__ == "__main__":
    asyncio.run(main())
