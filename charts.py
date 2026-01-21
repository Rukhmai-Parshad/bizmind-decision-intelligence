import os
import seaborn as sns
import matplotlib.pyplot as plt

from django.conf import settings
from django.db import models
from decisions.models import Decision


def _save_chart(fig, filename):
    charts_dir = os.path.join(settings.MEDIA_ROOT, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    path = os.path.join(charts_dir, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

    return f"charts/{filename}"


# ============================
# 1. CONFIDENCE DISTRIBUTION
# ============================
def confidence_distribution_chart(user):
    qs = Decision.objects.filter(dataset__uploaded_by=user)

    confidences = list(qs.values_list("confidence", flat=True))
    if not confidences:
        return None

    fig = plt.figure(figsize=(6, 4))
    sns.histplot(confidences, bins=10, kde=True)
    plt.title("Decision Confidence Distribution")
    plt.xlabel("Confidence")
    plt.ylabel("Count")

    return _save_chart(fig, f"confidence_{user.id}.png")



# ============================
# 2. DECISIONS PER DATASET
# ============================
def decisions_per_dataset_chart(user):
    qs = (
        Decision.objects
        .filter(dataset__uploaded_by=user)
        .values("dataset__name")
        .annotate(count=models.Count("id"))
    )

    if not qs.exists():
        return None

    names = [x["dataset__name"] for x in qs]
    counts = [x["count"] for x in qs]

    fig = plt.figure(figsize=(7, 4))
    sns.barplot(x=names, y=counts)
    plt.title("Decisions per Dataset")
    plt.ylabel("Decisions")
    plt.xticks(rotation=30)

    return _save_chart(fig, "dataset_{user.id}.png")


# ============================
# 3. DOMAIN-WISE DECISIONS
# ============================
def domain_wise_decisions_chart(user):
    qs = (
        Decision.objects
        .filter(dataset__uploaded_by=user)
        .values("domain")
        .annotate(count=models.Count("id"))
    )

    if not qs.exists():
        return None

    domains = [x["domain"] for x in qs]
    counts = [x["count"] for x in qs]

    fig = plt.figure(figsize=(6, 4))
    sns.barplot(x=domains, y=counts)
    plt.title("Domain-wise Decisions")
    plt.ylabel("Count")

    return _save_chart(fig, f"domain_{user.id}.png")

