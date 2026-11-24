
import logging

from sqlalchemy.orm import Session

from backend.database.models import (
    AutomationRule,
    AutomationEvent,
    SystemSettings
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


# Перевірка правил автоматизації
def evaluate_rules(
    db: Session,
    sensor_type: str,
    value: float
):
    settings = db.query(SystemSettings).filter(
        SystemSettings.id == 1
    ).first()

    # У ручному режимі автоматизація вимкнена
    if settings and settings.control_mode == "manual":
        return []

    rules = db.query(AutomationRule).filter(
        AutomationRule.sensor_type == sensor_type,
        AutomationRule.enabled == True
    ).all()

    triggered_rules = []

    for rule in rules:

        # Перевіряємо поточну умову
        condition_met = check_condition(
            value,
            rule.operator,
            rule.threshold
        )

        # Перевіряємо попередній стан умови
        previous_state = rule.last_condition_state

        # Реагуємо тільки на перехід False -> True
        if condition_met and not previous_state:

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

            triggered_rules.append({
                "id": rule.id,
                "name": rule.name,
                "action": rule.action
            })

            logger.warning(
                f"СПРАЦЮВАЛО ПРАВИЛО: {rule.name}"
            )

        # Запам'ятовуємо поточний стан умови
        rule.last_condition_state = condition_met

    return triggered_rules
