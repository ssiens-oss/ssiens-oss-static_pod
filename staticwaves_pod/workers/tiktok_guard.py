def normalize_variant(v):
    v["inventory_policy"] = "deny"
    v["inventory_management"] = "shopify"
    return v
