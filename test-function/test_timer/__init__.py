import azure.functions as func
import logging
from datetime import datetime


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().isoformat()

    if mytimer.past_due:
        logging.info('Timer function is past due!')

    logging.info('🚀 Test timer function executada em: %s', utc_timestamp)
    logging.info('✅ Function está funcionando perfeitamente!')