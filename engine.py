# decisions/engine.py

from django.db import transaction
from datasets.models import Dataset

# SALES RULES
from sales.rules import (
    revenue_health_check,
    region_focus_rule,
    top_product_rule,
)

# MARKETING RULES
from marketing.rules import (
    low_ctr_rule,
    poor_roas_rule,
    worst_channel_rule,
)

# FINANCE RULES
from finance.rules import (
    net_loss_rule,
    expense_exceeds_income_rule,
    top_expense_category_rule,
)


def generate_decisions(dataset):
    """
    Central, idempotent decision engine.
    Safe to call multiple times.
    """

    with transaction.atomic():
        locked_dataset = (
            Dataset.objects
            .select_for_update()
            .get(pk=dataset.pk)
        )

        # Prevent duplicate execution
        if locked_dataset.decisions_generated:
            return

        # Route rules by dataset type
        if locked_dataset.type == "sales":
            rules = (
                revenue_health_check,
                region_focus_rule,
                top_product_rule,
            )

        elif locked_dataset.type == "marketing":
            rules = (
                low_ctr_rule,
                poor_roas_rule,
                worst_channel_rule,
            )

        elif locked_dataset.type == "finance":
            rules = (
                net_loss_rule,
                expense_exceeds_income_rule,
                top_expense_category_rule,
            )

        else:
            return

        # Execute rules
        for rule in rules:
            rule(locked_dataset)

        # Mark dataset as processed
        locked_dataset.decisions_generated = True
        locked_dataset.save(update_fields=["decisions_generated"])
