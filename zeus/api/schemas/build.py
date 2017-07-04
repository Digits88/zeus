from marshmallow import Schema, fields


class BuildSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    started_at = fields.DateTime(attribute="date_started")
    finished_at = fields.DateTime(attribute="date_finished")
    status = fields.Str()
    result = fields.Str()