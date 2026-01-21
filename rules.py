# sales/rules.py

from sales.queries import total_revenue, worst_region, top_product
from decisions.confidence import clamp, linear_confidence
from decisions.models import Decision
from decisions.utils import DOMAIN_IMPACT, generate_insight_and_action


def revenue_health_check(dataset, threshold=10000):
    revenue = total_revenue(dataset)
    if revenue >= threshold:
        return

    confidence = linear_confidence(threshold - revenue, threshold)
    insight, action = generate_insight_and_action("sales", confidence)

    Decision.objects.update_or_create(
        dataset=dataset,
        rule_name="SALES_REVENUE_HEALTH",
        defaults={
            'domain': 'sales',
            'title': "Revenue Risk Detected",
            'recommendation': "Improve pricing and focus on high-margin products.",
            'explanation': f"Revenue {revenue} below threshold {threshold}.",
            'impact': DOMAIN_IMPACT["sales"],
            'confidence': confidence,
            'insight': insight,
            'action': action,
        }
    )


def region_focus_rule(dataset):
    region = worst_region(dataset)
    total = total_revenue(dataset)
    if not region or total == 0:
        return

    ratio = region['total_revenue'] / total
    confidence = clamp(1 - ratio)
    insight, action = generate_insight_and_action("sales", confidence)

    Decision.objects.update_or_create(
        dataset=dataset,
        rule_name="SALES_REGION_FOCUS",
        defaults={
            'domain': 'sales',
            'title': "Underperforming Sales Region",
            'recommendation': f"Improve performance in {region['region']}.",
            'explanation': f"{round(ratio*100,2)}% revenue contribution.",
            'impact': DOMAIN_IMPACT["sales"],
            'confidence': confidence,
            'insight': insight,
            'action': action,
        }
    )


def top_product_rule(dataset):
    product = top_product(dataset)
    total = total_revenue(dataset)
    if not product or total == 0:
        return

    dominance = product['total_revenue'] / total
    confidence = clamp(dominance)
    insight, action = generate_insight_and_action("sales", confidence)

    Decision.objects.update_or_create(
        dataset=dataset,
        rule_name="SALES_TOP_PRODUCT",
        defaults={
            'domain': 'sales',
            'title': "Top Performing Product",
            'recommendation': f"Scale sales of {product['product']}.",
            'explanation': f"{round(dominance*100,2)}% revenue contribution.",
            'impact': DOMAIN_IMPACT["sales"],
            'confidence': confidence,
            'insight': insight,
            'action': action,
        }
    )
