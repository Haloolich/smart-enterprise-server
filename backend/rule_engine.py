
import logging

from sqlalchemy.orm import Session

from backend.database.models import (
    AutomationRule,
    AutomationEvent
)


logger = logging.getLogger(__name__)


# Перевірка умови правила
def check_condition(value, operator, threshold):

    if operator == "greater_than":
        return value > threshold

    elif operator == "less_than":
        return value < threshold

    elif operator == "equal":
        return value == threshold

    elif operator == "greater_equal":
        return value >= threshold

    elif operator == "less_equal":
        return value <= threshold

    return False


# Перевірка всіх правил для отриманого показника
def evaluate_rules(db: Session, sensor_type: str, value: float):

    rules = db.query(AutomationRule).filter(
        AutomationRule.sensor_type == sensor_type,
        AutomationRule.enabled == True
    ).all()

    triggered_rules = []

    for rule in rules:

        if check_condition(
            value,
            rule.operator,
            rule.threshold
        ):

            event = AutomationEvent(
                rule_id=rule.id,
                sensor_type=sensor_type,
                value=value,
                action=rule.action,
                message=(
                    f"Спрацювало правило '{rule.name}'. "
                    f"Отримано {value}, "
                    f"порогове значення {rule.threshold}."
                )
            )

            db.add(event)

            triggered_rules.append(rule.name)

            logger.warning(
                f"СПРАЦЮВАЛО ПРАВИЛО: {rule.name}"
            )

    return triggered_rules
