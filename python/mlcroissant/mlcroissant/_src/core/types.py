"""Python types for ML Croissant."""

JsonScalar = str | int | float | bool | None
JsonArray = list["JsonValue"]
JsonObject = dict[str, "JsonValue"]
JsonValue = JsonScalar | JsonArray | JsonObject
# Keep `Json` around for call sites that expect a JSON object (mapping).
Json = JsonObject
