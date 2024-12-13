import logging
import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import jsonify
from sqlalchemy import and_, text
from random import randint
import psycopg2

from config import app, db


port_number = int(os.environ.get("APP_PORT", 5153))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Database connection setup
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD')
        )
        logger.info("Successfully connected to database")
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise


@app.route("/health_check")
def health_check():
    return "ok"


@app.route("/readiness_check")
def readiness_check():
    try:
        count = db.session.execute(text("SELECT COUNT(*) FROM tokens")).scalar()
    except Exception as e:
        app.logger.error(e)
        return "failed", 500
    else:
        return "ok"


def get_daily_visits():
    with app.app_context():
        logger.info("=== Starting periodic database check ===")
        try:
            result = db.session.execute(text("""
            SELECT Date(created_at) AS date,
                Count(*)         AS visits
            FROM   tokens
            WHERE  used_at IS NOT NULL
            GROUP  BY Date(created_at)
            """))

            response = {}
            for row in result:
                response[str(row[0])] = row[1]

            logger.info(f"Database query results: {response}")
            logger.info("=== Completed periodic database check ===")
            return response
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise


@app.route("/api/reports/daily_usage", methods=["GET"])
def daily_visits():
    return jsonify(get_daily_visits())


@app.route("/api/reports/user_visits", methods=["GET"])
def all_user_visits():
    logger.info("Executing user visits query...")
    try:
        result = db.session.execute(text("""
        SELECT t.user_id,
            t.visits,
            users.joined_at
        FROM   (SELECT tokens.user_id,
                    Count(*) AS visits
                FROM   tokens
                GROUP  BY user_id) AS t
            LEFT JOIN users
                    ON t.user_id = users.id;
        """))

        response = {}
        for row in result:
            response[row[0]] = {
                "visits": row[1],
                "joined_at": str(row[2])
            }
        
        logger.info(f"User visits query result: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting user visits: {str(e)}")
        raise


scheduler = BackgroundScheduler()
job = scheduler.add_job(get_daily_visits, 'interval', seconds=10)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_number)
